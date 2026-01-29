import telebot, random, time, sqlite3, os, re, json
from telebot import types, apihelper
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from threading import Thread

# [1] إعدادات البوت
BOT_TOKEN = "6193186034:AAHpKPAGwUPi3Jr7-Uv4f5Sz-gmY8tH8bNI"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

class WindowsRadar:
    def update_status(self, chat_id, mid, percent, status_text):
        """تحديث التقدم والنسبة المئوية"""
        bar = "▓" * (percent // 10) + "░" * (10 - (percent // 10))
        text = f"📡 **رادار التجنيد (محرك Edge)**\n\n" \
               f"📊 الإنجاز: {percent}%\n" \
               f"[{bar}]\n" \
               f"📍 الحالة: {status_text}"
        try: bot.edit_message_text(text, chat_id, mid, parse_mode="Markdown")
        except: pass

    def capture_crash(self, driver, chat_id, stage, error):
        """تصوير الشاشة فوراً عند حدوث خلل"""
        try:
            filename = f"crash_report.png"
            driver.save_screenshot(filename)
            with open(filename, 'rb') as photo:
                bot.send_photo(chat_id, photo, 
                               caption=f"⚠️ **تقرير تعطل النظام**\n\n"
                                       f"🔍 المرحلة: {stage}\n"
                                       f"🚫 الخلل: `{str(error)[:100]}`")
            os.remove(filename)
        except: pass

    def get_driver(self):
        """تنظيف الذاكرة وتشغيل محرك Edge"""
        os.system("taskkill /f /im msedge.exe /t >nul 2>&1")
        os.system("taskkill /f /im msedgedriver.exe /t >nul 2>&1")
        
        edge_options = Options()
        edge_options.add_argument("--start-maximized")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            service = Service(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=edge_options)
            return driver
        except Exception as e:
            print(f"Driver Error: {e}"); return None

    def start_mission(self, chat_id):
        msg = bot.send_message(chat_id, "📡 جاري تفعيل الرادار ومحرك Edge...")
        mid = msg.message_id
        
        driver = self.get_driver()
        if not driver:
            bot.edit_message_text("❌ فشل تشغيل Edge. تأكد من إغلاق المتصفح يدوياً.", chat_id, mid)
            return

        try:
            # 20% - سحب الإيميل
            self.update_status(chat_id, mid, 20, "سحب بيانات الإيميل المؤقت...")
            driver.get("https://www.1secmail.com/")
            wait = WebDriverWait(driver, 40)
            email = wait.until(EC.presence_of_element_located((By.ID, "item-to-copy"))).get_attribute("value")
            
            # 50% - الدخول لإنستغرام
            self.update_status(chat_id, mid, 50, f"تم جلب {email}\nفتح بوابة إنستغرام...")
            driver.execute_script("window.open('https://www.instagram.com/accounts/emailsignup/', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get("https://www.instagram.com/accounts/emailsignup/")

            # 80% - كتابة البيانات
            self.update_status(chat_id, mid, 80, "تغذية البيانات (يوزر/باسورد)...")
            user = f"edge_agent_{random.randint(10,99)}_{os.urandom(2).hex()}"
            pwd = f"Edge_Pass_{random.randint(1000,9999)}!"
            
            wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
            driver.find_element(By.NAME, "fullName").send_keys("Edge Automated")
            driver.find_element(By.NAME, "username").send_keys(user)
            driver.find_element(By.NAME, "password").send_keys(pwd)
            
            # 100% - التسجيل
            time.sleep(2)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            self.update_status(chat_id, mid, 100, f"✅ تمت العملية!\nاليوزر: `{user}`")

        except Exception as e:
            self.capture_crash(driver, chat_id, "تحليل البيانات", e)
            self.update_status(chat_id, mid, 0, "❌ تعطل النظام - راجع التقرير المصور")
        finally:
            print("Finished.")

@bot.message_handler(commands=['start'])
def start_bot(m):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🚀 إطلاق التجنيد (Edge Mode)", callback_data="run"))
    bot.send_message(m.chat.id, "🔱 **APOCALYPSE V120 - EDGE ENGINE**", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "run":
        Thread(target=WindowsRadar().start_mission, args=(call.message.chat.id,)).start()

print("📡 الرادار يعمل الآن.. جرب في تليجرام")
bot.infinity_polling()
