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
        """المحرك المصفح لبيئة كالي"""
        options = webdriver.ChromeOptions()
        options.binary_location = "/usr/bin/chromium"
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/120.0.0.0 Safari/537.36")
        
        try:
            os.system("pkill -f chromium")
            os.system("pkill -f chromedriver")
            service = Service(executable_path="/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)
            stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", fix_hairline=True)
            return driver
        except: return None

    def warm_up_soldier(self, driver, chat_id, mid):
        """تدفئة الحساب لرفع الموثوقية"""
        try:
            self.update_log(chat_id, mid, 90, "🛡️ تدفئة (متابعة Cristiano)...")
            driver.get("https://www.instagram.com/cristiano/")
            time.sleep(7)
            follow_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Follow')] | //div[text()='Follow']")))
            driver.execute_script("arguments[0].click();", follow_btn)
            time.sleep(3)
        except: pass

    def recruit(self, chat_id):
        """عملية إنشاء حساب جديد"""
        status_msg = bot.send_message(chat_id, "🚀 **بدء التجنيد...**")
        mid = status_msg.message_id
        driver = self.get_driver()
        if not driver:
            bot.edit_message_text("❌ انهار المحرك! تأكد من تشغيل Tor.", chat_id, mid)
            return

        try:
            # 1. جلب البريد
            driver.get("https://www.1secmail.com/")
            email = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "item-to-copy"))).get_attribute("value")
            
            # 2. التسجيل في إنستغرام
            driver.execute_script("window.open('https://www.instagram.com/accounts/emailsignup/', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            self.update_log(chat_id, mid, 40, f"تسجيل ببريد: {email}")
            
            user = f"kali_{random.randint(10,99)}_{os.urandom(2).hex()}"
            pwd = f"K_Kali_{random.randint(1000,9999)}!"
            
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
            driver.find_element(By.NAME, "fullName").send_keys("Kali Agent")
            driver.find_element(By.NAME, "username").send_keys(user)
            driver.find_element(By.NAME, "password").send_keys(pwd)
            time.sleep(2); driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # تخطي الميلاد
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//select[@title='Year:']"))).send_keys("1996")
                driver.find_element(By.XPATH, "//button[text()='Next']").click()
            except: pass

            # 3. جلب OTP
            otp = None
            driver.switch_to.window(driver.window_handles[0])
            for _ in range(12):
                driver.refresh(); time.sleep(10)
                if "Instagram" in driver.page_source:
                    driver.find_element(By.PARTIAL_LINK_TEXT, "Instagram").click()
                    otp = re.findall(r'\b\d{6}\b', driver.page_source)[0]
                    break

            if otp:
                driver.switch_to.window(driver.window_handles[1])
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email_confirmation_code"))).send_keys(otp)
                driver.find_element(By.XPATH, "//button[text()='Next']").click()
                time.sleep(10)
                self.warm_up_soldier(driver, chat_id, mid)
                
                # حفظ البيانات والكوكيز
                cookies = json.dumps(driver.get_cookies())
                with db_lock:
                    conn = sqlite3.connect('kali_army_v4.db')
                    conn.execute("INSERT INTO army (user, pwd, cookies, created_at) VALUES (?, ?, ?, ?)", 
                                 (user, pwd, cookies, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit(); conn.close()
                self.update_log(chat_id, mid, 100, f"✅ تم التجنيد: `{user}`")
            else: bot.edit_message_text("❌ لم يصل الكود.", chat_id, mid)
        except Exception as e: bot.send_message(chat_id, f"⚠️ خطأ: {str(e)[:50]}")
        finally: driver.quit()

    def attack_target(self, chat_id, target_username):
        """نظام الرشق باستخدام الجنود المخزنين"""
        status_msg = bot.send_message(chat_id, f"🎯 **بدء الهجوم على: {target_username}**")
        mid = status_msg.message_id
        
        conn = sqlite3.connect('kali_army_v4.db')
        soldiers = conn.execute("SELECT user, cookies FROM army WHERE status='ACTIVE'").fetchall()
        conn.close()

        if not soldiers:
            bot.edit_message_text("⚠️ القاعدة فارغة! جند أولاً.", chat_id, mid); return

        success = 0
        for user, cookies_json in soldiers:
            driver = self.get_driver()
            try:
                driver.get("https://www.instagram.com/")
                for cookie in json.loads(cookies_json): driver.add_cookie(cookie)
                driver.refresh(); time.sleep(5)
                driver.get(f"https://www.instagram.com/{target_username}/")
                btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Follow')] | //div[text()='Follow']")))
                driver.execute_script("arguments[0].click();", btn)
                success += 1
                self.update_log(chat_id, mid, int((success/len(soldiers))*100), f"رشق بواسطة: {user}")
            except: pass
            finally: driver.quit(); time.sleep(random.randint(5, 10))
        bot.send_message(chat_id, f"✅ تم الرشق بنجاح: {success} متابع.")

    def update_log(self, chat_id, mid, percent, status):
        bar = "▓" * (percent // 10) + "░" * (10 - (percent // 10))
        text = f"💀 **KALI SYSTEM V70**\n\n{bar} {percent}%\n📍 {status}"
        try: bot.edit_message_text(text, chat_id, mid, parse_mode="Markdown")
        except: pass

# [الواجهة والتحكم]
@bot.message_handler(commands=['start'])
def main(m):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🚀 تجنيد جندي جديد", callback_data="mass"),
               types.InlineKeyboardButton("🎯 إطلاق رشق (هجوم)", callback_data="attack"),
               types.InlineKeyboardButton("📊 عرض الجيش", callback_data="db"))
    bot.send_message(m.chat.id, "🔱 **APOCALYPSE CONTROL CENTER**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    engine = KaliEngine()
    if call.data == "mass": Thread(target=engine.recruit, args=(call.message.chat.id,)).start()
    elif call.data == "db":
        conn = sqlite3.connect('kali_army_v4.db')
        count = conn.execute("SELECT COUNT(*) FROM army").fetchone()[0]
        bot.answer_callback_query(call.id, f"جيشك يتكون من {count} جندي.", show_alert=True); conn.close()
    elif call.data == "attack":
        msg = bot.send_message(call.message.chat.id, "🎯 أرسل يوزر الضحية (بدون @):")
        bot.register_next_step_handler(msg, lambda m: Thread(target=engine.attack_target, args=(m.chat.id, m.text)).start())

bot.infinity_polling()
