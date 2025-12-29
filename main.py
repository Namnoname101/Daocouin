import time
import random
import string
import os
import subprocess
import sys

# --- FIX LỖI 'ANTIALIAS' ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import ddddocr
from DrissionPage import ChromiumPage, ChromiumOptions
import uiautomator2 as u2

# --- CẤU HÌNH ---
TARGET_URL = "https://gamety.org/?ref=386714"
ACCOUNT_FILE = "account.txt"

CHROME_PATH_1 = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PATH_2 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"C:\Users\dai99\AppData\Local\Google\Chrome\User Data"
PROFILE_DIR = "Profile 1"

# --- DATA ---
TEN = ["Nam", "Hung", "Dung", "Minh", "Tuan", "Thang", "Dat", "Hieu", "Trung", "Thanh", "Binh", "Son", "Phuc", "Lam", "Linh", "Trang", "Mai", "Hoa", "Lan", "Huong", "Vy", "Ngan", "Kiet", "Long", "Quan", "Khoi", "Ha", "Thao"]
HO = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan", "Vu", "Vo", "Dang", "Bui", "Do", "Ho", "Ngo", "Duong", "Ly"]
DEM = ["Van", "Thi", "Minh", "Huu", "Duc", "Dinh", "Xuan", "Ngoc", "Quang", "Tuan", "Thanh", "Hai", "Khanh", "Hoai"]
NICK_PREFIX = ["be", "mr", "ms", "iam", "im", "thay", "cau", "anh", "chi"]
NICK_SUFFIX = ["cute", "vip", "pro", "kun", "ka", "zz", "xx", "baby", "love"]

