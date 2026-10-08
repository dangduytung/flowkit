# CẨM NANG HƯỚNG DẪN TẠO VIDEO TIKTOK ADS & TIKTOK SHOP (USER GUIDE)

Tài liệu hướng dẫn toàn diện cách sản xuất video quảng cáo ngắn 9:16 (chuẩn TikTok, TikTok Shop, Facebook Reels, YouTube Shorts) từ **File ZIP sản phẩm trong thư mục TikTok Downloads** bằng **Dòng Lệnh (CLI)** hoặc **Giao Tiếp Bằng Tiếng Việt Với AI Agent (`/fk-tiktok-ad`)**.

---

## 📌 Phân Định Kiến Trúc Đa Nền Tảng (TikTok vs. Shopee)

Hệ thống FlowKit được thiết kế module hóa độc lập và hoàn thiện 100% giữa hai phân hệ thương mại điện tử:

| Tiêu chí | 🎵 Phân hệ TikTok (`tools.tiktok_ad`) | 🛍️ Phân hệ Shopee (`tools.shopee_ad`) |
|---|---|---|
| **Skill kích hoạt** | `/fk-tiktok-ad` | `/fk-shopee-ad` |
| **Gói công cụ (Tool)** | `tools.tiktok_ad` | `tools.shopee_ad` |
| **Thư mục đầu vào (.env)** | `TIKTOK_DOWNLOADS_DIR` (`TikTok Downloads`) | `SHOPEE_DOWNLOADS_DIR` (`Shopee Downloads`) |
| **Thư mục đầu ra (Output)** | `output/tiktok_ads/{slug}/` | `output/shopee_ads/{slug}/` |
| **Nguồn tư liệu đầu vào** | **File ZIP TikTok / TikTok Shop** (Video shop gốc, ảnh sản phẩm, thông số mô tả, phản hồi thực tế, đánh giá sao) | **File ZIP Shopee** (Ảnh sản phẩm, video shop gốc, thông số chi tiết, phản hồi thực tế, đánh giá sao) |
| **Đặc trưng kịch bản** | Hook 2-3s đầu gây sốc / giữ chân (Retention Rate), nhịp cắt nhanh, giải quyết vấn đề cấp bách | Khai thác sâu tính năng sản phẩm, unboxing, cận cảnh chất liệu, review đàm thoại đời sống |
| **Kêu gọi hành động (CTA)** | Bấm giỏ hàng màu vàng góc trái màn hình (`yellow_cart`), link Bio (`profile_bio`), Follow (`follow`), Không CTA (`none`) | Link bình luận ghim / giỏ hàng Shopee (`shopee`), Follow (`follow`), Không CTA (`none`) |
| **Đặc quyền xuất video** | Xuất độc lập theo từng biến thể (Semantic Variant) không bao giờ bị ghi đè: Bản có voice (`_local_<variant>.mp4`), Bản tắt tiếng (`_silent.mp4`), Bản AI (`_flow_<variant>.mp4`) | Xuất độc lập theo từng biến thể (Semantic Variant): Bản Local (`_local_<variant>.mp4`), Bản tắt tiếng (`_silent.mp4`), Bản AI (`_flow_<variant>.mp4`) |
| **Vùng an toàn giao diện (Safe Zone)** | Text Overlay đặt ở vùng an toàn phía trên ($y=140, y=210$) tránh bị che bởi Giỏ Hàng Vàng và icon TikTok | Text Overlay tiêu chuẩn 9:16 |
| **Tài liệu hướng dẫn** | `docs/TIKTOK_AD_GUIDE.md` (Web: `docs/ECOMMERCE_AD_GUIDE.html`) | `docs/SHOPEE_AD_GUIDE.md` (Web: `docs/ECOMMERCE_AD_GUIDE.html`) |

### 🤖 Cơ chế Auto-Routing: Khi bạn yêu cầu "Tạo video...", Agent xử lý thế nào?

Hệ thống tự động điều phối nguồn thông minh:
1. **Dựa vào ngữ cảnh & từ khóa**:
   - Nếu bạn dùng skill `/fk-tiktok-ad` hoặc nói "Tạo video TikTok", "TikTok Shop", "file TikTok vừa tải": Agent tự động chạy `tools.tiktok_ad` và quét thư mục `TIKTOK_DOWNLOADS_DIR`.
   - Nếu bạn dùng skill `/fk-shopee-ad` hoặc nói "Tạo video Shopee", "file Shopee vừa tải": Agent tự động chạy `tools.shopee_ad` và quét thư mục `SHOPEE_DOWNLOADS_DIR`.
