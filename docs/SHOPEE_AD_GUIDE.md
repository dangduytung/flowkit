# CẨM NANG HƯỚNG DẪN TẠO VIDEO SHOPEE ADS (USER GUIDE)

Tài liệu hướng dẫn toàn diện cách sản xuất video quảng cáo sản phẩm 9:16 (chuẩn TikTok, Reels, Shopee Video, YouTube Shorts) từ **File ZIP Shopee** bằng **Dòng Lệnh (CLI)** hoặc **Giao Tiếp Bằng Tiếng Việt Với AI Agent**.

---

## 📌 Phân Định Kiến Trúc Đa Nền Tảng (Shopee vs. TikTok)

Hệ thống FlowKit được thiết kế tách bạch rõ ràng giữa các phân hệ nền tảng từ **Skill**, **Prompt/Kịch bản**, **Công cụ** cho đến **Tài liệu hướng dẫn**:

| Tiêu chí | 🛍️ Phân hệ Shopee (`tools.shopee_ad`) | 🎵 Phân hệ TikTok (`tools.tiktok_ad`) |
|---|---|---|
| **Skill kích hoạt** | `/fk-shopee-ad` | `/fk-tiktok-ad` |
| **Gói công cụ (Tool)** | `tools.shopee_ad` | `tools.tiktok_ad` |
| **Thư mục đầu vào (.env)** | `SHOPEE_DOWNLOADS_DIR` (`Shopee Downloads`) | `TIKTOK_DOWNLOADS_DIR` (`TikTok Downloads`) |
| **Thư mục đầu ra (Output)** | `output/shopee_ads/{slug}/` | `output/tiktok_ads/{slug}/` |
| **Nguồn tư liệu đầu vào** | **File ZIP tải về từ Shopee** (ảnh sản phẩm, video shop, thông số mô tả, phản hồi thực tế, đánh giá sao) | **File ZIP tải về từ TikTok** (ảnh sản phẩm, video shop, thông số mô tả, phản hồi thực tế, đánh giá sao) |
| **Đặc trưng Prompt & Kịch bản** | • Khai thác sâu tính năng sản phẩm từ tư liệu thật.<br>• Góc quay cận cảnh POV bàn tay, mở hộp, test co giãn/chất liệu.<br>• Giọng đọc review đàm thoại tự nhiên, giải quyết vấn đề đời sống. | • Hook 2-3s đầu gây sốc/tò mò kéo retention rate.<br>• Nhịp cắt nhanh (Fast-cut), bắt beat âm thanh thịnh hành.<br>• Format POV cận cảnh thao tác, giải pháp cấp bách. |
| **Kêu gọi hành động (CTA)** | `--cta shopee` (link bình luận ghim/giỏ Shopee) | `--cta yellow_cart` (bấm giỏ hàng màu vàng góc trái màn hình) |
| **Đặc quyền xuất video** | Xuất độc lập theo từng biến thể (Semantic Variant) không bao giờ bị ghi đè: Bản Local (`_local_<variant>.mp4`), Bản tắt tiếng (`_silent.mp4`), Bản AI (`_flow_<variant>.mp4`) | Xuất độc lập theo từng biến thể (Semantic Variant): Bản Local (`_local_<variant>.mp4`), Bản tắt tiếng (`_silent.mp4`), Bản AI (`_flow_<variant>.mp4`) |
| **Tài liệu hướng dẫn** | `docs/SHOPEE_AD_GUIDE.md` (Web: `docs/ECOMMERCE_AD_GUIDE.html`) | `docs/TIKTOK_AD_GUIDE.md` (Web: `docs/ECOMMERCE_AD_GUIDE.html`) |

### 🤖 Khi bạn bảo "Tạo video...", Agent biết lấy sản phẩm từ Shopee hay TikTok bằng cách nào?

Hệ thống tự động điều phối nguồn (**Auto-Routing**) theo các nguyên tắc rõ ràng:
1. **Dựa vào Skill kích hoạt hoặc từ khóa nền tảng**:
   - Khi dùng `/fk-tiktok-ad` hoặc nhắc tới "TikTok", "TikTok Shop": Agent chạy phân hệ `tools.tiktok_ad` quét thư mục `TIKTOK_DOWNLOADS_DIR`.
   - Khi dùng `/fk-shopee-ad` hoặc nhắc tới "Shopee": Agent chạy phân hệ `tools.shopee_ad` quét thư mục `SHOPEE_DOWNLOADS_DIR`.
2. **Khi bạn chỉ định file ZIP trực tiếp**:
   - Sử dụng cờ `--zip <đường_dẫn>` tới file ZIP cần sản xuất.
3. **Khi chỉ nói tên sản phẩm chung chung**:
   - Agent sẽ kiểm tra thư mục sản phẩm tương ứng và tự động chọn file ZIP mới nhất phù hợp.

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
* **`--tag <tên>`**: Gắn nhãn/tag tùy chỉnh vào tên file (ví dụ: `--tag v2`, `--tag test1`) để thoải mái xuất thử nghiệm nhiều biến thể mà không bị ghi đè.
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

### 🔬 Trường hợp 2: Xuất nhiều phong cách khác nhau để tự so sánh và chọn video tốt nhất
*(Nhờ cơ chế Semantic Variant, các file sẽ không bao giờ đè lên nhau trong thư mục `final/`)*
```powershell
python -m tools.shopee_ad.orchestrator --style faceless_pov --tag v1
python -m tools.shopee_ad.orchestrator --style flow_cinematic --tag v2
python -m tools.shopee_ad.orchestrator --style problem_solution --tag v3
```

