# CẨM NANG HƯỚNG DẪN TẠO VIDEO SHOPEE ADS (USER GUIDE)

Tài liệu hướng dẫn toàn diện cách sản xuất video quảng cáo sản phẩm 9:16 (chuẩn TikTok, Reels, Shopee Video, YouTube Shorts) từ **File ZIP Shopee** bằng **Dòng Lệnh (CLI)** hoặc **Giao Tiếp Bằng Tiếng Việt Với AI Agent**.

---

## 📌 Phân Định Kiến Trúc Đa Nền Tảng (Shopee vs. TikTok)

Hệ thống FlowKit được thiết kế tách bạch rõ ràng giữa các phân hệ nền tảng từ **Skill**, **Prompt/Kịch bản**, **Công cụ** cho đến **Tài liệu hướng dẫn**:

| Tiêu chí | 🛍️ Phân hệ Shopee (Hiện tại) | 🎵 Phân hệ TikTok (Mở rộng tương lai) |
|---|---|---|
| **Skill kích hoạt** | `/fk-shopee-ad` | `/fk-tiktok-ad` |
| **Gói công cụ (Tool)** | `tools.shopee_ad` | `tools.tiktok_ad` |
| **Nguồn tư liệu đầu vào** | **File ZIP tải về từ Shopee** (ảnh sản phẩm, video shop, mô tả, thông số, lượt mua, đánh giá) | **Link video TikTok / TikTok Shop** (video scraper, âm thanh trend, hiệu ứng viral) |
| **Đặc trưng Prompt & Kịch bản** | • Khai thác sâu tính năng sản phẩm từ tư liệu thật.<br>• Góc quay cận cảnh POV bàn tay, mở hộp, test co giãn/chất liệu.<br>• Giọng đọc review đàm thoại tự nhiên, giải quyết vấn đề đời sống. | • Tập trung vào Hook 1-2 giây đầu gây sốc/tò mò.<br>• Nhịp cắt nhanh (Fast-cut 1-2s), bắt beat âm thanh thịnh hành.<br>• Format biến hình, reaction, thử thách viral. |
| **Kêu gọi hành động (CTA)** | `--cta shopee` (link bình luận ghim/giỏ Shopee) | `--cta tiktok` (bấm giỏ hàng màu vàng góc trái màn hình) |
| **Tài liệu hướng dẫn** | `docs/SHOPEE_AD_GUIDE.md` (Web: `docs/ECOMMERCE_AD_GUIDE.html`) | `docs/TIKTOK_AD_GUIDE.md` (Web: `docs/ECOMMERCE_AD_GUIDE.html`) |

### 🤖 Khi bạn bảo "Tạo video...", Agent biết lấy sản phẩm từ Shopee hay TikTok bằng cách nào?

Hệ thống tự động điều phối nguồn (**Auto-Routing**) theo 3 nguyên tắc rõ ràng:
1. **Dựa vào định dạng đầu vào (Ưu tiên số 1 — Chuẩn xác 100%)**:
   - **Gửi Link TikTok / Douyin** (ví dụ: `https://vt.tiktok.com/...`): Agent tự động chuyển sang phân hệ **TikTok** (`/fk-tiktok-ad` / `tools.tiktok_ad`) để cào video, bóc tách âm thanh trend và dựng hook viral.
   - **Nhắc đến File ZIP / Sản phẩm vừa tải về**: Agent tự động kích hoạt phân hệ **Shopee** (`/fk-shopee-ad` / `tools.shopee_ad`) để quét thư mục `Shopee Downloads` trên máy bạn.
2. **Khi bạn chỉ nói tên sản phẩm chung chung** *(ví dụ: "Tạo video cho tôi chiếc quần kaki nhé")*:
   - Agent sẽ tự động quét thư mục `Shopee Downloads` trước. Nếu thấy file ZIP khớp với sản phẩm bạn vừa tải, Agent lập tức dựng từ file đó.