2. **Khi bạn cung cấp đường dẫn file cụ thể**:
   - Chỉ định trực tiếp cờ `--zip <đường_dẫn>` tới file ZIP cần xử lý.
3. **Khi chỉ nói tên sản phẩm chung chung**:
   - Agent sẽ kiểm tra cả hai thư mục `TikTok Downloads` và `Shopee Downloads` để tìm file ZIP mới nhất phù hợp.

---

## 1. Cơ Chế Xử Lý Tự Động (Dynamic Universal)

Phân hệ TikTok Ad vận hành hoàn toàn tự động, áp dụng cho mọi ngành hàng sản phẩm mà không cần cấu hình thủ công:
1. **Phân loại danh mục tự động**: Nhận diện ngành hàng thông minh (`HEALTH_FITNESS`, `BEAUTY_SKINCARE`, `TECH_GADGETS`, `KITCHEN_HOME`, `FASHION_APPAREL`, `GENERAL_LIFESTYLE`).
2. **Làm sạch tiêu đề chuẩn TikTok**: Tự động loại bỏ từ khóa spam SEO, mã SKU, ký tự thừa để câu thoại tự nhiên, trôi chảy khi đọc thuyết minh.
3. **Trích xuất sub-clip thông minh**: Quét video gốc của shop, tự động né tránh các đoạn nháy hình (flash/glitch), chọn ra các góc quay đẹp nhất để cắt thành các phân cảnh 9:16 mượt mà.
4. **Hiệu ứng Ken Burns cho ảnh tĩnh**: Với các cảnh sử dụng ảnh sản phẩm, tự động tạo chuyển động lia máy điện ảnh (Pan & Zoom) trên nền mờ 9:16.
5. **Safe Zone Protection**: Bố trí Text Overlay ở vị trí an toàn phía trên để không bị che khuất bởi nút Giỏ Hàng Vàng, tên kênh, caption và thanh tương tác bên phải của TikTok.
6. **Xóa sạch 100% watermark**: Tự động xóa sạch logo 4 cánh của Google Flow bằng bộ lọc delogo chuẩn xác.

---

## 2. Bảng Tra Cứu Các Chế Độ Tạo Video (`--mode`)

| Chế độ (`--mode`) | Nguồn tư liệu | Đặc điểm & Kết quả xuất ra |
|---|---|---|
| **`auto`** *(Mặc định)* | **Tự động nhận diện tư liệu** | Tự động xuất cả 2 bản video: **`_local.mp4`** (có giọng đọc OmniVoice KOC) và **`_silent.mp4`** (video tắt tiếng kèm track stereo silence để bạn ghép nhạc thịnh hành trực tiếp trên app TikTok). Nếu FlowKit server đang kết nối, tự động kích hoạt sinh thêm bản **`_flow.mp4`**. |
| **`local`** | **Video & ảnh gốc từ file ZIP** | Dựng siêu tốc offline trong 10-15 giây qua FFmpeg. Cắt ghép từ video gốc của shop kết hợp hiệu ứng Ken Burns cho ảnh tĩnh. |
| **`flow`** | **100% Video AI Google Flow** | Sinh toàn bộ 4 phân cảnh điện ảnh 9:16 thông qua Google Flow. Tự động tải ảnh thật từ file ZIP lên làm tham chiếu vật lý và neo khuôn mặt nhân vật đồng nhất qua Anchor Frame. |
| **`both`** | **Local + Google Flow AI** | Chạy song song cả hai phân hệ để tạo ra đầy đủ các bản video so sánh. |

---

## 3. Bảng Tra Cứu Toàn Bộ 7 Phong Cách Kịch Bản (`--style`)

Hệ thống hỗ trợ đầy đủ 7 phong cách video ngắn chuẩn thuật toán TikTok:

