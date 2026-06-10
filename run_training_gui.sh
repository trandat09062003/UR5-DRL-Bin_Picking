#!/bin/bash
echo "[INFO] Đang khởi động CoppeliaSim (GUI)..."
"/home/aics/Màn hình nền/Rl_Bin_Picing/CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04/coppeliaSim.sh" -f simulation/simulation.ttt > coppelia.log 2>&1 &
SIM_PID=$!

echo "[INFO] Chờ 5 giây cho Simulator khởi động và mở cổng 19997..."
sleep 5

echo "[INFO] Đang chạy main.py..."
/home/aics/miniconda3/envs/vpg/bin/python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations

echo "[INFO] Đang đóng Simulator..."
kill -9 $SIM_PID
