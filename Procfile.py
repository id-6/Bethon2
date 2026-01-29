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

# [1] إعدادات المنظومة - تأكد من التوكن الخاص بك
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
        """محرك ويندوز - تم تعطيل البروكسي لتجنب أخطاء الاتصال"""
        options = webdriver.ChromeOptions()
        
        # خيارات التشغيل المستقر
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        # ملاحظة: إذا أردت إخفاء المتصفح لاحقاً، فعل السطر التالي:
        # options.add_argument("--headless=new") 
        
        try:
            # تحميل التعريف المناسب لكروم ويندوز تلقائياً
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # تمويه المتصفح
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
            return driver
        except Exception as e:
            print(f"❌ خطأ في تشغيل المتصفح: {e}")
            return None

    def recruit(self, chat_id):
        status_msg = bot.send_message(chat_id, "🚀 **بدء عملية التجنيد (Windows Mode)...**")
        mid = status_msg.message_id
        driver = self.get_driver()
        
        if not driver:
            bot.edit_message_text("❌ فشل تشغيل المحرك. تأكد من إغلاق أي متصفح كروم مفتوح بواسطة سكريبت قديم.", chat_id, mid)
            return

        try:
            # 1. جلب الإيميل المؤقت
            driver.get("https://www.1secmail.com/")
            wait = WebDriverWait(driver, 40)
            email = wait.until(EC.visibility_of_element_located((By.ID, "item-to-copy"))).get_attribute("value")
            
            self.update_log(chat_id, mid, 30, f"تم سحب إيميل: `{email}`")

            # 2. فتح إنستغرام في نافذة جديدة
            driver.execute_script("window.open('https://www.instagram.com/accounts/emailsignup/', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            
            user = f"win_{random.randint(10,99)}_{os.urandom(2).hex()}"
            pwd = f"Pass_{random.randint(1000,9999)}!X"
            
            self.update_log(chat_id, mid, 50, "إدخال البيانات في إنستغرام...")
            
            wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
            driver.find_element(By.NAME, "fullName").send_keys("Agent Windows")
            driver.find_element(By.NAME, "username").send_keys(user)
            driver.find_element(By.NAME, "password").send_keys(pwd)
            time.sleep(2)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # 3. إكمال الخطوات (التاريخ والـ OTP)
            # ملاحظة: هنا سيتوقف المتصفح لترى ماذا يحدث أمامك
            bot.send_message(chat_id, f"📡 **الآن المتصفح مفتوح أمامك!**\nتابع عملية إدخال الكود يدوياً أو برمجياً.\nيوزر: `{user}`\nباسورد: `{pwd}`")

        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطأ أثناء العمل: {str(e)[:100]}")
        # لا تغلق المتصفح (driver.quit) حالياً لكي ترى النتيجة

    def update_log(self, chat_id, mid, percent, status):
        bar = "▓" * (percent // 10) + "░" * (10 - (percent // 10))
        text = f"🛡️ **KALI-WIN SYSTEM**\n\n{bar} {percent}%\n📍 {status}"
        try: bot.edit_message_text(text, chat_id, mid, parse_mode="Markdown")
        except: pass

@bot.message_handler(commands=['start'])
def start_cmd(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 بدء التجنيد", callback_data="run"))
    bot.send_message(m.chat.id, "🔱 **نظام الرشق - نسخة ويندوز المباشرة**\nاضغط الزر لبدء تشغيل المتصفح.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "run":
        Thread(target=WindowsEngine().recruit, args=(call.message.chat.id,)).start()

print("✅ البوت يعمل الآن... اذهب لتليجرام وأرسل /start")
bot.infinity_polling()