| Phong cách (`--style`) | Cấu trúc phân cảnh & Đặc điểm | Ngành hàng phù hợp nhất |
|---|---|---|
| **`viral_hook`**<br>*(Mặc định TikTok)* | **Hook 2-3 giây đầu xoáy sâu nỗi đau / câu hỏi tò mò**:<br>• Cảnh 1 (Hook): Đặt câu hỏi sốc hoặc tình huống ức chế thường gặp để kéo tỷ lệ giữ chân (Retention Rate).<br>• Cảnh 2 (Feature 1): Trực diện thao tác giải pháp, cảm nhận sự thư giãn / tiện ích.<br>• Cảnh 3 (Feature 2): Chi tiết cấu tạo, độ bền, hoàn thiện tỉ mỉ.<br>• Cảnh 4 (Social Proof): Phản hồi tích cực từ người dùng thực tế và chốt đơn uy tín (không nêu số liệu bán cụ thể để tuân thủ chính sách quảng cáo TikTok). | Mọi ngành hàng thương mại điện tử, đồ tiện ích, giải pháp giải quyết nỗi đau thường nhật. |
| **`faceless_pov`** / **`hands_on_pov`** | **100% Không lộ mặt (First-Person POV)**:<br>• Cảnh 1: Mở hộp (Unbox) trên mặt bàn sạch sẽ, ấn tượng ban đầu.<br>• Cảnh 2: Hướng dẫn thao tác sử dụng thực tế (cận cảnh bàn tay/chân).<br>• Cảnh 3: Chi tiết công năng và chất liệu bền bỉ.<br>• Cảnh 4: Tổng kết không gian setup hoàn thiện, gọn gàng, tinh tươm. | Đồ tiện ích văn phòng, gia dụng, công nghệ, thời trang, dụng cụ cá nhân *(chuẩn định dạng review affiliate triệu view)*. |
| **`problem_solution`** | **Drama / Tình huống cấp bách "Giải cứu"**:<br>• Mở đầu bằng nỗi đau thực tế (mệt mỏi, bừa bộn, hỏng việc...) ➔ Sản phẩm xuất hiện giải cứu ngoạn mục ➔ Trải nghiệm hiệu năng vượt trội ➔ Kết quả thỏa mãn, nhẹ nhõm. | Kích thích nhu cầu mua sắm mạnh mẽ, các sản phẩm giải quyết vấn đề cấp bách. |
| **`flow_cinematic`** | **KOC Review điện ảnh có nhân vật**:<br>Nhân vật KOC xuất hiện trải nghiệm sản phẩm trong không gian studio/phòng hiện đại. Gương mặt và trang phục được đồng nhất xuyên suốt video bằng công nghệ Anchor Frame. | Mỹ phẩm, thời trang lookbook, sản phẩm cần người đại diện phong cách sống. |
| **`lifestyle_edc`** | **Phong cách sống năng động (Everyday Carry)**:<br>Món đồ luôn mang theo bên mình khi đi làm, cà phê, dã ngoại, di chuyển hàng ngày. | Phụ kiện cá nhân, bình nước, balo, túi xách, cáp sạc, thiết bị di động. |
| **`hybrid`** | **Kết hợp Video AI + Ảnh chụp thật**:<br>Cảnh 1 và 3 dùng Video AI tạo cảm xúc điện ảnh; Cảnh 2 và 4 sử dụng ảnh chụp thật từ shop để tăng độ tin cậy khi mua hàng. | Sản phẩm cần sự cân bằng giữa hình ảnh điện ảnh bắt mắt và tính chân thực. |

---

## 4. Các Tùy Chọn Âm Thanh, Chữ & Lời Kêu Gọi Hành Động (CTA)

* **`--cta {yellow_cart, profile_bio, follow, none}`**:
  * `yellow_cart` *(Mặc định TikTok Shop)*: Cảnh cuối kêu gọi người xem bấm vào giỏ hàng màu vàng ở góc dưới bên trái màn hình.
  * `profile_bio`: Cảnh cuối kêu gọi xem đường link đính kèm trên Bio đầu kênh.
  * `follow`: Cảnh cuối kêu gọi bấm follow kênh để nhận thêm mẹo hay và deal hời.
  * `none`: 4 cảnh review tự nhiên, không kêu gọi thương mại.
