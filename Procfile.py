import telebot, random, time, sqlite3, os, re, json, requests
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from threading import Thread, Lock
from webdriver_manager.chrome import ChromeDriverManager

# [1] إعدادات المنظومة
BOT_TOKEN = "6193186034:AAHpKPAGwUPi3Jr7-Uv4f5Sz-gmY8tH8bNI"

# إعداد جلسة اتصال قوية لتجنب الـ Timeout
session = requests.Session()
session.proxies = {} # التأكد من عدم وجود بروكسي معطل

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

def init_db():
    conn = sqlite3.connect('army_windows.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS army 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, pwd TEXT, 
         cookies TEXT, status TEXT DEFAULT 'ACTIVE')''')
    conn.commit(); conn.close()

init_db()

class WindowsEngine:
    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        # إذا أردت رؤية ما يحدث، اترك السطر التالي معطلاً
        # options.add_argument("--headless=new") 
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", fix_hairline=True)
            return driver
        except Exception as e:
            print(f"❌ خطأ المتصفح: {e}"); return None

    def recruit(self, chat_id):
        bot.send_message(chat_id, "🚀 **بدأ الهجوم.. سيفتح المتصفح الآن!**")
        driver = self.get_driver()
        if not driver: return
        
        try:
            driver.get("https://www.1secmail.com/")
            time.sleep(5)
            email = driver.find_element(By.ID, "item-to-copy").get_attribute("value")
            bot.send_message(chat_id, f"📧 تم سحب الإيميل: `{email}`")
            # اترك المتصفح مفتوحاً لترى النتيجة
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ حدث خطأ: {e}")

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 ابدأ التجنيد فوراً", callback_data="run"))
    bot.send_message(m.chat.id, "🔱 **APOCALYPSE WINDOWS V1**\nالمنظومة جاهزة للعمل على جهازك الأساسي.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "run":
        Thread(target=WindowsEngine().recruit, args=(call.message.chat.id,)).start()

# [السر هنا لتجاوز الخطأ الذي ظهر لك]
if __name__ == "__main__":
    print("📡 جاري تخطي حواجز الشبكة...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=90)
        except Exception as e:
            print(f"🔄 إعادة محاولة الاتصال... ({e})")
            time.sleep(5)