3. **Cơ chế dự phòng (Fallback)**:
   - Nếu không có link TikTok và trong thư mục máy cũng chưa có file ZIP tương ứng, Agent sẽ hỏi xác nhận: *"Bạn muốn lấy từ file ZIP Shopee trong máy hay gửi link video TikTok để tôi phân tích?"*

---

## 1. Tổng Quan Về Hệ Thống Shopee Ads

Hệ thống hoạt động theo cơ chế **Dynamic Universal** (tự động thích ứng với mọi sản phẩm từ file ZIP tải về trên Shopee):
1. **Phân tích sản phẩm**: Tự động nhận diện ngành hàng (Công nghệ, Đồ tiện ích văn phòng, Thời trang, Nhà bếp, Mỹ phẩm, Sức khỏe).
2. **Làm sạch tiêu đề**: Tự động lược bỏ các từ spam SEO, mã SKU nước ngoài để tiêu đề ngắn gọn, tự nhiên chuẩn đàm thoại.
3. **Tránh giật hình video shop**: Tự động quét và né các đoạn chuyển cảnh flash/glitch nháy hình trong video gốc của shop.
4. **Không watermark**: Tự động xóa sạch logo 4 cánh của Google Flow bằng bộ lọc delogo chuẩn xác.

---

## 2. Bảng Tra Cứu Các Chế Độ Tạo Video (`--mode`)

| Chế độ (`--mode`) | Nguồn tư liệu | Đặc điểm & Khuyến nghị |
|---|---|---|
| **`flow`** | **100% Video AI từ Google Flow** | Sinh các góc quay điện ảnh 9:16 sống động, tự nạp ảnh thật từ ZIP làm tham chiếu, tự động xóa sạch watermark Google Flow. Phù hợp khi muốn hình ảnh sáng tạo, điện ảnh, góc quay độc lạ. |
| **`local`** | **Video/Ảnh gốc trong file ZIP** | • Nếu ZIP có video gốc của shop: Tự động phân tích cảnh, né đoạn chớp giật, cắt thành 4 sub-clip 9:16 mượt mà.<br>• Nếu ZIP chỉ có ảnh: Tự tạo chuyển động lia máy Pan & Zoom (Ken Burns) trên nền mờ 9:16.<br>👉 **Ưu điểm**: Chạy offline siêu tốc (10-15s là xong), tận dụng 100% tư liệu thật của shop. |
| **`hybrid`** | **Kết hợp Video AI + Ảnh thật** | Cảnh 1 và 3 dùng Video AI cảm xúc; Cảnh 2 và 4 dùng ảnh thật từ ZIP. |
| **`auto`** *(Mặc định)* | **Tự động nhận diện** | Nếu ZIP có video: Tự động dựng cả bản `_local.mp4` và `_flow.mp4` để bạn chọn. Nếu chỉ có ảnh: Tự chạy `flow`. |

---

## 3. Bảng Tra Cứu Các Phong Cách Kịch Bản (`--style`)

| Phong cách (`--style`) | Góc quay & Nội dung | Phù hợp với |
|---|---|---|
| **`faceless_pov`**<br>*(Mới nhất)* | **100% Không lộ mặt**: Góc nhìn thứ nhất (First-Person POV), cận cảnh đôi bàn tay thao tác, hoặc từ cổ trở xuống (neck-down).<br>• Cảnh 1: Mở hộp (Unbox) trên bàn/sàn.<br>• Cảnh 2: Hướng dẫn lắp đặt / chỉnh nấc / xoay con lăn / kéo giãn vải.<br>• Cảnh 3: Thử nghiệm thực tế trong đời sống (lăn chân, giấu dây, đi thử...).<br>• Cảnh 4: Góc setup hoàn thiện sạch sẽ, outfit gọn gàng. | Đồ tiện ích văn phòng, ghế kê chân, khay giấu dây, quần áo, gia dụng, phụ kiện công nghệ *(chuẩn clip review chân thực triệu view)*. |
| **`flow_cinematic`**<br>*(Mặc định)* | **KOC Review điện ảnh có nhân vật**: KOC xuất hiện ngắm nghía sản phẩm, cận cảnh bàn tay trải nghiệm, hiệu quả sử dụng và phong cách sống. Có khuôn mặt đồng nhất xuyên suốt video. | Sản phẩm cần người đại diện KOC, mỹ phẩm, thời trang phong cách lookbook. |
| **`problem_solution`** | **Drama / Tình huống cấp bách**: Mở đầu bằng nỗi đau (đầy ổ cứng giữa deadline, dây điện bừa bộn dưới chân, sáng nào cũng đắn đo chọn đồ, chảo dính cháy...) -> Sản phẩm xuất hiện giải cứu ngoạn mục -> Nhẹ nhõm thảnh thơi. | Kích thích nhu cầu mua sắm mạnh, giải quyết vấn đề cấp bách. |
| **`lifestyle_edc`** | **Phong cách sống năng động**: Món đồ bỏ túi bất ly thân mang theo bên mình khi đi làm, du lịch, quán cà phê. | Đồ mang theo người (ví, túi, cáp sạc, USB, bình nước...). |

