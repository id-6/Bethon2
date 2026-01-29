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

# [1] إعدادات المنظومة القتالية
BOT_TOKEN = "6193186034:AAHpKPAGwUPi3Jr7-Uv4f5Sz-gmY8tH8bNI"
bot = telebot.TeleBot(BOT_TOKEN)
db_lock = Lock()

def init_db():
    with db_lock:
        conn = sqlite3.connect('kali_army_v4.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS army 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, pwd TEXT, 
             cookies TEXT, status TEXT DEFAULT 'ACTIVE', created_at TEXT)''')
        conn.commit()
        conn.close()

init_db()

class KaliEngine:
    def get_driver(self):
        """إنشاء متصفح مع صمام أمان للبروكسي"""
        options = webdriver.ChromeOptions()
        # إعدادات البروكسي الصارمة لـ Tor
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # تجاوز أخطاء الاتصال بالبروكسي في كالي
        options.add_argument("--proxy-bypass-list=<-loopback>")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(f"user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        
        try:
            driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", fix_hairline=True)
            return driver
        except Exception as e:
            print(f"DEBUG: Proxy/Driver Error: {e}")
            return None

    def warm_up_soldier(self, driver, chat_id, mid):
        """تدفئة الحساب لرفع الموثوقية (متابعة Cristiano)"""
        try:
            self.update_log(chat_id, mid, 90, "🛡️ جاري التدفئة (تجنب الحظر)...")
            driver.get("https://www.instagram.com/cristiano/")
            time.sleep(6)
            
            # محاولة الضغط على زر المتابعة بمختلف الصيغ
            follow_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Follow')] | //div[text()='Follow']")))
            driver.execute_script("arguments[0].click();", follow_btn)
            
            # محاكاة نشاط بشري (Scrolling)
            driver.execute_script("window.scrollTo(0, 700);")
            time.sleep(3)
            return True
        except:
            return False

    def recruit(self, chat_id):
        status_msg = bot.send_message(chat_id, "🌑 **بدء عملية التجنيد السيبرانية...**")
        mid = status_msg.message_id
        driver = None
        
        try:
            driver = self.get_driver()
            if not driver:
                bot.edit_message_text("❌ فشل البروكسي! تأكد من تشغيل Tor عبر: `sudo systemctl restart tor`", chat_id, mid)
                return

            wait = WebDriverWait(driver, 50)

            # 1. جلب البريد
            self.update_log(chat_id, mid, 20, "توليد بريد سيبراني...")
            driver.get("https://www.1secmail.com/")
            wait.until(EC.visibility_of_element_located((By.ID, "item-to-copy")))
            email = driver.find_element(By.ID, "item-to-copy").get_attribute("value")
            
            # 2. تسجيل إنستغرام
            driver.execute_script("window.open('https://www.instagram.com/accounts/emailsignup/', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            self.update_log(chat_id, mid, 40, f"محاولة التسجيل بـ: `{email}`")
            
            wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
            user = f"v_army_{random.randint(100,999)}_{os.urandom(2).hex()}"
            pwd = f"K_Pass_{random.randint(1000,9999)}!"
            
            driver.find_element(By.NAME, "fullName").send_keys("Ghost Agent")
            driver.find_element(By.NAME, "username").send_keys(user)
            driver.find_element(By.NAME, "password").send_keys(pwd)
            time.sleep(2)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # تخطي الميلاد
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//select[@title='Year:']"))).send_keys("1998")
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
                time.sleep(3)
                driver.find_element(By.XPATH, "//button[text()='Next']").click()
                time.sleep(8) 

                # --- التدفئة الإلزامية ---
                self.warm_up_soldier(driver, chat_id, mid)
                
                # حفظ البيانات والكوكيز
                cookies = json.dumps(driver.get_cookies())
                with db_lock:
                    conn = sqlite3.connect('kali_army_v4.db')
                    conn.execute("INSERT INTO army (user, pwd, cookies, created_at) VALUES (?, ?, ?, ?)", 
                                 (user, pwd, cookies, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    conn.close()
                
                self.update_log(chat_id, mid, 100, f"✅ تم الحفظ والتدفئة: `{user}`")
            else:
                bot.edit_message_text("❌ لم يتم استلام كود OTP. (تور بطيء جداً)", chat_id, mid)

        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطأ غير متوقع: {str(e)[:100]}")
        finally:
            if driver: driver.quit()

    def update_log(self, chat_id, mid, percent, status):
        bar = "▓" * (percent // 10) + "░" * (10 - (percent // 10))
        text = f"🔥 **OVERLORD KALI EDITION**\n\n{bar} {percent}%\n📍 {status}"
        try: bot.edit_message_text(text, chat_id, mid, parse_mode="Markdown")
        except: pass

# [واجهة التحكم]
@bot.message_handler(commands=['start'])
def main_panel(m):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🚀 تجنيد جندي جاهز للرشق", callback_data="mass"),
               types.InlineKeyboardButton("📊 إحصائيات الجيش", callback_data="db"))
    bot.send_message(m.chat.id, "🔱 **مركز إدارة مشروع الرشق**\nالنظام مجهز بصمامات أمان للبروكسي وتدفئة تلقائية.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_actions(call):
    if call.data == "mass":
        Thread(target=KaliEngine().recruit, args=(call.message.chat.id,)).start()
    elif call.data == "db":
        conn = sqlite3.connect('kali_army_v4.db')
        count = conn.execute("SELECT COUNT(*) FROM army").fetchone()[0]
        bot.answer_callback_query(call.id, f"لديك {count} جندي في القاعدة.", show_alert=True)
        conn.close()

bot.infinity_polling()
