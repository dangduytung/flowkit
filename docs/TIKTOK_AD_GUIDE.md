# CẨM NANG HƯỚNG DẪN TẠO VIDEO TIKTOK ADS & TIKTOK SHOP (USER GUIDE)

Tài liệu hướng dẫn phân hệ sản xuất video ngắn TikTok (9:16) từ **Link Video TikTok / TikTok Shop** bằng **Dòng Lệnh (CLI)** hoặc **Giao Tiếp Bằng Tiếng Việt Với AI Agent**.

---

## 📌 Phân Định Kiến Trúc: TikTok vs. Shopee

| Tiêu chí | 🎵 Phân hệ TikTok | 🛍️ Phân hệ Shopee |
|---|---|---|
| **Skill kích hoạt** | `/fk-tiktok-ad` | `/fk-shopee-ad` |
| **Gói công cụ (Tool)** | `tools.tiktok_ad` | `tools.shopee_ad` |
| **Nguồn tư liệu đầu vào** | **Link video TikTok / TikTok Shop** (cào video trend, âm thanh viral) | **File ZIP tải về từ Shopee** (ảnh thật shop, video shop, thông số SKU) |
| **Mục tiêu kịch bản** | Hook 1-2s giật gân, nhịp cắt nhanh bắt beat, viral sound | Unboxing, macro cận cảnh bàn tay POV, review tính năng thực tế |
| **Kêu gọi hành động (CTA)** | Bấm giỏ hàng màu vàng góc trái màn hình (`yellow_cart`) | Link bình luận ghim / Giỏ hàng Shopee (`shopee`) |
| **Tài liệu hướng dẫn** | `docs/TIKTOK_AD_GUIDE.md` (Web: `docs/ECOMMERCE_AD_GUIDE.html`) | `docs/SHOPEE_AD_GUIDE.md` (Web: `docs/ECOMMERCE_AD_GUIDE.html`) |

### 🤖 Cơ chế phân định nguồn tự động (Auto-Routing)
1. **Có Link TikTok**: Agent tự động chạy phân hệ này (`tools.tiktok_ad` / `/fk-tiktok-ad`).
2. **Nhắc đến File ZIP / Đã tải về**: Agent tự động chạy phân hệ Shopee (`tools.shopee_ad` / `/fk-shopee-ad`).
3. **Nói tên chung chung**: Agent quét thư mục `Shopee Downloads` trước; nếu không có file ZIP thì sẽ hỏi lại bạn để chọn nguồn.

---

## 1. Các Cách Tạo Video TikTok (`--mode`)

1. **`flow`**: Sinh 100% Video AI điện ảnh thông qua Google Flow nhưng điều chỉnh nhịp cắt nhanh (2-3s/cảnh) chuẩn thuật toán TikTok.
2. **`remix`**: Tải video TikTok gốc qua URL, tự động cắt ghép, đổi hook 2 giây đầu để tạo bản remix độc bản tránh trùng lặp bản quyền.
3. **`hybrid`**: Cảnh 1 (0-3s) dùng Hook giật gân AI + Cảnh 2-4 (3-15s) dùng clip review thực tế.

---

## 2. Các Phong Cách Kịch Bản TikTok (`--style`)

- **`viral_hook`**: Đặt câu hỏi sốc / tình huống oái oăm trong 2 giây đầu để kéo tỷ lệ giữ chân (Retention Rate).
- **`hands_on_pov`**: Góc nhìn thứ nhất (First-person POV) cận cảnh đôi tay thao tác, không lộ mặt, chuẩn video review affiliate triệu view.
- **`fast_cut`**: Nhịp cắt nhanh dồn dập 1-2 giây chuyển cảnh 1 lần theo beat nhạc nền.
- **`reaction_duet`**: Khung hình chia đôi hoặc lồng PIP phản ứng với sản phẩm.

---

## 3. Lời Kêu Gọi Hành Động (CTA) Cho TikTok Shop

* **`--cta yellow_cart`**: "Các bạn bấm ngay vào giỏ hàng màu vàng ở góc dưới bên trái màn hình để nhận ưu đãi hôm nay nhé!"
* **`--cta profile_bio`**: "Link sản phẩm mình để ngay trên Bio đầu trang, bấm vào xem nha!"
* **`--cta follow`**: "Bấm follow kênh để săn thêm nhiều deal hời và mẹo hay mỗi ngày!"
* **`--cta none`**: 4 cảnh tự nhiên, không kêu gọi gượng ép.

---

## 4. Dòng Lệnh Mẫu Phổ Biến (CLI)

```powershell
# 1. Tạo video POV không lộ mặt, không tiếng để ghép nhạc trend TikTok:
python -m tools.tiktok_ad.orchestrator --url "https://vt.tiktok.com/..." --style hands_on_pov --silent --clean

# 2. Tạo video quảng cáo TikTok Shop có CTA trỏ giỏ hàng vàng:
python -m tools.tiktok_ad.orchestrator --url "https://vt.tiktok.com/..." --style viral_hook --cta yellow_cart
```