---

## 4. Các Tùy Chọn Âm Thanh & Lời Kêu Gọi Hành Động (CTA)

* **`--no-voice`** (hoặc `--silent`): Tắt giọng đọc OmniVoice, xuất video chuẩn 20 giây (4 cảnh x 5 giây) với track âm thanh silent stereo sẵn sàng để bạn ném vào TikTok/CapCut ghép nhạc trend.
* **`--no-overlay`** (hoặc `--clean`): Tắt chữ Text Overlay vàng/trắng, xuất video sạch 100% để bạn tự chèn chữ font yêu thích.
* **`--cta {none, follow, shopee, tiktok}`**:
  * `none` (mặc định 4 cảnh): Thích hợp video review tự nhiên hoặc chạy ads không lộ tính thương mại.
  * `follow` (5 cảnh): Cảnh cuối kêu gọi bấm follow kênh (ở dạng `faceless_pov` cảnh cuối vẫn chỉ xuất hiện bàn tay giơ ngón tay like/thân thiện).
  * `shopee` (5 cảnh): Cảnh cuối kêu gọi bấm vào link giỏ hàng hoặc xem bình luận ghim.
  * `tiktok` (5 cảnh): Cảnh cuối kêu gọi bấm vào giỏ hàng màu vàng ở góc dưới bên trái màn hình.
* **`--idea "nội dung"`**: Thêm ý tưởng/bối cảnh riêng (ví dụ: `--idea "bàn làm việc tone gỗ sồi ấm cúng"`).
* **`--speed <float>`**: Tốc độ đọc OmniVoice (mặc định: `1.03` chuẩn KOC đàm thoại tự nhiên).

---

## 5. Dòng Lệnh Mẫu Phổ Biến (CLI Cheat Sheet)

Chạy trực tiếp trong terminal tại thư mục gốc repository `flowkit`:

### 🎯 Trường hợp 1: Dạng TikTok POV không lộ mặt, không voice, không dán chữ
*(Chuẩn clip review TikTok Affiliate để tự gắn nhạc trend và gõ chữ trong TikTok)*
* **Bằng Google Flow AI**:
  ```powershell
  python -m tools.shopee_ad.orchestrator --mode flow --style faceless_pov --no-voice --no-overlay
  ```
* **Bằng Video gốc của Shop (Local siêu nhanh 10 giây)**:
  ```powershell
  python -m tools.shopee_ad.orchestrator --mode local --style faceless_pov --no-voice --no-overlay
  ```

### 🎙️ Trường hợp 2: Dạng KOC Review đầy đủ (Có giọng đọc OmniVoice + Chữ Text Overlay)
* **Bằng Google Flow**:
  ```powershell
  python -m tools.shopee_ad.orchestrator --mode flow --style flow_cinematic
  ```
* **Bằng Local**:
  ```powershell
  python -m tools.shopee_ad.orchestrator --mode local --style flow_cinematic
  ```

### 🎭 Trường hợp 3: Kịch bản Drama "Giải cứu" (Problem - Solution) có kêu gọi Follow kênh
```powershell
python -m tools.shopee_ad.orchestrator --mode flow --style problem_solution --cta follow
```

