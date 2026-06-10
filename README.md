# 🚀 Hướng Dẫn Chạy Mô Phỏng & Huấn Luyện UR5-VPG

Tài liệu này hướng dẫn chi tiết cách chạy demo mô phỏng và chạy huấn luyện học tăng cường (Deep Q-Learning) cho robot UR5 trong môi trường CoppeliaSim.

---

## ⚠️ LƯU Ý CỰC KỲ QUAN TRỌNG (ĐỌC TRƯỚC KHI CHẠY)

1. **Phải di chuyển vào thư mục dự án**: 
   Trước khi chạy bất kỳ câu lệnh nào, bạn **bắt buộc** phải mở terminal và di chuyển vào thư mục con `visual-pushing-grasping` bằng lệnh:
   ```bash
   cd "/home/aics/Màn hình nền/Rl_Bin_Picing/visual-pushing-grasping"
   ```
   *Nếu không chạy lệnh `cd` này, Python sẽ báo lỗi không tìm thấy các file script (`main.py`, `run_one_grasp_gui.py`,...).*

2. **Môi trường Python (Conda)**:
   Dự án sử dụng môi trường Conda có tên là `vpg` nằm tại `/home/aics/miniconda3/envs/vpg`. Bạn có thể chạy theo **2 cách** dưới đây (Khuyên dùng **Cách 1** vì nhanh và không sợ lỗi đường dẫn Conda).

---

## 📂 CÁCH 1: Chạy Trực Tiếp (Không Cần Kích Hoạt Conda) - KHUYÊN DÙNG

Cách này sử dụng trực tiếp đường dẫn tuyệt đối của trình biên dịch Python trong môi trường `vpg`, giúp tránh các lỗi cấu hình conda của terminal.

### 1. Chạy Demo Gắp Vật Thử Nghiệm (Có Giao Diện)
Kịch bản demo tự động khởi động simulator, sinh vật thể, điều khiển robot gắp 1 lần thành công, hiển thị kết quả trong 10 giây rồi tự động tắt.
```bash
# Bước 1: Di chuyển vào thư mục dự án
cd "/home/aics/Màn hình nền/Rl_Bin_Picing/visual-pushing-grasping"

# Bước 2: Chạy demo
/home/aics/miniconda3/envs/vpg/bin/python run_one_grasp_gui.py
```

### 2. Chạy Huấn Luyện Mô Hình (Training - Có Giao Diện)
Chạy vòng lặp huấn luyện chính (Đẩy và Gắp phối hợp) hiển thị trực quan trên màn hình:
```bash
# Bước 1: Di chuyển vào thư mục dự án
cd "/home/aics/Màn hình nền/Rl_Bin_Picing/visual-pushing-grasping"

# Bước 2: Chạy training có giao diện
/home/aics/miniconda3/envs/vpg/bin/python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations
```

### 3. Chạy Huấn Luyện Mô Hình Ẩn Giao Diện (Headless Training)
Thích hợp khi muốn chạy huấn luyện lâu dài ở chế độ nền (không mở cửa sổ CoppeliaSim đè lên màn hình làm việc):
```bash
# Bước 1: Di chuyển vào thư mục dự án
cd "/home/aics/Màn hình nền/Rl_Bin_Picing/visual-pushing-grasping"

# Bước 2: Khởi động simulator chạy ẩn ở DISPLAY=:1
DISPLAY=:1 /home/aics/CoppeliaSim_Pro_V4_7_0_rev4_Ubuntu22_04/coppeliaSim.sh -h -f simulation/simulation.ttt &

# Bước 3: Đợi 4 giây cho simulator khởi động xong, sau đó chạy mã nguồn huấn luyện
DISPLAY=:1 /home/aics/miniconda3/envs/vpg/bin/python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations
```

---

## 🐍 CÁCH 2: Kích Hoạt Môi Trường Conda Rồi Chạy

Nếu bạn muốn kích hoạt môi trường conda trước rồi chạy lệnh ngắn hơn:

```bash
# 1. Nạp cấu hình conda vào terminal hiện tại (nếu terminal chưa nhận lệnh conda)
source /home/aics/miniconda3/etc/profile.d/conda.sh

# 2. Kích hoạt môi trường vpg
conda activate vpg

# 3. Di chuyển vào thư mục dự án
cd "/home/aics/Màn hình nền/Rl_Bin_Picing/visual-pushing-grasping"

# 4. Chạy demo hoặc training bằng lệnh python thông thường
python run_one_grasp_gui.py
# hoặc
python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations
```

---

## 📊 Các Câu Lệnh Bổ Trợ Khác

### 1. Vẽ Biểu Đồ Hiệu Suất Huấn Luyện (Plotting)
Vẽ đồ thị tỉ lệ gắp thành công dựa trên thư mục log đã lưu (thay `TEN_THU_MUC_LOG` bằng tên thư mục thực tế trong thư mục `logs/` của bạn):
```bash
cd "/home/aics/Màn hình nền/Rl_Bin_Picing/visual-pushing-grasping"
/home/aics/miniconda3/envs/vpg/bin/python plot.py 'logs/TEN_THU_MUC_LOG'
```

### 2. Tiếp Tục Huấn Luyện Từ Checkpoint Cũ (Resume)
Nếu tiến trình huấn luyện bị ngắt quãng, bạn có thể chạy tiếp tục từ checkpoint bằng cách chỉ định thư mục log cũ và file snapshot:
```bash
cd "/home/aics/Màn hình nền/Rl_Bin_Picing/visual-pushing-grasping"
/home/aics/miniconda3/envs/vpg/bin/python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations --continue_logging --logging_directory logs/THU_MUC_CU --load_snapshot --snapshot_file logs/THU_MUC_CU/models/snapshot-backup.reinforcement.pth
```

---

## 🛠️ Hướng Dẫn Khắc Phục Sự Cố (Troubleshooting)

### 1. Lỗi cổng kết nối đã được sử dụng (Address already in use / Connection Refused)
Nếu CoppeliaSim bị tắt đột ngột, cổng API kết nối `19997` hoặc `23000` có thể bị treo. Hãy chạy lệnh sau để dọn sạch các tiến trình simulator và python đang chạy ngầm:
```bash
kill -9 $(pgrep -f "coppeliaSim") $(pgrep -f "main.py") $(pgrep -f "run_one_grasp_gui.py")
```

### 2. Lỗi `No such file or directory` khi chạy Python
* **Nguyên nhân**: Bạn chưa chạy lệnh `cd` vào thư mục `visual-pushing-grasping`.
* **Cách sửa**: Chạy lệnh `cd "/home/aics/Màn hình nền/Rl_Bin_Picing/visual-pushing-grasping"` trước khi chạy lệnh gọi file `.py`.
