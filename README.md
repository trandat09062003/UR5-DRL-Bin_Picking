# Điều Khiển Robot UR5 Phối Hợp Đẩy và Gắp (VPG) Trong CoppeliaSim

Dự án này triển khai thuật toán Học tăng cường sâu (Deep Reinforcement Learning - Q-Learning) để huấn luyện robot UR5 thực hiện các hành vi phối hợp Đẩy (Pushing) và Gắp (Grasping) vật thể trong môi trường mô phỏng CoppeliaSim V4.7.0.

Mã nguồn được kế thừa từ nghiên cứu *Visual Pushing and Grasping (VPG)* và được refactor lại để hoạt động ổn định trên các hệ thống Linux hiện đại sử dụng CoppeliaSim bản mới nhất.

---

## 🛠️ Các cải tiến & Tối ưu hóa kỹ thuật

* **Tích hợp ZeroMQ Remote API:** Đồng bộ trạng thái simulator trực tiếp thông qua API ZMQ mới (mặc định cổng `23000`), giúp phát hiện chính xác thời điểm scene được nạp đầy đủ thay vì sử dụng thời gian chờ cố định.
* **Cơ chế tự sửa lỗi (Self-Healing):** Nếu kịch bản gắp thử nghiệm thất bại, simulator sẽ tự reset, xóa sạch không gian làm việc, sinh lại vật thể dạng so le theo phương đứng (tránh va chạm) và tự động thử lại cho đến khi thành công.
* **Tự động đóng tiến trình:** Sau khi thực hiện thành công kịch bản gắp demo, GUI simulator sẽ được giữ lại 10 giây để kiểm tra trực quan và tự động đóng, giải phóng tài nguyên.
* **Khắc phục lỗi treo điều khiển (Deadlock):** Bổ sung cơ chế giám sát chuyển động của kẹp gắp (`stuck_count` trong `open_gripper`) và bảo vệ hàm di chuyển `move_to` giúp ngăn ngừa hoàn toàn hiện tượng đơ/treo luồng điều khiển trong quá trình huấn luyện dài hạn.
* **Hỗ trợ huấn luyện nền (Headless & CUDA):** Chạy huấn luyện hoàn toàn trong nền thông qua cấu hình `DISPLAY=:1` kết hợp cờ chạy ẩn `-h` của CoppeliaSim, tận dụng GPU với tăng tốc CUDA.
* **Khả năng tiếp tục huấn luyện (Resume):** Sửa lỗi chỉ số (index) khi tải tệp `clearance.log.txt` bị rỗng hoặc chỉ có 1 dòng, hỗ trợ tiếp tục huấn luyện mượt mà từ các checkpoint cũ bằng tham số `--continue_logging`.

---

## 💻 Cài đặt & Chuẩn bị môi trường

### 1. Yêu cầu hệ thống
* **Hệ điều hành:** Linux (đã thử nghiệm trên Ubuntu 22.04)
* **Phần mềm mô phỏng:** CoppeliaSim V4.7.0
* **Môi trường Python:** Conda (Python 3.8 trở lên)

### 2. Thiết lập môi trường
Kích hoạt môi trường conda chứa các thư viện cần thiết trước khi chạy:
```bash
conda activate vpg
```

---

## 🚀 Hướng dẫn chạy Demo (Gắp tự động)

Chương trình cung cấp một kịch bản demo tự động (`run_one_grasp_gui.py`) giúp khởi động simulator, nạp robot, sinh vật thể so le, thực hiện gắp, tự động reset nếu trượt và thoát sau 10 giây thành công.

Chạy lệnh sau:
```bash
python run_one_grasp_gui.py
```

---

## 🏋️ Huấn luyện mô hình từ đầu (Training)

Do liên kết tải các tệp trọng số đã huấn luyện trước (`vpg-original-sim-pretrained-10-obj.pth`) từ máy chủ gốc của Princeton hiện không hoạt động (lỗi 404), mô hình cần được huấn luyện từ đầu (`scratch`) trong môi trường mô phỏng.

### 1. Chạy huấn luyện (Có giao diện)
```bash
python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations
```

### 2. Chạy huấn luyện nền (Headless - Ẩn giao diện)
Thích hợp cho việc huấn luyện thời gian dài trên server/GPU:
```bash
# Khởi động simulator chạy ẩn
DISPLAY=:1 /home/aics/CoppeliaSim_Pro_V4_7_0_rev4_Ubuntu22_04/coppeliaSim.sh -h -f simulation/simulation.ttt &

# Chạy mã nguồn huấn luyện
DISPLAY=:1 python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations
```

### 3. Tiếp tục huấn luyện từ checkpoint cũ
Sử dụng tham số chỉ định thư mục log và tệp checkpoint muốn tiếp tục:
```bash
DISPLAY=:1 python main.py --is_sim --push_rewards --experience_replay --explore_rate_decay --save_visualizations --continue_logging --logging_directory logs/2026-06-05.11:18:37 --load_snapshot --snapshot_file logs/2026-06-05.11:18:37/models/snapshot-backup.reinforcement.pth
```

### 4. Vẽ biểu đồ kết quả
Để theo dõi hiệu suất huấn luyện (tỉ lệ gắp thành công theo thời gian):
```bash
python plot.py 'logs/THU_MUC_LOG_CUA_BAN'
```

---

## ⚠️ Khắc phục sự cố

Nếu simulator bị treo hoặc các cổng kết nối API (`19997` hoặc `23000`) báo lỗi đang được sử dụng (Address already in use), tiến hành dọn sạch các tiến trình chạy ngầm bằng lệnh:

```bash
kill -9 $(pgrep -f "coppeliaSim") $(pgrep -f "main.py")
```

---

## 📄 Tài liệu tham khảo
Dự án được xây dựng dựa trên bài báo khoa học:
**Learning Synergies between Pushing and Grasping with Self-supervised Deep Reinforcement Learning (IROS 2018)**
[ArXiv PDF](https://arxiv.org/pdf/1803.09956.pdf) | [Project Webpage](http://vpg.cs.princeton.edu/)
