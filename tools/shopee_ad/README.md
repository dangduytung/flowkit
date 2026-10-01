# Shopee Video Ad Generator (Dynamic, Universal & Watermark-Free)

Hệ thống tự động hóa sản xuất video quảng cáo sản phẩm Shopee dạng dọc 9:16 (chuẩn TikTok / Reels / Shopee Video / Facebook Page). Hoạt động linh hoạt với **mọi ngành hàng** (Mỹ phẩm, Đồ gia dụng, Thời trang, Công nghệ, Thể thao, Đời sống), tự động tải ảnh làm tham chiếu lên Google Flow và **xóa sạch 100% logo Google Flow**.

👉 **Xem cẩm nang hướng dẫn sử dụng nhanh & cách giao tiếp với Agent**: [Tài Liệu Markdown (SHOPEE_AD_GUIDE.md)](../../docs/SHOPEE_AD_GUIDE.md) | 🌐 **[Mở Trực Tiếp Trên Trình Duyệt (ECOMMERCE_AD_GUIDE.html)](../../docs/ECOMMERCE_AD_GUIDE.html)**

---

## 1. Cơ Chế Thông Minh Đa Ngành Hàng (Universal Multi-Category)

Hệ thống **không bao giờ hardcode** theo một sản phẩm cụ thể. Khi đọc file ZIP của bất kỳ sản phẩm nào, hệ thống tự động:
1. **Phân tích ngành hàng tự động (`detect_product_category`)**:
   * 💄 **Mỹ phẩm & Chăm sóc da (`BEAUTY_SKINCARE`)**: Serum, kem dưỡng, son môi, kem chống nắng... -> Bối cảnh bàn trang điểm ngập tràn ánh nắng, thoa dưỡng chất thẩm thấu tức thì, ngắm làn da căng bóng rạng ngời, cất túi xách.
   * 🍳 **Nhà bếp & Đồ gia dụng (`KITCHEN_HOME`)**: Chảo chống dính, nồi chiên, máy xay, bình giữ nhiệt... -> Bối cảnh gian bếp hiện đại mặt đá, nấu nướng lướt nhẹ chống dính, thành phẩm thơm ngon, lau sạch bóng trong chớp mắt.
   * 👗 **Thời trang & Phụ kiện (`FASHION_APPAREL`)**: Áo thun, sơ mi, đầm váy, áo khoác, giày dép, túi xách... -> Cận cảnh chất vải mềm mát, đường may chuẩn form, chỉnh trang trước gương, sải bước tự tin dạo phố.
   * ⚡ **Công nghệ & Phụ kiện số (`TECH_GADGETS`)**: USB, thẻ nhớ, pin sạc, tai nghe, chuột máy tính... -> Bối cảnh bàn làm việc tối giản, kết nối cắm là nhận ngay, truyền tải siêu tốc, gọn gàng bỏ túi/móc khóa.
   * 🧘 **Sức khỏe & Thể thao (`HEALTH_FITNESS`)**: Súng massage, thảm yoga, dây kháng lực, đồ tập... -> Xung lực tác động sâu, cơ bắp thả lỏng nhẹ nhõm, nạp lại 100% năng lượng, gọn nhẹ mang theo.
   * 🌟 **Tiện ích đời sống (`GENERAL_LIFESTYLE`)**: Đồ dùng thông minh, decor bàn học, quà tặng... -> Thao tác mở hộp trực quan, giải quyết rắc rối hàng ngày, nâng tầm chất lượng sống.
2. **Quy tắc chống lệch khẩu hình (No Lip-Sync Glitch)**:
   * Toàn bộ prompt video AI đều khóa chuẩn Voice-over TVC: `"Calm focused expression, subtle genuine smile, mouth closed, no speaking, no dialogue. NO text overlays, NO talking."`
   * Nhân vật tương tác chân thật bằng hành động, cử chỉ và biểu cảm; giọng thuyết minh tiếng Việt do OmniVoice đảm nhiệm chuẩn xác từng giây.
3. **Tự động xóa sạch logo Google Flow**:
   * Tích hợp bộ lọc FFmpeg `delogo=x=568:y=1120:w=64:h=64`, xóa sạch watermark biểu tượng ngôi sao 4 cánh ở góc dưới màn hình mà không để lại vết mờ.

---

## 2. Các Chế Độ Hoạt Động

### 🌟 Chế độ 1: Google Flow AI Video (MẶC ĐỊNH)
* Tự động tải ảnh sản phẩm từ ZIP lên Google Flow làm hình ảnh tham chiếu (`upload-image`).
* Sinh 100% video AI sống động, nhân vật tương tác tự nhiên với sản phẩm theo đúng ngành hàng.
* Tự động xóa sạch watermark Google Flow.
```bash
# Chạy với sản phẩm mới nhất trong thư mục Shopee Downloads:
python -m tools.shopee_ad.orchestrator

# Chỉ định rõ chế độ Flow:
python -m tools.shopee_ad.orchestrator --mode flow
```

### 📦 Chế độ 2: Chỉ dùng ảnh/video gốc từ file ZIP (Offline / Local)
* Không cần mở Chrome Extension hay kết nối Google Flow.
* Tự động cắt video gốc của shop (nếu có) hoặc tạo chuyển động ảnh Ken Burns 9:16 trên nền mờ nghệ thuật.
```bash
python -m tools.shopee_ad.orchestrator --mode local
# hoặc:
python -m tools.shopee_ad.orchestrator --mode zip
```

---

## 3. Lựa Chọn Phong Cách & Ý Tưởng Sáng Tạo

Bạn có thể thay đổi phong cách kịch bản và câu chuyện bằng các cờ CLI:

