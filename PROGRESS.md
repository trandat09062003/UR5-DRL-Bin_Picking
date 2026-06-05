# Nhật ký Tiến trình Dự án & Đánh giá Kết quả (Visual Pushing and Grasping)

Tài liệu này ghi nhận chi tiết các hạng mục đã tối ưu hóa, các tính năng đã hoàn thành, cũng như các điểm hạn chế cần cải tiến trong tương lai cho hệ thống Visual Pushing and Grasping (VPG) mô phỏng trên CoppeliaSim.

---

## ✅ Những thứ đã đạt được (Accomplished)

### 1. Đồng bộ hóa Physics & Khắc phục lỗi điều khiển Gripper
- **Vấn đề:** Các vòng lặp kiểm tra khớp và điều khiển đóng/mở gripper trước đây chạy liên tục không ngừng nghỉ, gây nghẽn CPU và nghẽn API kết nối socket của simulator, dẫn đến việc CoppeliaSim bị đơ hoặc cánh tay chuyển động giật cục, gắp trượt liên tục do mất đồng bộ.
- **Giải pháp:** Thêm thời gian trễ nhỏ (`time.sleep(0.01)`) bên trong các vòng lặp chờ trạng thái khớp (`close_gripper`, `open_gripper` và `move_to` trong `robot.py`). Điều này giúp giải phóng tài nguyên CPU và cho phép bộ công cụ vật lý của CoppeliaSim có đủ thời gian cập nhật trạng thái khớp chính xác.

### 2. Tự động hóa Cơ chế Sinh Vật thể (Staggered Spawning)
- **Vấn đề:** Khi sinh nhiều vật thể cùng lúc tại các vị trí ngẫu nhiên, các vật thể dễ bị chồng lấp lên nhau hoặc sinh ra ở góc nghiêng dẫn đến va chạm mạnh và văng ra ngoài sàn mô phỏng ngay khi vừa bắt đầu.
- **Giải pháp:** Thiết lập chiều cao sinh vật thể so le (`0.15 + object_idx * 0.05`) và bắt buộc thời gian chờ ổn định (`time.sleep(3.0)`). Vật thể sẽ rơi tự do và định vị ổn định trên sàn trước khi robot thực hiện lượt gắp đầu tiên.

### 3. Tự động hóa Kịch bản Kiểm thử & Cơ chế Tự Phục hồi (Self-Healing)
- **Vấn đề:** Khi robot gắp trượt, chương trình dừng lại hoặc tiếp tục gắp trên đống đổ nát bị xô lệch khiến các lượt gắp sau chắc chắn trượt.
- **Giải pháp:** Cải tiến kịch bản chạy thử nghiệm `run_one_grasp_gui.py`:
  - Nếu lượt gắp trước đó thất bại (`Grasp thất bại`), hệ thống tự động reset simulator và gọi hàm tái tạo đồ vật từ đầu để thực hiện lượt gắp mới. Vòng lặp sẽ tiếp diễn cho đến khi gắp thành công.
  - Khi gắp thành công, hệ thống hiển thị kết quả trực quan trong 10 giây rồi tự động tắt simulator và giải phóng cổng kết nối. Không cần thao tác thủ công.

### 4. Nhận diện trạng thái Scene bằng ZeroMQ Remote API
- **Vấn đề:** Thời gian tải scene của CoppeliaSim thường không ổn định, nếu chỉ sử dụng lệnh `time.sleep` cứng dễ dẫn đến lỗi kết nối API khi simulator chưa sẵn sàng.
- **Giải pháp:** Sử dụng thư viện ZeroMQ API (port 23000) để liên tục kiểm tra sự hiện diện của robot UR5 trong scene. Khi scene được xác nhận đã tải hoàn tất, chương trình mới kích hoạt luồng chạy chính.

---

## ❌ Những thứ chưa đạt được & Hướng phát triển (Limitations & Future Work)

### 1. Phụ thuộc một phần vào Legacy Remote API
- Hệ thống điều khiển chuyển động của cánh tay UR5 hiện tại vẫn phụ thuộc vào file `vrep.py` (Legacy Remote API qua cổng 19997). Mặc dù hoạt động ổn định nhờ cơ chế tối ưu luồng, về lâu dài nên chuyển hoàn toàn mã nguồn điều khiển robot sang ZeroMQ API để đạt tốc độ phản hồi và tính đồng bộ tối đa.

### 2. Ngưỡng Nhận Diện Thành Công cố định (Hardcoded Grasp Threshold)
- Lệnh `robot.check_grasp()` hiện đang kiểm tra thành công dựa trên khoảng cách cố định giữa 2 má kẹp gripper (`gripper_position < -0.045`). Đối với các khối vật thể có kích thước quá lớn hoặc quá nhỏ, ngưỡng này có thể cho kết quả sai lệch.
- **Hướng cải tiến:** Cần đọc thông tin bounding box hoặc kích thước thực tế của mesh vật thể được sinh ra để điều chỉnh ngưỡng kiểm tra linh hoạt.

### 3. Cảnh báo script PID cũ của Khớp điều khiển (Joint Control Callback Script)
- Scene mô phỏng `simulation.ttt` sử dụng kịch bản điều khiển PID cũ cho các khớp, CoppeliaSim phiên bản mới liên tục đưa ra cảnh báo lỗi thời (deprecated warnings).
- **Hướng cải tiến:** Cần chuyển đổi script PID cũ này sang định dạng hàm callback khớp chuẩn mới (Joint Callback Function) của CoppeliaSim để tăng hiệu suất chạy mô phỏng.
