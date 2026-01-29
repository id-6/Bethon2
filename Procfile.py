import telebot, random, time, sqlite3, os, re, json
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from threading import Thread, Lock
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# [1] إعدادات المنظومة
BOT_TOKEN = "6193186034:AAHpKPAGwUPi3Jr7-Uv4f5Sz-gmY8tH8bNI"
bot = telebot.TeleBot(BOT_TOKEN)
db_lock = Lock()

def init_db():
    with db_lock:
        conn = sqlite3.connect('army_windows.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS army 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, pwd TEXT, 
             cookies TEXT, status TEXT DEFAULT 'ACTIVE', created_at TEXT)''')
        conn.commit(); conn.close()

init_db()

class WindowsEngine:
    def get_driver(self):
        options = webdriver.ChromeOptions()
        # إذا لم تشغل Tor حالياً، يمكنك تعطيل سطر البروكسي بوضع # قبله
        # options.add_argument('--proxy-server=socks5://127.0.0.1:9050') 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--headless=new") # فعل هذا لاحقاً ليعمل البوت في الخلفية
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", fix_hairline=True)
            return driver
        except Exception as e:
            print(f"Error: {e}"); return None

    def recruit(self, chat_id):
        status_msg = bot.send_message(chat_id, "🚀 **بدء التجنيد على ويندوز...**")
        mid = status_msg.message_id
        driver = self.get_driver()
        if not driver:
            bot.edit_message_text("❌ فشل تشغيل المتصفح.", chat_id, mid); return

        try:
            # 1. جلب الإيميل
            driver.get("https://www.1secmail.com/")
            email = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "item-to-copy"))).get_attribute("value")
            
            # 2. تسجيل إنستغرام
            driver.execute_script("window.open('https://www.instagram.com/accounts/emailsignup/', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            
            user = f"win_{random.randint(10,99)}_{os.urandom(2).hex()}"
            pwd = f"Win_Kali_{random.randint(1000,9999)}!"
            
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
            driver.find_element(By.NAME, "fullName").send_keys("Windows Agent")
            driver.find_element(By.NAME, "username").send_keys(user)
            driver.find_element(By.NAME, "password").send_keys(pwd)
            time.sleep(2); driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # (تكملة خطوات الميلاد و OTP تبقى كما هي في الكود السابق)
            bot.edit_message_text(f"📡 جاري انتظار الكود للإيميل: {email}", chat_id, mid)
            # ... (بقية الكود المعتاد) ...
            
        except Exception as e: bot.send_message(chat_id, f"⚠️ خطأ: {str(e)[:50]}")
        finally: driver.quit()

# [واجهة التحكم]
@bot.message_handler(commands=['start'])
def main(m):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🚀 تجنيد جندي (Windows Mode)", callback_data="run"))
    bot.send_message(m.chat.id, "🔱 **نظام الرشق - نسخة ويندوز المستقرة**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def btn(call):
    if call.data == "run":
        Thread(target=WindowsEngine().recruit, args=(call.message.chat.id,)).start()

bot.infinity_polling()