### 💡 Trường hợp 4: Thêm ý tưởng bối cảnh riêng
```powershell
python -m tools.shopee_ad.orchestrator --style faceless_pov --idea "phòng làm việc phong cách tối giản ánh đèn vàng" --no-voice
```

### 📂 Trường hợp 5: Chỉ định file ZIP cụ thể (thay vì lấy file mới nhất)
```powershell
python -m tools.shopee_ad.orchestrator --zip "C:\Users\user\Downloads\Shopee Downloads\file_san_pham.zip" --style faceless_pov --no-voice
```

---

## 6. Hướng Dẫn Giao Tiếp Với AI Agent (Nhắn Bằng Tiếng Việt Tự Nhiên)

Khi làm việc với AI Agent (như Antigravity), bạn **không cần phải gõ dòng lệnh phức tạp**. Bạn chỉ cần chat bằng ngôn ngữ tự nhiên:

| Mục tiêu của bạn | Câu bạn có thể nhắn cho Agent | Hành động Agent sẽ tự động thực hiện |
|---|---|---|
| **Dạng POV không mặt, không tiếng** | *"Tạo video POV không lộ mặt, không voice, không chữ cho sản phẩm quần kaki vừa tải nhé"* | Tự động kích hoạt: `--style faceless_pov --no-voice --no-overlay` |
| **Dựng nhanh từ video shop có sẵn** | *"Cắt video local cho tôi chiếc quần kaki, kiểu POV hướng dẫn sử dụng không tiếng"* | Tự động kích hoạt: `--mode local --style faceless_pov --no-voice --no-overlay` |
| **Sinh Video AI Google Flow đầy đủ** | *"Tạo video Google Flow cho khay giấu dây, có voice đọc đầy đủ"* | Tự động kích hoạt: `--mode flow --style flow_cinematic` |
| **Làm video drama giải cứu** | *"Làm video kịch bản drama cứu nguy cho khay giấu dây, thêm đoạn cuối kêu gọi follow kênh nhé"* | Tự động kích hoạt: `--style problem_solution --cta follow` |
| **Tạo video có ý tưởng bối cảnh riêng** | *"Tạo video AI cho ghế kê chân, kiểu POV bàn tay, bối cảnh phòng làm việc tone màu tối decor đèn led"* | Tự động kích hoạt: `--style faceless_pov --idea "..." --no-voice` |
| **Xem lại danh sách file ZIP có sẵn** | *"Xem trong thư mục Downloads có những file sản phẩm nào rồi"* | Tự động quét và liệt kê danh sách file ZIP kèm dung lượng |
| **Kiểm tra hoặc tùy chỉnh kịch bản trước khi dựng** | *"Cho tôi xem kịch bản phân cảnh của sản phẩm trước khi sinh video"* | Tự động đọc hoặc tạo `storyboard.json` và trình bày cho bạn duyệt |

---

## 7. Cấu Trúc Thư Mục Xuất Thành Phẩm

Khi chạy xong một sản phẩm, thư mục `output/shopee_ads/<tên-slug-sản-phẩm>/` sẽ tự động có đầy đủ bộ tài nguyên:
```
output/shopee_ads/<slug>/
├── final/
│   ├── <slug>_flow.mp4           # Video thành phẩm AI từ Google Flow (9:16)
│   ├── <slug>_local.mp4          # Video thành phẩm dựng từ video shop (9:16)
│   ├── <slug>_cover.jpg          # Ảnh bìa (Thumbnail/Cover) 9:16 bắt mắt
│   ├── <slug>_voiceover.mp3      # File audio giọng đọc đầy đủ (nếu có voice)
│   ├── <slug>_script.txt         # File text kịch bản & timecode từng cảnh
│   └── <slug>_publish_guide.txt  # Cẩm nang hướng dẫn đăng bài (Facebook/TikTok/Shorts)
├── storyboard.json               # File kịch bản JSON (có thể chỉnh sửa thủ công)
└── assets/                       # Ảnh và video gốc trích xuất từ file ZIP Shopee
```