* **`--no-voice`** (hoặc `--silent`): Mutes giọng đọc OmniVoice, xuất video với track âm thanh stereo silence sẵn sàng để bạn tải lên TikTok và chọn nhạc thịnh hành (Trending Sound) trực tiếp.
* **`--no-overlay`** (hoặc `--clean`): Tắt toàn bộ Text Overlay trên video, xuất ra video sạch 100% để bạn tự chèn chữ theo font yêu thích trong CapCut hoặc TikTok Studio.
* **`--tag <tên>`**: Gắn nhãn/tag tùy chỉnh vào tên file (ví dụ: `--tag v2`, `--tag testA`) để thoải mái xuất thử nghiệm nhiều biến thể mà không bị ghi đè.
* **`--speed <float>`**: Tốc độ đọc OmniVoice (mặc định: `1.03` chuẩn nhịp điệu KOC đàm thoại tự nhiên).
* **`--profile <id>`**: ID cấu hình giọng đọc OmniVoice (KOC Việt).
* **`--crop {blur_bg, center_crop}`**: Cơ chế chuyển đổi tỷ lệ 9:16 (mặc định: `blur_bg` giữ nguyên khung hình gốc trên nền mờ sang trọng).
* **`--idea "ý tưởng riêng"`**: Bổ sung bối cảnh hoặc phong cách mong muốn cho kịch bản.
* **`--scene <id> [<id> ...]`**: Chỉ làm lại các phân cảnh được chọn (kịch bản của cảnh đó được cập nhật theo builder mới nhất); các cảnh còn lại giữ nguyên giọng đọc và clip. Khi Google Flow lỗi một vài cảnh, các clip đã xong vẫn được lưu và tool in sẵn lệnh `--scene ...` để chạy lại.
* **`--regen`**: Sinh lại toàn bộ clip AI từ Google Flow, **giữ nguyên** storyboard (kể cả phần bạn sửa tay). Muốn viết lại kịch bản từ đầu thì dùng **`--force-storyboard`** (hoặc `--idea`).
  * Prompt Flow giờ được viết theo kiểu **clip quay điện thoại cầm tay** (xem `tools/common/prompts/realism.py`). `storyboard_*.json` tạo từ bản cũ vẫn được tự làm sạch khi gửi đi, nhưng muốn dùng hẳn kịch bản mới thì chạy lại với **`--force-storyboard`**.

---

## 5. Dòng Lệnh Mẫu Phổ Biến (CLI Cheat Sheet)

Chạy trong PowerShell hoặc Terminal tại thư mục gốc repository:

```powershell
# 1. Tự động nhận diện file ZIP mới nhất trong thư mục TikTok Downloads:
python -m tools.tiktok_ad.orchestrator

# 2. Tạo video POV không lộ mặt, không giọng đọc, không dán chữ (để ghép nhạc trend & gõ chữ TikTok):
python -m tools.tiktok_ad.orchestrator --style faceless_pov --silent --clean

# 3. Xuất nhiều phong cách khác nhau để tự xem và chọn video tốt nhất (Không bị ghi đè):
python -m tools.tiktok_ad.orchestrator --style viral_hook --tag hook1
python -m tools.tiktok_ad.orchestrator --style faceless_pov --tag pov1
python -m tools.tiktok_ad.orchestrator --style problem_solution --tag drama1

# 4. Tạo video TikTok Shop chuẩn với kịch bản Hook 3s đầu & CTA giỏ hàng vàng:
python -m tools.tiktok_ad.orchestrator --style viral_hook --cta yellow_cart

# 5. Sinh video AI điện ảnh thông qua Google Flow:
python -m tools.tiktok_ad.orchestrator --mode flow --style viral_hook --cta yellow_cart

# 6. Kịch bản Drama Problem - Solution kêu gọi follow kênh:
python -m tools.tiktok_ad.orchestrator --style problem_solution --cta follow

# 7. Chỉ định file ZIP cụ thể:
python -m tools.tiktok_ad.orchestrator --zip "path/to/tiktok_product_file.zip" --style viral_hook

# 8. Liệt kê tất cả các file ZIP có sẵn trong thư mục TikTok Downloads:
python -m tools.tiktok_ad.orchestrator --list
```

---

## 6. Hướng Dẫn Giao Tiếp Với AI Agent (Bằng Tiếng Việt Tự Nhiên)

Khi làm việc với AI Agent (thông qua skill `/fk-tiktok-ad`), bạn chỉ cần trao đổi bằng ngôn ngữ tự nhiên:

