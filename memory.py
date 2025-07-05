
import random
import numpy as np
# Bộ nhớ kinh nghiệm có ưu tiên (Prioritized Experience Replay)
# Thay vì lấy mẫu từ replay buffer một cách ngẫu nhiên (uniform), ta ưu tiên các trải nghiệm (samples) mà mô hình học chưa tốt (lỗi lớn) để học lại.

# Logic xử lý mẫu và ưu tiên
class Memory:  # stored as ( s, a, r, s_ ) in SumTree
    e = 0.01                                    # Ưu tiên tối thiểu
    a = 0.6                                     # Mức độ ưu tiên
    beta = 0.4                                  # Bù sai lệch. Giups giảm thiên lệch khi dùng lấy mấu có trọng số
    beta_increment_per_sampling = 0.001         # Tốc độ tăng của beta 

    def __init__(self, capacity, size_min):
        self.tree = SumTree(capacity)
        self.capacity = capacity
        self._size_min = size_min

    # Tính độ ưu tiên. Từ sai số TD (temporal-difference) 
    def _get_priority(self, error):
        return (np.abs(error) + self.e) ** self.a

    # Thêm một mẫu (s, a, r, s') vào SumTree
    def add_sample(self, error, sample):
        p = self._get_priority(error)
        self.tree.add(p, sample)

    # Lấy ra một batch có trọng số cao
    def get_samples(self, n):
        batch = []
        idxs = []
        segment = self.tree.total() / n         # Chia tổng ưu tiên (sum of all priorities) thành n đoạn bằng nhau.
        priorities = []
    
        self.beta = np.min([1., self.beta + self.beta_increment_per_sampling])      # beta tăng dần lên 1 để giảm sai lệch theo thời gian.
        # Vòng lặp lấy mẫu
        for i in range(n):
            a = segment * i
            b = segment * (i + 1)
    
            s = random.uniform(a, b)
            (idx, p, data) = self.tree.get(s)
            priorities.append(p)
            batch.append(data)
            idxs.append(idx)
        # Tính trọng số IS (Importance Sampling)
        sampling_probabilities = priorities / self.tree.total()
        is_weight = np.power(self.tree.n_entries * sampling_probabilities, -self.beta)
        is_weight /= is_weight.max()
    
        return batch, idxs, is_weight
        
    # Cập nhật lại độ ưu tiên của sample đã chọn, sau khi model học xong
    def update(self, idx, error):
        p = self._get_priority(error)
        self.tree.update(idx, p)


# SumTree
# Cấu trúc dữ liệu cây nhị phân giúp truy xuất theo mẫu theo xác suất ưu tiên
class SumTree:
    write = 0                   # Chỉ số trỏ đến vị trí cần ghi

    def __init__(self, capacity):
        self.capacity = capacity
        self.tree = np.zeros(2 * capacity - 1)
        self.data = np.zeros(capacity, dtype=object)
        self.n_entries = 0

    # update to the root node
    def _propagate(self, idx, change):
        parent = (idx - 1) // 2

        self.tree[parent] += change

        if parent != 0:
            self._propagate(parent, change)

    # Cây nhị phân lưu các priority sao cho tree[parent] = tree[left] + tree[right]
    def _retrieve(self, idx, s):
        left = 2 * idx + 1
        right = left + 1

        if left >= len(self.tree):
            return idx

        if s <= self.tree[left]:    # Đi về trái
            return self._retrieve(left, s)
        else:                       # Đi về phải
            return self._retrieve(right, s - self.tree[left])

    # Trả về tổng giá trị priority
    def total(self):
        return self.tree[0]

    # Thêm priority và samples
    def add(self, p, data):

        idx = self.write + self.capacity - 1        # Chỉ số trỏ đến vị trí tiếp theo cần ghi

        self.data[self.write] = data
        self.update(idx, p)

        self.write += 1
        if self.write >= self.capacity:
            self.write = 0

        if self.n_entries < self.capacity:
            self.n_entries += 1

    # Cập nhật lại priority
    def update(self, idx, p):
        change = p - self.tree[idx]

        self.tree[idx] = p
        self._propagate(idx, change)

    # Lấy ra priority and samples
    def get(self, s):
        idx = self._retrieve(0, s)
        dataIdx = idx - self.capacity + 1

        return (idx, self.tree[idx], self.data[dataIdx])
