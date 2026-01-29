import telebot, requests, random, time, sqlite3, os, re, shutil, json
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from threading import Thread, Lock
from datetime import datetime

# [1] إعدادات المنظومة
BOT_TOKEN = "6193186034:AAHpKPAGwUPi3Jr7-Uv4f5Sz-gmY8tH8bNI"
bot = telebot.TeleBot(BOT_TOKEN)
db_lock = Lock()

class KaliEngine:
    def get_driver(self):
        """إعدادات قتالية لمنع انهيار المتصفح في كالي"""
        options = webdriver.ChromeOptions()
        
        # --- حل مشكلة Stacktrace والانهيار ---
        options.add_argument("--no-sandbox") # ضروري جداً لمستخدم Root
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        
        # --- إعدادات البروكسي (Tor) ---
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        options.add_argument("--ignore-certificate-errors")
        
        # --- تمويه المتصفح ---
        options.add_argument(f"user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"
            binary_path = shutil.which("chromium") or "/usr/bin/chromium"
            options.binary_location = binary_path
            
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            
            # منع التعليق (Timeouts)
            driver.set_page_load_timeout(90)
            
            stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", fix_hairline=True)
            return driver
        except Exception as e:
            print(f"❌ خطأ في بدء المحرك: {e}")
            return None

    def warm_up_soldier(self, driver, chat_id, mid):
        """تدفئة الحساب (متابعة Cristiano)"""
        try:
            self.update_log(chat_id, mid, 90, "🛡️ تدفئة الحساب (تجاوز الحظر)...")
            driver.get("https://www.instagram.com/cristiano/")
            time.sleep(7)
            follow_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Follow')] | //div[text()='Follow']")))
            driver.execute_script("arguments[0].click();", follow_btn)
            time.sleep(3)
            return True
        except: return False

    def recruit(self, chat_id):
        status_msg = bot.send_message(chat_id, "🚀 **جاري تشغيل المحرك في كالي...**")
        mid = status_msg.message_id
        driver = None
        
        try:
            driver = self.get_driver()
            if not driver:
                bot.edit_message_text("❌ المحرك انهار! تأكد من تثبيت chromium-driver", chat_id, mid)
                return

            wait = WebDriverWait(driver, 50)
            # 1. جلب البريد
            self.update_log(chat_id, mid, 20, "سحب إيميل مؤقت...")
            driver.get("https://www.1secmail.com/")
            wait.until(EC.visibility_of_element_located((By.ID, "item-to-copy")))
            email = driver.find_element(By.ID, "item-to-copy").get_attribute("value")
            
            # 2. تسجيل إنستغرام
            driver.execute_script("window.open('https://www.instagram.com/accounts/emailsignup/', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            self.update_log(chat_id, mid, 40, f"تجنيد بـ: {email}")
            
            wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
            user = f"v_army_{random.randint(100,999)}_{os.urandom(2).hex()}"
            pwd = f"K_Kali_{random.randint(1000,9999)}!"
            
            driver.find_element(By.NAME, "fullName").send_keys("Kali Ghost")
            driver.find_element(By.NAME, "username").send_keys(user)
            driver.find_element(By.NAME, "password").send_keys(pwd)
            time.sleep(3)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # تخطي الميلاد
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//select[@title='Year:']"))).send_keys("1995")
                driver.find_element(By.XPATH, "//button[text()='Next']").click()
            except: pass

            # 3. جلب OTP
            otp = None
            driver.switch_to.window(driver.window_handles[0])
            for _ in range(12):
                driver.refresh()
                time.sleep(10)
                if "Instagram" in driver.page_source:
                    driver.find_element(By.PARTIAL_LINK_TEXT, "Instagram").click()
                    time.sleep(3)
                    otp = re.findall(r'\b\d{6}\b', driver.page_source)[0]
                    break

            if otp:
                driver.switch_to.window(driver.window_handles[1])
                wait.until(EC.presence_of_element_located((By.NAME, "email_confirmation_code"))).send_keys(otp)
                time.sleep(2)
                driver.find_element(By.XPATH, "//button[text()='Next']").click()
                time.sleep(10)

                self.warm_up_soldier(driver, chat_id, mid)
                
                # حفظ البيانات
                with db_lock:
                    conn = sqlite3.connect('kali_army_v4.db')
                    conn.execute("INSERT INTO army (user, pwd, created_at) VALUES (?, ?, ?)", 
                                 (user, pwd, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    conn.close()
                
                self.update_log(chat_id, mid, 100, f"✅ تم بنجاح: `{user}`")
            else:
                bot.edit_message_text("❌ لم يصل الكود (تور بطيء).", chat_id, mid)

        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطأ: {str(e)[:50]}")
        finally:
            if driver: driver.quit()

    def update_log(self, chat_id, mid, percent, status):
        bar = "▓" * (percent // 10) + "░" * (10 - (percent // 10))
        text = f"💀 **KALI OVERLORD V55**\n\n{bar} {percent}%\n📍 {status}"
        try: bot.edit_message_text(text, chat_id, mid, parse_mode="Markdown")
        except: pass

# [الواجهة]
@bot.message_handler(commands=['start'])
def main(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 تجنيد حساب (Kali Special)", callback_data="run"))
    bot.send_message(m.chat.id, "🔱 **نظام الرشق - نسخة كالي المستقرة**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def btn(call):
    if call.data == "run":
        Thread(target=KaliEngine().recruit, args=(call.message.chat.id,)).start()

bot.infinity_polling()
