# Shopee Video Ad Generator (Dynamic & Loosely-Coupled)

Hệ thống tự động hóa sản xuất video quảng cáo sản phẩm Shopee dạng dọc 9:16 (chuẩn TikTok / Reels / Shopee Video). Tích hợp linh hoạt giữa tư liệu Shopee (video/ảnh), OmniVoice TTS và FlowKit.

---

## 1. Cơ chế hoạt động (Không Hardcode)

* **Nguồn lấy file ZIP**:
  * Tự động quét thư mục `C:\Users\Tung\Downloads\Shopee Downloads\`.
  * Có thể truyền file zip cụ thể qua cờ `--zip <đường_dẫn>`.
  * Xem danh sách tất cả các zip có trong máy qua cờ `--list`.
* **Phân tích sản phẩm tự động**:
  * Đọc `description.txt` để trích xuất tên sản phẩm, link Shopee, số sao, lượt bán, tính năng chính.
  * Tự động tạo thư mục output riêng theo slug sản phẩm: `output/shopee_ads/<product_slug>/`.
* **Kịch bản linh hoạt (`storyboard.json`)**:
  * Mỗi sản phẩm có 1 file kịch bản `storyboard.json` riêng trong thư mục của nó.
  * Lần đầu chạy, hệ thống tự động sinh template 5 cảnh phù hợp với sản phẩm.
  * Bạn có thể chỉnh sửa lại text, phụ đề, thời gian cắt clip trong file `storyboard.json` bất cứ lúc nào.
* **Hỗ trợ cả sản phẩm CHỈ CÓ ẢNH**:
  * Nếu sản phẩm không có clip video sẵn, hệ thống tự động tạo hiệu ứng chuyển động ảnh **Ken Burns (Pan & Zoom)** 9:16 trên nền mờ từ các ảnh chụp trong file zip.

---

## 2. Các lệnh sử dụng

### Xem danh sách file zip đang có trong máy:
```bash
python -m tools.shopee_ad.orchestrator --list
```

### Chạy tự động file zip mới nhất:
```bash
python -m tools.shopee_ad.orchestrator
```

### Chạy cho một file zip cụ thể:
```bash
python -m tools.shopee_ad.orchestrator --zip "C:\Users\Tung\Downloads\Shopee Downloads\ten_file.zip"
```

### Tùy chỉnh tốc độ đọc hoặc Profile giọng:
```bash
python -m tools.shopee_ad.orchestrator --speed 0.88 --profile 338d9ba2
```

---

## 3. Cấu trúc thư mục độc lập (Loose Coupling)

```
tools/shopee_ad/
├── __init__.py
├── config.py           # Quản lý đường dẫn và biến môi trường
├── product_parser.py   # Phân tích file zip, đọc description.txt
├── storyboard.py       # Quản lý và tự sinh storyboard.json theo sản phẩm
├── omnivoice_client.py # Client gọi OmniVoice API riêng (kèm speed, auth)
├── asset_extractor.py  # Cắt sub-clip 9:16 và tạo Ken Burns slide từ ảnh
├── video_assembler.py  # Ghép audio, burn text overlay và concat ffmpeg
├── orchestrator.py     # Bộ điều phối CLI trung tâm
└── README.md
```

Tất cả code nằm trong `tools/shopee_ad/`, giữ nguyên 100% các file core của FlowKit (`agent/`, `skills/`, `extension/`).
