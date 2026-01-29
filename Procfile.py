import telebot, random, time, sqlite3, os, re, json
from telebot import types, apihelper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread, Lock
from webdriver_manager.chrome import ChromeDriverManager

# [1] الإعدادات الأساسية
BOT_TOKEN = "6193186034:AAHpKPAGwUPi3Jr7-Uv4f5Sz-gmY8tH8bNI"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

class WindowsEngine:
    def update_status(self, chat_id, mid, percent, status_text):
        """تحديث شريط التقدم والنسبة المئوية"""
        bar = "▓" * (percent // 10) + "░" * (10 - (percent // 10))
        text = f"🛡️ **رادار التجنيد العملياتي**\n\n" \
               f"📊 التقدم: {percent}%\n" \
               f"[{bar}]\n" \
               f"📍 الحالة: {status_text}"
        try:
            bot.edit_message_text(text, chat_id, mid, parse_mode="Markdown")
        except: pass

    def capture_error(self, driver, chat_id, stage_name, error_msg):
        """تصوير الشاشة عند حدوث أي خلل لإظهار مكان التوقف"""
        try:
            filename = f"crash_{stage_name}.png"
            driver.save_screenshot(filename)
            with open(filename, 'rb') as photo:
                bot.send_photo(chat_id, photo, 
                               caption=f"⚠️ **توقف النظام!**\n\n"
                                       f"📍 المرحلة: {stage_name}\n"
                                       f"❌ الخطأ: `{error_msg[:100]}`", 
                               parse_mode="Markdown")
            os.remove(filename)
        except: pass

    def get_driver(self):
        # تنظيف العمليات لضمان عدم التجميد
        os.system("taskkill /f /im chrome.exe /t >nul 2>&1")
        os.system("taskkill /f /im chromedriver.exe /t >nul 2>&1")
        
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        # عطلنا الـ headless لكي ترى ما يحدث
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(60)
            return driver
        except: return None

    def recruit(self, chat_id):
        status_msg = bot.send_message(chat_id, "📡 جاري بدء المحرك...")
        mid = status_msg.message_id
        
        driver = self.get_driver()
        if not driver:
            bot.edit_message_text("❌ فشل تشغيل المتصفح كلياً!", chat_id, mid)
            return

        try:
            # المرحلة 1 (10%)
            self.update_status(chat_id, mid, 10, "فتح موقع الإيميلات المؤقتة...")
            driver.get("https://www.1secmail.com/")
            
            # المرحلة 2 (30%)
            self.update_status(chat_id, mid, 30, "جاري استخراج الإيميل...")
            wait = WebDriverWait(driver, 45)
            email_field = wait.until(EC.visibility_of_element_located((By.ID, "item-to-copy")))
            email = email_field.get_attribute("value")
            
            # المرحلة 3 (50%)
            self.update_status(chat_id, mid, 50, f"تم جلب الإيميل: {email}\nفتح إنستغرام...")
            driver.execute_script("window.open('https://www.instagram.com/accounts/emailsignup/', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get("https://www.instagram.com/accounts/emailsignup/")

            # المرحلة 4 (70%)
            self.update_status(chat_id, mid, 70, "جاري ملء بيانات الحساب...")
            user = f"kali_{random.randint(10,99)}_{os.urandom(2).hex()}"
            pwd = f"K_Army_{random.randint(100,999)}!"
            
            wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
            driver.find_element(By.NAME, "fullName").send_keys("Kali Soldier")
            driver.find_element(By.NAME, "username").send_keys(user)
            driver.find_element(By.NAME, "password").send_keys(pwd)
            
            # المرحلة 5 (90%)
            self.update_status(chat_id, mid, 90, "الضغط على زر التسجيل...")
            time.sleep(2)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # المرحلة النهائية (100%)
            time.sleep(10)
            self.update_status(chat_id, mid, 100, f"✅ اكتملت المرحلة الأولى!\nاليوزر: `{user}`")

        except Exception as e:
            stage = "غير معروفة"
            # محاولة تحديد المرحلة التي وقف عندها
            if "1secmail" in driver.current_url: stage = "جلب الإيميل"
            elif "instagram" in driver.current_url: stage = "تسجيل إنستغرام"
            
            self.capture_error(driver, chat_id, stage, str(e))
            self.update_status(chat_id, mid, 0, f"❌ حدث خلل في مرحلة: {stage}")
        
        finally:
            print("العملية انتهت.")
            # اترك المتصفح مفتوحاً لكي تراجع الخطأ بنفسك في اللابتوب

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 بدء التجنيد والمراقبة", callback_data="run"))
    bot.send_message(m.chat.id, "🔱 **APOCALYPSE SYSTEM V100**\n\nنظام الرصد والمتابعة بنسبة مئوية جاهز.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == "run":
        Thread(target=WindowsEngine().recruit, args=(call.message.chat.id,)).start()

if __name__ == "__main__":
    print("📡 المنظومة تعمل الآن.. راقب تليجرام.")
    bot.infinity_polling()