### 🎙️ Trường hợp 3: Dạng KOC Review đầy đủ (Có giọng đọc OmniVoice + Chữ Text Overlay)
* **Bằng Google Flow**:
  ```powershell
  python -m tools.shopee_ad.orchestrator --mode flow --style flow_cinematic
  ```
* **Bằng Local**:
  ```powershell
  python -m tools.shopee_ad.orchestrator --mode local --style flow_cinematic
  ```

### 🎭 Trường hợp 4: Kịch bản Drama "Giải cứu" (Problem - Solution) có kêu gọi Follow kênh
```powershell
python -m tools.shopee_ad.orchestrator --mode flow --style problem_solution --cta follow
```

### 💡 Trường hợp 5: Thêm ý tưởng bối cảnh riêng
```powershell
python -m tools.shopee_ad.orchestrator --style faceless_pov --idea "phòng làm việc phong cách tối giản ánh đèn vàng" --no-voice
```

### 📂 Trường hợp 6: Chỉ định file ZIP cụ thể (thay vì lấy file mới nhất)
```powershell
python -m tools.shopee_ad.orchestrator --zip "path/to/shopee_product_file.zip" --style faceless_pov --no-voice
```

---

## 6. Hướng Dẫn Giao Tiếp Với AI Agent (Nhắn Bằng Tiếng Việt Tự Nhiên)

Khi làm việc với AI Agent (như Antigravity), bạn **không cần phải gõ dòng lệnh phức tạp**. Bạn chỉ cần chat bằng ngôn ngữ tự nhiên:

| Mục tiêu của bạn | Câu bạn có thể nhắn cho Agent | Hành động Agent sẽ tự động thực hiện |
|---|---|---|
| **Dạng POV không mặt, không tiếng** | *"Tạo video POV không lộ mặt, không voice, không chữ cho sản phẩm quần kaki vừa tải nhé"* | Tự động kích hoạt: `--style faceless_pov --no-voice --no-overlay` |
| **Xuất nhiều bản để so sánh** | *"Xuất cho tôi 2 bản: 1 bản POV và 1 bản cinematic để tôi xem cái nào đẹp hơn"* | Tự động kích hoạt: `--style faceless_pov --tag v1` và `--style flow_cinematic --tag v2` |
| **Dựng nhanh từ video shop có sẵn** | *"Cắt video local cho tôi chiếc quần kaki, kiểu POV hướng dẫn sử dụng không tiếng"* | Tự động kích hoạt: `--mode local --style faceless_pov --no-voice --no-overlay` |
| **Sinh Video AI Google Flow đầy đủ** | *"Tạo video Google Flow cho khay giấu dây, có voice đọc đầy đủ"* | Tự động kích hoạt: `--mode flow --style flow_cinematic` |
| **Làm video drama giải cứu** | *"Làm video kịch bản drama cứu nguy cho khay giấu dây, thêm đoạn cuối kêu gọi follow kênh nhé"* | Tự động kích hoạt: `--style problem_solution --cta follow` |
| **Tạo video có ý tưởng bối cảnh riêng** | *"Tạo video AI cho ghế kê chân, kiểu POV bàn tay, bối cảnh phòng làm việc tone màu tối decor đèn led"* | Tự động kích hoạt: `--style faceless_pov --idea "..." --no-voice` |
| **Xem lại danh sách file ZIP có sẵn** | *"Xem trong thư mục Downloads có những file sản phẩm nào rồi"* | Tự động quét và liệt kê danh sách file ZIP kèm dung lượng |
| **Kiểm tra hoặc tùy chỉnh kịch bản trước khi dựng** | *"Cho tôi xem kịch bản phân cảnh của sản phẩm trước khi sinh video"* | Tự động đọc hoặc tạo `storyboard_<style>.json` và trình bày cho bạn duyệt |

---

## 7. Cấu Trúc Thư Mục Xuất Thành Phẩm

Hệ thống sử dụng cơ chế đặt tên **Semantic Variant (`{slug}_{mode}_{style}[_clean][_cta-<cta>][_tag].mp4`)**. Tất cả các biến thể được lưu trữ trong thư mục `output/shopee_ads/<slug>/final/` mà **không bao giờ đè lên nhau**, giúp bạn dễ dàng duyệt qua các phiên bản để chọn video ưng ý nhất trước khi tải lên các kênh:

```
output/shopee_ads/<slug>/
├── final/
│   ├── <slug>_local_flow_cinematic.mp4        # Video dựng từ video shop (Style: flow_cinematic)
│   ├── <slug>_local_flow_cinematic_silent.mp4 # Video Local tắt tiếng (chỉ sinh khi truyền cờ --silent để ghép nhạc trend)
│   ├── <slug>_local_faceless_pov_clean.mp4    # Bản POV sạch chữ (Style: faceless_pov, clean)
│   ├── <slug>_flow_flow_cinematic.mp4         # Video AI điện ảnh từ Google Flow (9:16)
│   ├── <slug>_<variant>_cover.jpg             # Ảnh bìa (Thumbnail/Cover) 9:16 bắt mắt cho từng biến thể
│   ├── <slug>_<variant>_voiceover.mp3         # File audio giọng đọc đầy đủ (MP3 48kHz)
│   ├── <slug>_<variant>_script.txt            # File text kịch bản & timecode từng cảnh
│   └── <slug>_<variant>_publish_guide.txt     # Cẩm nang hướng dẫn đăng bài (Facebook/TikTok/Shorts)
├── storyboard_flow_cinematic.json             # Kịch bản JSON lưu riêng biệt theo từng phong cách
├── storyboard_faceless_pov.json               # Đảm bảo an toàn không xung đột kịch bản khi đổi style
└── assets/                                    # Ảnh và video gốc trích xuất từ file ZIP Shopee
```
