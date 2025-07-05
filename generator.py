import numpy as np
import math

class TrafficGenerator:
    def __init__(self, max_steps, n_cars_generated):
        self._n_cars_generated = n_cars_generated
        self._max_steps = max_steps

    def generate_routefile(self, seed):
        np.random.seed(seed)

        timings = np.random.weibull(2, self._n_cars_generated)
        timings = np.sort(timings)

        car_gen_steps = []
        min_old = math.floor(timings[1])
        max_old = math.ceil(timings[-1])
        min_new = 0
        max_new = self._max_steps
        for value in timings:
            car_gen_steps = np.append(car_gen_steps, ((max_new - min_new) / (max_old - min_old)) * (value - max_old) + max_new)

        car_gen_steps = np.rint(car_gen_steps)

        file_path = "D:\\SUMO_CaiDat\\StageLight-main\\StageLight-main\\episode_routes.rou.xml"

        with open(file_path, "w") as routes:
            print("""<routes>
            <vType accel="2.5" decel="4.5" id="car" length="4.5" minGap="2.5" maxSpeed="25" sigma="0.5" guiShape="passenger"/>
            <vType accel="3.0" decel="5.0" id="motorbike" length="2.0" minGap="1.5" maxSpeed="18" sigma="0.3" guiShape="motorcycle"/>
            <vType accel="1.0" decel="2.0" id="bicycle" length="1.8" minGap="1.0" maxSpeed="6" sigma="0.2" guiShape="bicycle"/>

            <route id="W_N" edges="W2TL TL2N"/>
            <route id="W_E" edges="W2TL TL2E"/>
            <route id="W_S" edges="W2TL TL2S"/>
            <route id="N_W" edges="N2TL TL2W"/>
            <route id="N_E" edges="N2TL TL2E"/>
            <route id="N_S" edges="N2TL TL2S"/>
            <route id="E_W" edges="E2TL TL2W"/>
            <route id="E_N" edges="E2TL TL2N"/>
            <route id="E_S" edges="E2TL TL2S"/>
            <route id="S_W" edges="S2TL TL2W"/>
            <route id="S_N" edges="S2TL TL2N"/>
            <route id="S_E" edges="S2TL TL2E"/>""", file=routes)

            # Quy tắc làn theo loại xe và số làn trên edge đầu tiên
            lanes_4lanes = {
                'car': [1, 2, 3],
                'motorbike': [0, 1],
                'bicycle': [0]
            }
            lanes_3lanes = {
                'car': [1, 2],
                'motorbike': [0, 1],
                'bicycle': [0]
            }

            # Các tuyến đường theo nhóm số làn
            routes_4lanes_prefix = ['W', 'E']
            routes_3lanes_prefix = ['N', 'S']

            for car_counter, step in enumerate(car_gen_steps):
                vehicle_type = np.random.choice(['car', 'motorbike', 'bicycle'])

                # Xác định đi thẳng hay quành (75% thẳng, 25% quành)
                straight_or_turn = np.random.uniform()

                # Chọn tuyến dựa vào đi thẳng/quành
                if straight_or_turn < 0.75:
                    # Đi thẳng (chọn random trong 4 tuyến thẳng)
                    route_straight = np.random.randint(1, 5)
                    if route_straight == 1:
                        route = "W_E"
                    elif route_straight == 2:
                        route = "E_W"
                    elif route_straight == 3:
                        route = "N_S"
                    else:
                        route = "S_N"
                else:
                    # Quành (chọn random trong 8 tuyến quành)
                    route_turn = np.random.randint(1, 9)
                    route_map = {
                        1: "W_N",
                        2: "W_S",
                        3: "N_W",
                        4: "N_E",
                        5: "E_N",
                        6: "E_S",
                        7: "S_W",
                        8: "S_E"
                    }
                    route = route_map[route_turn]

                # Xác định prefix edge đầu tiên
                prefix = route[0]

                # Lấy danh sách làn phù hợp
                if prefix[0] in routes_4lanes_prefix:
                    lane_set = lanes_4lanes[vehicle_type]
                elif prefix[0] in routes_3lanes_prefix:
                    lane_set = lanes_3lanes[vehicle_type]
                else:
                    lane_set = lanes_3lanes[vehicle_type]  # mặc định

                lane = str(np.random.choice(lane_set))

                print(f'    <vehicle id="{route}_{car_counter}" type="{vehicle_type}" route="{route}" depart="{step}" departLane="{lane}" departSpeed="10" />', file=routes)

            print("</routes>", file=routes)

# if __name__ == "__main__":
#     generator = TrafficGenerator(max_steps=10000, n_cars_generated=2000)
#     generator.generate_routefile(seed=42)