### 🎬 Các phong cách kịch bản (`--style`):
1. `--style faceless_pov` *(POV Bàn Tay / Hands-On Tutorial - 100% Không Lộ Mặt)*:
   * **Chuẩn clip review TikTok Affiliate**: Mở hộp (Unbox), lắp ráp điều chỉnh phụ kiện, thử nghiệm thực tế (test co giãn vải, lăn chân, giấu dây...), kết quả góc setup/outfit thẩm mỹ.
   * Hoàn toàn không lộ mặt/đầu nhân vật (POV góc nhìn thứ nhất, cận cảnh bàn tay hoặc từ cổ trở xuống).
   * Thích hợp nhất khi kết hợp cùng `--no-voice` và `--no-overlay` để lấy video sạch rồi tự chèn nhạc trend + text trên TikTok!
2. `--style flow_cinematic` *(Mặc định)*:
   * 4 cảnh điện ảnh tập trung vào chiêm ngưỡng thiết kế, thao tác trải nghiệm trực tiếp, tính năng vượt trội và phong cách sống hàng ngày.
3. `--style problem_solution`:
   * Kịch bản Drama/Tình huống cấp bách theo ngành hàng (da khô sạm trước sự kiện, chảo dính cháy khét, không biết mặc gì mỗi sáng, đau mỏi vai gáy, đầy bộ nhớ...) -> Sản phẩm xuất hiện giải cứu ngoạn mục -> Nhẹ nhõm, thảnh thơi.
4. `--style lifestyle_edc`:
   * Phong cách sống năng động, du lịch, quán cafe, món đồ bỏ túi bất ly thân.
5. `--style hybrid`:
   * Kết hợp video AI cho cảnh con người/cảm xúc và chèn xen kẽ ảnh chụp thật từ shop Shopee.

### 💡 Tự do thêm ý tưởng sáng tạo (`--idea`):
```bash
# Video POV hướng dẫn sử dụng không lộ mặt, không voiceover, không dán chữ:
python -m tools.shopee_ad.orchestrator --style faceless_pov --no-voice --no-overlay

# Thêm bối cảnh hoặc phong cách riêng:
python -m tools.shopee_ad.orchestrator --style problem_solution --idea "một bạn sinh viên đang ở phòng trọ chuẩn bị đi phỏng vấn"

# Hoặc:
python -m tools.shopee_ad.orchestrator --style lifestyle_edc --idea "nữ vlogger du lịch Đà Lạt buổi sáng săn mây"
```

---

## 4. Các Tùy Chọn CLI Khác

| Cờ CLI | Ý nghĩa | Mặc định |
|---|---|---|
| `--mode {auto, both, flow, local, zip}` | Chế độ tạo video: 'auto' (ZIP có video sinh cả 2 bản `_local.mp4` & `_flow.mp4`), 'both', 'flow', 'local' | `auto` |
| `--zip <đường_dẫn>` | Chỉ định đường dẫn tới file ZIP cụ thể | Mới nhất trong Downloads |
| `--list` | Xem toàn bộ danh sách file ZIP đang có | - |
| `--style {faceless_pov, flow_cinematic, problem_solution, lifestyle_edc, hybrid}` | Phong cách kịch bản | `flow_cinematic` |
| `--no-voice`, `--silent` | Không tạo voiceover thuyết minh (video thuần hình ảnh, nhịp chuẩn ~5s/cảnh để ghép nhạc trend TikTok) | `False` |
| `--no-overlay`, `--clean` | Không chèn chữ Text Overlay (xuất video sạch để tự gõ text font TikTok/CapCut) | `False` |
| `--idea "..."` | Bổ sung ý tưởng / bối cảnh sáng tạo vào prompt | Không |
| `--cta {none, follow, shopee}` | Lời kêu gọi hành động ở cảnh kết thúc | `none` (4 cảnh Fanpage) |
| `--speed <float>` | Tốc độ đọc của OmniVoice | `1.03` (chuẩn KOC đàm thoại) |
| `--profile <id>` | ID profile giọng đọc tiếng Việt OmniVoice | Lấy từ .env `OMNIVOICE_PROFILE_ID` |
| `--channel-name <tên>` | Tên kênh xuất bản đa nền tảng | Lấy từ .env `SHOPEE_AD_CHANNEL_NAME` |
| `--channel-handle <id>` | Handle/ID kênh | Lấy từ .env `SHOPEE_AD_CHANNEL_HANDLE` |
| `--regen` | Bắt buộc sinh lại toàn bộ clip AI từ Google Flow | `False` |

---

## 5. Cấu Trúc Thư Mục Độc Lập

```
tools/shopee_ad/
├── __init__.py
├── config.py             # Quản lý đường dẫn và cấu hình môi trường (.env)
├── product_parser.py     # Phân tích file zip, trích xuất metadata và tính năng
├── storyboard.py         # Nhận diện ngành hàng thông minh & tạo kịch bản phân cảnh
├── omnivoice_client.py   # Client sinh giọng đọc tiếng Việt OmniVoice (VoiceStudio)
├── asset_extractor.py    # Xử lý video/ảnh gốc (Ken Burns 9:16)
├── video_assembler.py    # Ráp video, delogo Flow, text overlay UTF-8, xuất master audio & script
├── caption_generator.py  # Tạo caption đa nền tảng (Facebook Reels, TikTok, Shorts)
├── cover_generator.py    # Tạo ảnh bìa thumbnail 9:16 bắt mắt cho video
├── publish_guide.py      # Sinh file cẩm nang hướng dẫn đăng bài chi tiết từng nền tảng
├── flow_ad_generator.py  # Điều phối sinh video AI qua Google Flow Omni Flash
├── orchestrator.py       # Bộ điều khiển CLI trung tâm (quét ZIP, điều phối auto/flow/local)
└── README.md
```
