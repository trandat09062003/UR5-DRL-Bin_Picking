# 🚀 Hướng Dẫn Mô Phỏng & Huấn Luyện UR5-VPG (Visual Pushing & Grasping)

Tài liệu này cung cấp tài liệu kỹ thuật chi tiết về cấu trúc dự án và cách vận hành quy trình học tăng cường (Deep Q-Learning) cho robot cánh tay UR5 thực hiện tác vụ Bin Picking trong môi trường CoppeliaSim.

---

## 📂 1. CẤU TRÚC THƯ MỤC VÀ TỔ CHỨC FILE

Dự án đã được quy hoạch lại để chuyên nghiệp và dễ bảo trì hơn. Các tệp tin được phân loại theo chức năng:

### 1.1. Các File Chạy Chính (Entry-point Scripts)
Đây là các bash script bạn dùng để tương tác nhanh với hệ thống:
*   `run_training.sh`: Khởi chạy quá trình Train. Hệ thống sẽ luôn thả **DUY NHẤT 1 vật thể ngẫu nhiên** (màu sắc/hình khối bất kỳ) mỗi đợt để robot luyện tập từ từ, tránh gây nhiễu môi trường.
*   `run_test.sh`: Khởi chạy chế độ Kiểm thử (Test). Hệ thống sẽ rải cùng lúc **10 VẬT THỂ LỘN XỘN** xuống bàn. Robot sẽ phải dùng model đã học được để lần lượt gắp bỏ hết cả 10 vật này vào thùng (thực hiện 30 lượt test).
*   `edit_scene.sh`: Mở CoppeliaSim ở chế độ chỉnh sửa giao diện 3D (Scene Editor).

### 1.2. Thư Mục Mã Nguồn Python
*   `main.py`, `robot.py`, `trainer.py`, `models.py`: Chứa lõi thuật toán học tăng cường (RL), cấu trúc mạng Nơ-ron và logic kết nối điều khiển cánh tay robot.
*   `logger.py`, `utils.py`: Lưu trữ log, biểu đồ, và các hàm hỗ trợ tính toán ảnh RGB-D.
*   `evaluate.py`, `plot.py`: Công cụ vẽ biểu đồ tỷ lệ thành công và phân tích log sau khi Test.

### 1.3. Thư Mục Dữ Liệu
*   `logs/`: Nơi tự động lưu các checkpoint (model não bộ của robot) và dữ liệu ảnh/độ sâu mỗi vòng chạy.
*   `objects/blocks/`: Chứa các bản thiết kế 3D (file `.obj`) đại diện cho các vật thể mà robot cần gắp.
*   `simulation/`: Chứa file `simulation.ttt` (bản đồ môi trường vật lý trong CoppeliaSim).
*   `tools/`: Thư mục lưu các script tiện ích bổ trợ như căn chỉnh camera (`calibrate.py`), kiểm tra độ va chạm (`touch.py`), và gắp thủ công 1 lần (`run_one_grasp_gui.py`).

---

## 🚦 2. HƯỚNG DẪN SỬ DỤNG

### Bước Chuẩn Bị (Bắt Buộc)
Mở terminal và luôn đảm bảo bạn đang đứng ở thư mục gốc của project trước khi chạy bất kỳ script nào:
```bash
cd "/home/aics/Màn hình nền/Rl_Bin_Picing/visual-pushing-grasping"
```

### 2.1. Quá Trình Huấn Luyện (Training)
Tất cả các script học đã được tích hợp tính năng **Auto-Resume** (tự động phát hiện model cũ và học tiếp). Nếu bạn muốn bắt đầu lại từ đầu (từ con số 0), hãy xóa thư mục `logs/`.

Chạy lệnh sau để bắt đầu huấn luyện với 1 vật thể ngẫu nhiên:
```bash
./run_training.sh
```

### 2.2. Kiểm Thử và Đánh Giá (Testing & Evaluation)
Sau khi huấn luyện thành công (hoặc đạt được độ chính xác mong muốn), chạy lệnh dưới đây để kiểm tra thực tế khả năng dọn dẹp đống 10 vật thể của robot:
```bash
./run_test.sh
```
*Lưu ý: Mặc định script sẽ chạy 30 lượt. Mỗi lượt yêu cầu dọn sạch 10 vật.*

Sau khi Test xong, dùng lệnh sau để vẽ biểu đồ kết quả:
```bash
/home/aics/miniconda3/envs/vpg/bin/python plot.py 'logs/TÊN_THƯ_MỤC_CẦN_VẼ'
```

---

## 🛠️ 3. XỬ LÝ SỰ CỐ (TROUBLESHOOTING)

**Lỗi ModuleNotFoundError (Không nhận diện môi trường Conda)**
Nếu bạn quyết định không dùng bash script mà gõ lệnh `python main.py` trực tiếp, bạn bắt buộc phải chỉ định đường dẫn môi trường:
```bash
/home/aics/miniconda3/envs/vpg/bin/python main.py ...
```
*(Các file `.sh` tôi viết đã tự động bao bọc đường dẫn này cho bạn nên bạn không cần gõ lệnh dài dòng).*
