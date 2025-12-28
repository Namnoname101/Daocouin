import uiautomator2 as u2
import time

def test_click_may_bay():
    print("--- TEST CLICK CHẾ ĐỘ MÁY BAY ---")
    try:
        d = u2.connect()
        print(f"📱 Đã kết nối: {d.info.get('model')}")

        # Tìm phần tử có chứa chữ "máy bay"
        # Dùng textContains sẽ an toàn hơn là gõ chính xác 100%
        btn_maybay = d(textContains="máy bay")
        
        if btn_maybay.exists:
            print("👇 [Lần 1] Bấm vào chữ 'máy bay' (Ngắt mạng)")
            btn_maybay.click()
            time.sleep(3) # Đợi máy bay bật lên
            
            print("👇 [Lần 2] Bấm vào chữ 'máy bay' (Mở lại mạng)")
            btn_maybay.click()
            
            print("⏳ Đợi 8 giây cho 4G hồi phục...")
            time.sleep(8)
            print("✅ Xong.")
        else:
            print("❌ Không tìm thấy chữ nào là 'máy bay' trên màn hình.")
            print("👉 Lưu ý: Chữ trên màn hình phải chuẩn tiếng Việt.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    test_click_may_bay()