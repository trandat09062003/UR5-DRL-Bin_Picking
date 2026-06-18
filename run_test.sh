#!/bin/bash
# Script để TEST mô hình sau khi train
# Bạn có thể thay đổi ID bên dưới để chọn test vật thể cụ thể (0-7), hoặc để -1 để test ngẫu nhiên
SPECIFIC_OBJ_ID=-1
MAX_TEST_TRIALS=30

echo "[INFO] Đang chạy chế độ TEST MODEL (Đánh giá) - Vật thể ID: $SPECIFIC_OBJ_ID..."

echo "[INFO] Dọn dẹp các tiến trình kẹt ngầm..."
pkill -9 -f -i coppelia
fuser -k -n tcp 19997 2>/dev/null
sleep 2

echo "[INFO] Đang khởi động CoppeliaSim (Tự động mở cửa sổ 3D)..."
nohup "/home/aics/Màn hình nền/Rl_Bin_Picing/CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04/coppeliaSim.sh" -f simulation/simulation.ttt < /dev/null > coppelia_test.log 2>&1 &
SIM_PID=$!

echo "[INFO] Chờ 15 giây cho Simulator tải xong..."
sleep 15

# Tìm thư mục log mới nhất chứa model đã train
LATEST_LOG=$(ls -td logs/*/ 2>/dev/null | head -1)

if [ ! -z "$LATEST_LOG" ]; then
    SNAPSHOT_FILE="${LATEST_LOG}models/snapshot-backup.reinforcement.pth"
    if [ -f "$SNAPSHOT_FILE" ]; then
        echo "[INFO] Tìm thấy Model đã train tại $SNAPSHOT_FILE."
        
        # Test sẽ sinh ra 10 vật thể ngẫu nhiên trên bàn
        CMD="/home/aics/miniconda3/envs/vpg/bin/python main.py --is_sim --is_testing --load_snapshot --snapshot_file \"$SNAPSHOT_FILE\" --max_test_trials $MAX_TEST_TRIALS --num_obj 10 --specific_obj -1 --experience_replay --explore_rate_decay"
        
        echo "[INFO] Bắt đầu TEST $MAX_TEST_TRIALS lượt (Mỗi lượt dọn sạch 10 vật thể)..."
        echo "[INFO] Đang chạy lệnh: $CMD"
        eval $CMD
        
    else
        echo "[ERROR] Không tìm thấy file model (snapshot.pth) trong thư mục $LATEST_LOG"
    fi
else
    echo "[ERROR] Không tìm thấy thư mục logs/ nào chứa model đã train. Vui lòng train trước!"
fi

echo "[INFO] Đang đóng Simulator..."
kill -9 $SIM_PID