| Yêu cầu của bạn | Câu nhắn mẫu cho AI Agent | Lệnh Agent sẽ thực thi ngầm |
|---|---|---|
| **Dựng nhanh từ file TikTok vừa tải** | *"Tạo video TikTok cho file zip vừa tải về nhé"* | `python -m tools.tiktok_ad.orchestrator --mode auto --style viral_hook` |
| **Dạng POV không mặt, không tiếng** | *"Làm clip POV không lộ mặt, tắt tiếng và không dán chữ để tôi tự ghép nhạc trend TikTok"* | `python -m tools.tiktok_ad.orchestrator --style faceless_pov --silent --clean` |
| **Xuất nhiều bản so sánh A/B** | *"Tạo cho tôi 2 bản: 1 bản viral_hook và 1 bản faceless_pov gắn tag để tôi tự so sánh nhé"* | `python -m tools.tiktok_ad.orchestrator --style viral_hook --tag v1` và `... --style faceless_pov --tag v2` |
| **Video TikTok Shop trỏ giỏ hàng vàng** | *"Tạo video quảng cáo TikTok Shop có CTA trỏ vào giỏ hàng màu vàng"* | `python -m tools.tiktok_ad.orchestrator --style viral_hook --cta yellow_cart` |
| **Sinh video Google Flow AI** | *"Tạo video Google Flow AI cho sản phẩm TikTok, có giọng đọc KOC đầy đủ"* | `python -m tools.tiktok_ad.orchestrator --mode flow --style flow_cinematic` |
| **Video tình huống cấp bách** | *"Dựng kịch bản drama giải cứu cho sản phẩm, có kêu gọi follow kênh"* | `python -m tools.tiktok_ad.orchestrator --style problem_solution --cta follow` |
| **Kiểm tra file đã tải** | *"Xem trong thư mục TikTok Downloads có những file zip nào"* | `python -m tools.tiktok_ad.orchestrator --list` |

---

## 7. Trọn Bộ Thành Phẩm Xuất Bản (Deliverables Package)

Hệ thống sử dụng cơ chế đặt tên **Semantic Variant (`{slug}_{mode}_{style}[_clean][_cta-<cta>][_tag].mp4`)**. Tất cả các biến thể được xuất vào thư mục `output/tiktok_ads/<slug>/final/` mà **không bao giờ đè lên nhau**, giúp bạn thoải mái mở thư mục ra xem và chọn video ưng ý nhất để upload:

```
output/tiktok_ads/<slug>/
├── final/
│   ├── <slug>_local_viral_hook.mp4            # Bản dựng Local có voice KOC (Style: viral_hook)
│   ├── <slug>_local_viral_hook_silent.mp4     # Bản dựng Local tắt tiếng (chỉ sinh khi truyền cờ --silent để ghép nhạc trend TikTok)
│   ├── <slug>_local_faceless_pov_clean.mp4    # Bản POV sạch chữ, không bị đè bởi bản viral_hook
│   ├── <slug>_flow_flow_cinematic.mp4         # Video AI điện ảnh từ Google Flow (Style: flow_cinematic)
│   ├── <slug>_<variant>_cover.jpg             # Ảnh bìa (Thumbnail/Cover) 9:16 tương ứng cho từng biến thể
│   ├── <slug>_<variant>_voiceover.mp3         # File audio thuyết minh MP3 48kHz cho từng biến thể
│   ├── <slug>_<variant>_script.txt            # File văn bản kịch bản chi tiết & timecode từng cảnh
│   ├── <slug>_<variant>_publish_guide.txt     # Hướng dẫn quy trình đăng video & gắn Giỏ Hàng Vàng
│   ├── <slug>_<variant>_tiktok_caption.txt    # Caption & Hashtag tối ưu thuật toán TikTok Shop
│   ├── <slug>_<variant>_facebook_caption.txt  # Caption tối ưu tương tác Facebook Reels
│   └── <slug>_<variant>_shorts_caption.txt    # Caption & Tag chuẩn SEO YouTube Shorts
├── storyboard_viral_hook.json                 # Kịch bản JSON lưu riêng biệt theo từng style
├── storyboard_faceless_pov.json               # Đảm bảo không xung đột kịch bản khi chuyển đổi style
└── assets/                                    # Toàn bộ hình ảnh và video trích xuất từ file ZIP gốc
```

---

## 8. Quy Chuẩn Về Quyền Riêng Tư & Tính Linh Hoạt (Universal Compliance)

Hệ thống được phát triển theo các tiêu chuẩn kỹ thuật nghiêm ngặt:
- **Không hardcode**: Không chứa bất kỳ tên riêng tác giả, tên cá nhân, thương hiệu độc quyền hoặc tài khoản cố định nào trong mã nguồn và tài liệu.
- **Tương thích toàn diện**: Hoạt động mượt mà với mọi file ZIP sản phẩm thương mại điện tử từ bất kỳ danh mục hàng hóa nào.
- **Sẵn sàng đa kênh**: Sản phẩm xuất ra đạt chuẩn hiển thị trên TikTok, TikTok Shop, Facebook Reels và YouTube Shorts.
