# Background Music (BGM) Library for FlowKit & Shopee Ads

Thư mục lưu trữ nhạc nền ngẫu nhiên dùng chung cho toàn bộ hệ thống tạo video quảng cáo Shopee / TikTok.

## Cơ chế hoạt động:

1. **Mặc định (Default: Tắt BGM)**:
   - Hệ thống **mặc định KHÔNG chèn nhạc nền** vào video xuất bản (chỉ giữ âm thanh môi trường vật lý Google Flow Foley + giọng đọc OmniVoice trong trẻo, chân thực).

2. **Kích hoạt BGM ngẫu nhiên (`--bgm`)**:
   - Khi truyền cờ `--bgm` (không kèm tham số), hệ thống sẽ quét toàn bộ các file nhạc trong thư mục này (`.mp3`, `.wav`, `.m4a`) và bốc ngẫu nhiên một bài cho mỗi video thành phẩm để tránh trùng lặp giai điệu.

3. **Chỉ định bài nhạc cụ thể (`--bgm <path>`)**:
   - Truyền tham số kèm đường dẫn: `--bgm "assets/bgm/01_Cheerful_Glow_general_household_ad.mp3"` hoặc tên file: `--bgm 01_Cheerful_Glow_general_household_ad.mp3`.
   - Hoặc đặt file `bgm.mp3` trong `output/shopee_ads/<slug>/assets/`.

4. **Các bài nhạc có sẵn trong kho**:
   - `01_Cheerful_Glow_general_household_ad.mp3`: Đồ gia dụng tổng hợp, vui tươi, nhẹ nhàng.
   - `02_Gentle_Samba_Flow_kitchen_cleaning.mp3`: Nhà bếp, vệ sinh, lau dọn, thư thái.
   - `03_Warm_Funk_Glide_smart_gadgets.mp3`: Đồ công nghệ thông minh, phụ kiện bàn làm việc.
   - `04_Triumph_Smile_home_decor_lifestyle.mp3`: Decor nhà cửa, đời sống, tích cực.

5. **Thêm nhạc mới**:
   - Chỉ cần thả thêm bất kỳ file `.mp3`, `.wav` nào vào thư mục này, hệ thống sẽ tự động nhận diện vào danh sách chọn ngẫu nhiên khi bật `--bgm`.