class GametyAutoReg:
    def __init__(self):
        self.page = None
        self.total_runs = 0
        self.success_count = 0
        
        try: self.ocr = ddddocr.DdddOcr(show_ad=False)
        except: self.ocr = ddddocr.DdddOcr()
        
        if not os.path.exists(ACCOUNT_FILE):
            with open(ACCOUNT_FILE, "w") as f: pass
            
        if os.path.exists(CHROME_PATH_1): self.chrome_exe = CHROME_PATH_1
        elif os.path.exists(CHROME_PATH_2): self.chrome_exe = CHROME_PATH_2
        else: self.chrome_exe = None

    # --- UI & LOG ---
    def countdown_timer(self, seconds):
        while seconds > 0:
            m, s = divmod(seconds, 60)
            sys.stdout.write(f"\r💤 Đang nghỉ: {m:02d}:{s:02d} (Chờ lượt tiếp theo)     ")
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
        sys.stdout.write("\r" + " " * 60 + "\r") 

    def log(self, msg, type="info"):
        stats = f"[{self.success_count}/{self.total_runs}]"
        if type == "success": print(f"✅ {stats} {msg}")
        elif type == "error": print(f"❌ {stats} {msg}")
        elif type == "warning": print(f"⚠️ {stats} {msg}")

    # --- HỆ THỐNG ---
    def close_chrome(self):
        try:
            subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except: pass

    def open_chrome(self):
        if not self.chrome_exe: return False
        try:
            cmd = f'"{self.chrome_exe}" --headless=new --remote-debugging-port=9222 --user-data-dir="{USER_DATA_DIR}" --profile-directory="{PROFILE_DIR}"'
            subprocess.Popen(cmd, shell=True)
            time.sleep(3) 
            return True
        except: return False

    def connect_browser(self):
        co = ChromiumOptions()
        co.set_local_port(9222)
        try:
            self.page = ChromiumPage(addr_or_opts=co)
            if not self.page.address: self.page = None
            else: self.page.set.timeouts(base=10)
        except: self.page = None

    def rotate_ip_mobile(self):
        sys.stdout.write(f"📱 [{self.success_count}/{self.total_runs + 1}] Đổi IP... ")
        sys.stdout.flush()
        try:
            d = u2.connect()
            if d(textContains="Tắt").exists: d(textContains="Tắt").click()
            elif d(textContains="máy bay").exists: d(textContains="máy bay").click()
            time.sleep(5) 
            if d(textContains="Bật").exists: d(textContains="Bật").click()
            elif d(textContains="máy bay").exists: d(textContains="máy bay").click()
            
            for _ in range(20):
                try:
                    subprocess.check_call(["ping", "-n", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("-> OK")
                    return
                except: time.sleep(1)
            print("-> Mất mạng!")
        except: 
            print("-> Lỗi ĐT")

    def generate_natural_profile(self):
        ho = random.choice(HO)
        dem = random.choice(DEM)
        ten = random.choice(TEN)
        
        style = random.choice([1, 2, 3, 4, 5])
        if style == 1: raw_name = f"{ho}{dem}{ten}"
        elif style == 2:
            if random.choice([True, False]): raw_name = f"{random.choice(NICK_PREFIX)}{ten}"
            else: raw_name = f"{ten}{random.choice(NICK_SUFFIX)}"
        elif style == 3: raw_name = f"{ten}{random.randint(1995, 2005)}"
        elif style == 4: raw_name = f"{ten}{ho}{random.randint(1, 999)}"
        else: raw_name = f"{ten}{ten}"

        username = raw_name.lower()
        if random.choice([True, False]): email_user = f"{ten}{ho}{random.randint(10,999)}".lower()
        else: email_user = username
            
        email = f"{email_user}@gmail.com"
        pwd = "Aa1" + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))
        return username, email, pwd

    def giai_captcha(self, img_bytes):
        try:
            if not img_bytes: return None
            res = self.ocr.classification(img_bytes)
            if res: res = res.replace("o", "0").replace("O", "0").replace(" ", "")
            return res
        except: return None

    def check_ip_limit(self):
        if self.page.ele('text:There has already been registration', timeout=3):
            return True
        return False

    def check_turnstile(self):
        try:
            iframe = self.page.ele('xpath://iframe[contains(@src, "challenges.cloudflare.com")]')
            if iframe:
                time.sleep(2) 
                iframe.click()
                time.sleep(3) 
        except: pass

    def save_account(self, username, password, email):
        with open(ACCOUNT_FILE, "a") as f:
            f.write(f"{username}|{password}|{email}\n")
        self.success_count += 1
        self.log(f"THÀNH CÔNG: {username}", "success")

    # --- TRẢ VỀ TRUE/FALSE ĐỂ BIẾT CÓ CẦN RETRY KHÔNG ---
    def run_cycle(self):
        self.total_runs += 1
        self.close_chrome()
        self.rotate_ip_mobile()
        
        if not self.open_chrome(): return False
        self.connect_browser()
        if not self.page: return False

        try:
            try: self.page.run_cdp('Network.clearBrowserCookies')
            except: pass

            self.page.get(TARGET_URL)
            
            if self.page.ele('text:Create an account', timeout=5):
                self.page.ele('text:Create an account').click()
            
            if not self.page.wait.ele_displayed('xpath:/html/body/div/div[2]/div[2]/div/form/div[1]/input', timeout=10):
                self.log("Lỗi load Form", "warning")
                return False # Lỗi -> Trả về False
            
            user, email, pwd = self.generate_natural_profile()
            
            self.page.ele('xpath:/html/body/div/div[2]/div[2]/div/form/div[1]/input').input(user)
            self.page.ele('xpath:/html/body/div/div[2]/div[2]/div/form/div[2]/input').input(email)
            self.page.ele('xpath:/html/body/div/div[2]/div[2]/div/form/div[3]/input').input(pwd)

            img_ele = self.page.ele('xpath:/html/body/div/div[2]/div[2]/div/form/div[4]/img')
            inp_ele = self.page.ele('xpath:/html/body/div/div[2]/div[2]/div/form/div[4]/input')
            
            final_code = ""
            for i in range(3):
                img_bytes = img_ele.get_screenshot(as_bytes='png')
                code = self.giai_captcha(img_bytes)
                if code and len(code) == 4 and code.isdigit():
                    final_code = code
                    break
                else:
                    inp_ele.clear()
                    time.sleep(0.5)

            if final_code:
                inp_ele.input(final_code)
                self.check_turnstile()
                
                try:
                    submit_btn = self.page.ele('@name=sub_reg')
                    if submit_btn: submit_btn.click()
                    else:
                        self.page.actions.key_down('ENTER')
                        self.page.actions.key_up('ENTER')
                except: pass

                time.sleep(2)
                
                if self.check_ip_limit():
                    self.log("Trùng IP (Limit Reached)", "error")
                    return False # Lỗi IP -> Trả về False để retry ngay

                alert_text = self.page.handle_alert(timeout=3)
                if alert_text:
                    self.log(f"Lỗi Web: {alert_text}", "error")
                    return False # Lỗi Popup -> Trả về False

                time.sleep(8) 
                
                # Click nút phụ ngầm
                try:
                    if self.page.ele('xpath:/html/body/div/div[3]/div[2]/div[3]/form/button', timeout=3):
                        self.page.ele('xpath:/html/body/div/div[3]/div[2]/div[3]/form/button').click()
                        time.sleep(1)
                except: pass
                
                try:
                    self.page.scroll.to_bottom() 
                    if self.page.ele('xpath:/html/body/div/div[3]/div[13]/div[4]/form/button', timeout=3):
                        self.page.ele('xpath:/html/body/div/div[3]/div[13]/div[4]/form/button').click()
                except: pass

                self.save_account(user, pwd, email)
                return True # THÀNH CÔNG -> Trả về True
            else:
                self.log("Lỗi Captcha", "warning")
                return False # Lỗi Captcha -> Trả về False

        except Exception as e:
            return False # Lỗi Runtime -> Trả về False
        finally:
            self.close_chrome()

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=========================================")
    print("   GAMETY REG TOOL - FINAL V4 (RETRY)    ")
    print("=========================================")
    
    bot = GametyAutoReg()
    
    while True:
        # Chạy và lấy kết quả (True/False)
        is_success = bot.run_cycle()
        
        if is_success:
            # Nếu thành công -> Nghỉ ngơi
            delay = random.randint(60, 155)
            bot.countdown_timer(delay)
        else:
            # Nếu thất bại (False) -> In thông báo và chạy lại ngay (Bỏ qua delay)
            print("⚠️ Gặp lỗi -> Thử lại ngay lập tức (Skip delay)...")
