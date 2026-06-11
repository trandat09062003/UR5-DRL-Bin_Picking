#!/bin/bash
echo "[INFO] Đang khởi động CoppeliaSim (GUI)..."
"/home/aics/Màn hình nền/Rl_Bin_Picing/CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04/coppeliaSim.sh" -f simulation/simulation.ttt > coppelia.log 2>&1 &
SIM_PID=$!

echo "[INFO] Chờ 15 giây cho Simulator tải xong hoàn toàn môi trường (Scene)..."
sleep 15

# ==== LOGIC TỰ ĐỘNG HỌC TIẾP (AUTO-RESUME) ====
LATEST_LOG=$(ls -td logs/*/ 2>/dev/null | head -1)
CMD="/home/aics/miniconda3/envs/vpg/bin/python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations"

if [ ! -z "$LATEST_LOG" ]; then
    SNAPSHOT_FILE="${LATEST_LOG}models/snapshot-backup.reinforcement.pth"
    if [ -f "$SNAPSHOT_FILE" ]; then
        echo "[INFO] Tìm thấy bản lưu cũ tại $SNAPSHOT_FILE. Đang tiến hành học tiếp (Resume)..."
        # Bỏ đi dấu / ở cuối đường dẫn LATEST_LOG
        LOG_DIR="${LATEST_LOG%/}"
        CMD="$CMD --load_snapshot --snapshot_file \"$SNAPSHOT_FILE\" --continue_logging --logging_directory \"$LOG_DIR\""
    else
        echo "[INFO] Không tìm thấy file não (snapshot). Bắt đầu học từ đầu..."
    fi
else
    echo "[INFO] Chưa có dữ liệu học cũ. Bắt đầu học từ đầu..."
fi

echo "[INFO] Đang chạy lệnh: $CMD"
eval $CMD

echo "[INFO] Đang đóng Simulator..."
kill -9 $SIM_PID
