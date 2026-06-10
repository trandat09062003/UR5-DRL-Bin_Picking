#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_one_grasp_gui.py

Phiên bản tự động hóa hoàn toàn:
- Khởi động scene CoppeliaSim.
- Đợi Scene load bằng ZMQ API check.
- Khởi tạo Robot.
- Thực hiện grasp tại vị trí thực tế của vật thể.
- Nếu gắp trượt (failed), tự động reset simulation và spawn/xếp lại đồ vật từ đầu để gắp lại.
- Lặp lại cho tới khi gắp thành công.
- Sau khi thành công, đợi 10 giây để hiển thị kết quả và tự động đóng simulator, kết thúc chương trình.
"""

import os
import sys
import subprocess
import time
import socket
import signal
import numpy as np

# 1. Đảm bảo biến DISPLAY (cần cho GUI)
if not os.getenv("DISPLAY"):
    os.environ["DISPLAY"] = ":0"
    print("[INFO] Đặt DISPLAY=:0 để bật GUI")

def terminate_process_group(proc):
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            pass

# 2. Hàm khởi động CoppeliaSim
def launch_coppelia_sim(gui=True, scene_path=None):
    coppelia_path = "/home/aics/Màn hình nền/Rl_Bin_Picing/CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04/coppeliaSim.sh"
    if scene_path is None:
        scene_path = "simulation/simulation.ttt"
    args = [coppelia_path, "-xnone"]
    if not gui:
        args.append("-h")
    args.extend(["-f", scene_path])
    env = os.environ.copy()
    for k in list(env.keys()):
        if k.startswith("QT_"):
            env.pop(k)
    log_file = open("coppelia_subprocess.log", "w")
    proc = subprocess.Popen(args, stdout=log_file, stderr=subprocess.STDOUT, env=env, preexec_fn=os.setsid)
    print(f"[INFO] Đang khởi động CoppeliaSim (GUI={gui}) … PID={proc.pid}")
    return proc

# 4. Thực hiện một grasp
def perform_one_grasp(robot):
    ws = robot.workspace_limits
    
    # Lấy vị trí thực tế của các vật thể từ simulator để thực hiện gắp chính xác
    obj_positions = robot.get_obj_positions()
    target_pos = None
    
    # Tìm vật thể nằm trong phạm vi làm việc (workspace)
    for pos in obj_positions:
        if (ws[0][0] + 0.05 <= pos[0] <= ws[0][1] - 0.05) and (ws[1][0] + 0.05 <= pos[1] <= ws[1][1] - 0.05):
            target_pos = pos
            break
            
    if target_pos is not None:
        print(f"[INFO] Tìm thấy vật thể thực tế tại: X={target_pos[0]:.3f}, Y={target_pos[1]:.3f}, Z={target_pos[2]:.3f}")
        position = np.array([target_pos[0], target_pos[1], target_pos[2]])
    else:
        # Nếu không tìm thấy, fallback về ngẫu nhiên
        rand_x = np.random.uniform(ws[0][0] + 0.1, ws[0][1] - 0.1)
        rand_y = np.random.uniform(ws[1][0] + 0.1, ws[1][1] - 0.1)
        position = np.array([rand_x, rand_y, 0.0])
        print(f"[WARNING] Không tìm thấy vật thể nào trong workspace. Gắp ngẫu nhiên tại ({rand_x:.3f}, {rand_y:.3f})")
        
    heightmap_angle = np.random.uniform(0, 2 * np.pi)
    print(f"[INFO] Thực hiện grasp tại ({position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}) – góc {heightmap_angle:.2f}")
    success = robot.grasp(position, heightmap_angle, ws)
    if success:
        print("[RESULT] Grasp thành công!")
    else:
        print("[RESULT] Grasp thất bại.")
    return success

def is_port_open(port, host="127.0.0.1"):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            s.connect((host, port))
            return True
    except Exception:
        return False

def wait_for_scene_load(timeout=30):
    """
    Sử dụng ZeroMQ Remote API để phát hiện chính xác khi nào Scene đã được load hoàn chỉnh.
    """
    print("[INFO] Đang đợi cổng ZMQ Remote API (23000) mở...")
    port_opened = False
    for _ in range(15):
        if is_port_open(23000):
            port_opened = True
            break
        time.sleep(1)
        
    if not port_opened:
        print("[WARNING] Cổng ZMQ (23000) không phản hồi.")
        return False

    print("[INFO] Cổng ZMQ (23000) đã mở. Đang chờ Scene tải xong hoàn toàn...")
    try:
        from coppeliasim_zmqremoteapi_client import RemoteAPIClient
        client = RemoteAPIClient()
        sim = client.require('sim')
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Query đối tượng UR5 để xác nhận scene đã load xong
                sim.getObject('/UR5')
                print("[INFO] Scene đã tải xong hoàn toàn (phát hiện thấy UR5)!")
                return True
            except Exception:
                time.sleep(0.5)
    except Exception as e:
        print(f"[WARNING] Lỗi khi truy vấn qua ZMQ API: {e}")
    return False

# 5. Main
def main():
    original_scene = "simulation/simulation.ttt"
    max_attempts = 3
    success = False
    sim_process = None

    for attempt in range(1, max_attempts + 1):
        print(f"\n[INFO] ----- LẦN THỬ KẾT NỐI {attempt}/{max_attempts} -----")
        sim_process = launch_coppelia_sim(gui=True, scene_path=original_scene)

        # Kiểm tra nhanh xem tiến trình có chết ngay không
        time.sleep(3)
        if sim_process.poll() is not None:
            print("[ERROR] CoppeliaSim đã thoát ngay lập tức.")
            continue

        # Chờ scene load hoàn chỉnh qua ZMQ check
        if not wait_for_scene_load(timeout=30):
            print("[WARNING] Không thể tải scene đúng hạn. Tiến hành tắt và chạy lại...")
            terminate_process_group(sim_process)
            time.sleep(2)
            continue

        print("[INFO] Khởi tạo Robot và chạy kịch bản gắp vật...")

        # Thiết lập cơ chế timeout 120 giây (dành cho việc chạy nhiều lần gắp gộp lại)
        def timeout_handler(signum, frame):
            raise TimeoutError("Quá thời gian thực thi tổng thể (120s).")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(120)

        try:
            from robot import Robot
            robot = Robot(
                is_sim=True,
                obj_mesh_dir="objects/blocks",
                num_obj=10,
                workspace_limits=[[-0.724, -0.276], [-0.224, 0.224], [-0.0001, 0.4]],
                tcp_host_ip="127.0.0.1",
                tcp_port=19997,
                rtc_host_ip="127.0.0.1",
                rtc_port=23000,
                is_testing=False,
                test_preset_cases=False,
                test_preset_file="",
            )
            
            # Vòng lặp gắp vật cho tới khi thành công
            grasp_attempt = 1
            while True:
                print(f"\n[INFO] === THỰC HIỆN GRASP LẦN THỨ {grasp_attempt} ===")
                grasp_success = perform_one_grasp(robot)
                if grasp_success:
                    print(f"[SUCCESS] Gắp thành công ở lần thử thứ {grasp_attempt}!")
                    success = True
                    break
                else:
                    print(f"[WARNING] Gắp trượt ở lần thử thứ {grasp_attempt}. Tiến hành reset simulation và đặt lại đồ vật từ đầu...")
                    robot.restart_sim()
                    robot.add_objects()
                    grasp_attempt += 1
                    time.sleep(1)

            signal.alarm(0)  # Tắt alarm khi thành công
            break

        except Exception as e:
            signal.alarm(0)  # Tắt alarm khi lỗi
            print(f"[ERROR] Lỗi thực thi trong lần thử {attempt}: {e}")
            terminate_process_group(sim_process)
            time.sleep(2)
            continue

    if success:
        print("\n[SUCCESS] Kịch bản gắp đã hoàn thành và thành công!")
        print("[INFO] Đang hiển thị kết quả trong 10 giây trước khi tự động đóng chương trình...")
        time.sleep(10)
    else:
        print("\n[FAILURE] Không thể hoàn thành gắp thành công sau các lần thử kết nối.")

    if sim_process is not None:
        print("[INFO] Đang đóng CoppeliaSim...")
        terminate_process_group(sim_process)
        print("[INFO] CoppeliaSim đã dừng. Kết thúc chương trình.")

if __name__ == "__main__":
    main()
