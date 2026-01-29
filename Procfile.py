import telebot, requests, random, time, sqlite3, os, re, shutil
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from threading import Thread

# [1] الإعدادات
BOT_TOKEN = "6193186034:AAHpKPAGwUPi3Jr7-Uv4f5Sz-gmY8tH8bNI"
bot = telebot.TeleBot(BOT_TOKEN)

conn = sqlite3.connect('insta_army.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS army (user TEXT, pwd TEXT, status TEXT DEFAULT "READY")')
conn.commit()

class UltimateEngine:
    def create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        chrome_path = shutil.which("chromium") or "/usr/bin/chromium"
        options.binary_location = chrome_path
        driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"
        service = Service(executable_path=driver_path)
        dr = webdriver.Chrome(service=service, options=options)
        stealth(dr, languages=["en-US"], vendor="Google Inc.", platform="Win32", fix_hairline=True)
        return dr

    def update_progress(self, chat_id, msg_id, percent, status):
        bar = "🟦" * (percent // 10) + "⬜" * (10 - (percent // 10))
        text = f"⚙️ **نظام القيادة البصري**\n\n{bar} {percent}%\n📍 الحالة: {status}"
        try: bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown")
        except: pass

    def deploy_soldier(self, chat_id):
        status_msg = bot.send_message(chat_id, "🚀 بدء تجنيد جندي جديد...")
        mid = status_msg.message_id
        driver = None
        try:
            driver = self.create_driver()
            wait = WebDriverWait(driver, 30)

            # --- الخطوة 1: توليد الإيميل بصرياً ---
            self.update_progress(chat_id, mid, 20, "فتح تبويب البريد المؤقت...")
            driver.get("https://www.1secmail.com/")
            time.sleep(5)
            email = driver.execute_script("return document.getElementById('item-to-copy').value")
            
            # --- الخطوة 2: التسجيل في إنستغرام ---
            self.update_progress(chat_id, mid, 40, f"التسجيل بـ: {email}")
            driver.execute_script("window.open('https://www.instagram.com/accounts/emailsignup/', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            
            wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
            user = f"v_army_{random.randint(1000,99999)}"
            pwd = f"King_{random.randint(1000,9999)}!"
            driver.find_element(By.NAME, "fullName").send_keys("Ghost Soldier")
            driver.find_element(By.NAME, "username").send_keys(user)
            driver.find_element(By.NAME, "password").send_keys(pwd)
            
            submit = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            driver.execute_script("arguments[0].click();", submit)
            
            # تخطي تاريخ الميلاد
            try:
                time.sleep(5)
                year = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@title='Year:']")))
                year.send_keys("1997")
                driver.find_element(By.XPATH, "//button[text()='Next']").click()
            except: pass

            # --- الخطوة 3: جلب OTP بصرياً ---
            self.update_progress(chat_id, mid, 70, "العودة للبريد لجلب الكود...")
            otp = None
            driver.switch_to.window(driver.window_handles[0]) # العودة للتبويب الأول (البريد)
            
            for i in range(15):
                driver.refresh()
                time.sleep(8)
                try:
                    # محاولة الضغط على أول رسالة تصل
                    msg_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Instagram")
                    msg_link.click()
                    time.sleep(3)
                    body_text = driver.find_element(By.ID, "messageText").text
                    res = re.findall(r'\b\d{6}\b', body_text)
                    if res: 
                        otp = res[0]
                        break
                except: pass
                self.update_progress(chat_id, mid, 70, f"انتظار OTP (محاولة {i+1}/15)")

            # --- الخطوة 4: تأكيد الحساب ---
            if otp:
                driver.switch_to.window(driver.window_handles[1]) # العودة لإنستغرام
                wait.until(EC.presence_of_element_located((By.NAME, "email_confirmation_code"))).send_keys(otp)
                time.sleep(2)
                driver.find_element(By.XPATH, "//button[text()='Next']").click()
                
                cursor.execute('INSERT INTO army (user, pwd) VALUES (?, ?)', (user, pwd))
                conn.commit()
                self.update_progress(chat_id, mid, 100, f"✅ تم التجنيد: `{user}`")
            else:
                bot.edit_message_text("❌ لم يصل الكود لموقع البريد.", chat_id, mid)

        except Exception as e:
            if driver: driver.save_screenshot("visual_error.png")
            bot.send_photo(chat_id, open("visual_error.png", "rb"), caption=f"⚠️ خلل: {str(e)[:50]}")
        finally:
            if driver: driver.quit()

engine = UltimateEngine()

# --- واجهة الأزرار المائية ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ تجنيد جنود", callback_data="gen_multi"),
        types.InlineKeyboardButton("🎯 إطلاق رشق", callback_data="attack_start"),
        types.InlineKeyboardButton("📊 حالة الجيش", callback_data="status"),
        types.InlineKeyboardButton("📥 تصدير Excel", callback_data="export")
    )
    return markup

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.send_message(m.chat.id, "💀 **OVERLORD V33 - VISUAL ENGINE**\nتحكم بسيرفر الرشق الخاص بك:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "gen_multi":
        msg = bot.send_message(call.message.chat.id, "🔢 كم حساباً تريد إنشاؤه؟")
        bot.register_next_step_handler(msg, process_gen_count)
    elif call.data == "status":
        cursor.execute('SELECT COUNT(*) FROM army')
        count = cursor.fetchone()[0]
        bot.answer_callback_query(call.id, f"الجيش الحالي: {count}")
    elif call.data == "export":
        cursor.execute('SELECT user, pwd FROM army')
        rows = cursor.fetchall()
        with open("army.csv", "w") as f:
            f.write("Username,Password\n")
            for r in rows: f.write(f"{r[0]},{r[1]}\n")
        bot.send_document(call.message.chat.id, open("army.csv", "rb"), caption="🛡️ بيانات الجيش")
    elif call.data == "attack_start":
        bot.send_message(call.message.chat.id, "🎯 أرسل: `/attack [target] [count]`")

def process_gen_count(m):
    try:
        count = int(m.text)
        for _ in range(count):
            Thread(target=engine.deploy_soldier, args=(m.chat.id,)).start()
            time.sleep(5)
    except: bot.send_message(m.chat.id, "⚠️ أرسل رقماً صحيحاً!")

bot.infinity_polling()
