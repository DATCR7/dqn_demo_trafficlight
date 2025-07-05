import os
import sys
import subprocess
# Thêm đường dẫn tới thư mục 'tools' của SUMO
sys.path.append(r'D:\SUMO_CaiDat\tools')
import configparser
from sumolib import checkBinary

# Đọc file .ini và lấy thông tin
def import_train_configuration(config_file):
    content = configparser.ConfigParser()
    files_read = content.read(config_file)
    if not files_read:
        sys.exit(f"Config file {config_file} not found or empty!")
    if 'dir' not in content:
        sys.exit("Section [dir] not found in config file!")
    config = {}
    config['models_path_name'] = content['dir']['models_path_name']
    config['sumocfg_file_name'] = content['dir']['sumocfg_file_name']
    return config

# Xác nhận biến môi trường đã được thiết lập chưa
def set_sumo(gui, sumocfg_file_name, max_steps):
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    # Xem coi gui có hoạt động hay không
    if gui == False:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
 
    sumo_cfg_path = sumocfg_file_name
    sumo_cmd = [
        sumoBinary,
        "-c", sumo_cfg_path,
        # "--no-step-log", "true",
        "--start",
        "--quit-on-end"
        # Bạn cũng có thể bỏ "--waiting-time-memory" nếu không cần thiết
    ]
    return sumo_cmd

# Tạo mục chứa model mới
def set_train_path(models_path_name):
    base_dir = r"D:\SUMO_CaiDat\StageLight-main\StageLight-main"
    models_path = os.path.join(base_dir, models_path_name)
    # Tạo thư mục nếu chưa có
    os.makedirs(models_path, exist_ok=True)
    # Kiểm tra thư mục đã chắc chắn tồn tại
    dir_content = os.listdir(models_path) 
    previous_versions = []
    if dir_content:
        previous_versions = [int(name.split("_")[1]) for name in dir_content]
        new_version = str(max(previous_versions) + 1)
    else:
        new_version = '1'

    data_path = os.path.join(models_path, 'model_' + new_version)
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    return data_path 

# Lấy đường dẫn đến Model đã huấn luyện
def get_model_path(models_path_name, model_n):
    base_dir = r"D:\SUMO_CaiDat\StageLight-main\StageLight-main"
    model_folder_path = os.path.join(base_dir, models_path_name, f"model_{model_n}")
    return model_folder_path

# Tạo thư mục test có trong modle_n
def set_test_path(models_path_name, model_n):
    base_dir = r"D:\SUMO_CaiDat\StageLight-main\StageLight-main"
    model_folder_path = os.path.join(base_dir, models_path_name, f"model_{model_n}")

    if os.path.isdir(model_folder_path):
        plot_path = os.path.join(model_folder_path, 'test')
        os.makedirs(plot_path, exist_ok=True)
        return model_folder_path, plot_path
    else:
        sys.exit(f"The model number {model_n} specified does not exist in the models folder")
