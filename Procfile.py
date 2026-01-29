import telebot, requests, random, time, sqlite3, os, re
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
        options.binary_location = "/usr/bin/chromium"
        service = Service(executable_path="/usr/bin/chromedriver")
        dr = webdriver.Chrome(service=service, options=options)
        stealth(dr, languages=["en-US"], vendor="Google Inc.", platform="Win32", fix_hairline=True)
        return dr

    def update_progress(self, chat_id, msg_id, percent, status):
        bar = "🟦" * (percent // 10) + "⬜" * (10 - (percent // 10))
        text = f"⚙️ **جاري العمل...**\n\n{bar} {percent}%\n📍 الحالة: {status}"
        try: bot.edit_message_text(text, chat_id, msg_id, parse_mode="Markdown")
        except: pass

    # --- وحدة الإنشاء ---
    def deploy_soldier(self, chat_id):
        status_msg = bot.send_message(chat_id, "🚀 بدء المحرك...")
        mid = status_msg.message_id
        driver = self.create_driver()
        wait = WebDriverWait(driver, 25)
        
        try:
            self.update_progress(chat_id, mid, 10, "توليد بريد مؤقت...")
            email = requests.get("https://www.1secmail.com/api/v1/?action=genAddrs&count=1").json()[0]
            
            self.update_progress(chat_id, mid, 30, "فتح صفحة التسجيل...")
            driver.get("https://www.instagram.com/accounts/emailsignup/")
            
            wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone"))).send_keys(email)
            user = f"army_{random.randint(1000,99999)}"
            pwd = f"King_{random.randint(1000,9999)}!"
            driver.find_element(By.NAME, "fullName").send_keys("Ghost Soldier")
            driver.find_element(By.NAME, "username").send_keys(user)
            driver.find_element(By.NAME, "password").send_keys(pwd)
            
            self.update_progress(chat_id, mid, 50, "إرسال البيانات وتجاوز الميلاد...")
            submit = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            driver.execute_script("arguments[0].click();", submit)
            
            try:
                time.sleep(4)
                year = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@title='Year:']")))
                year.send_keys("1998")
                driver.find_element(By.XPATH, "//button[text()='Next']").click()
            except: pass

            self.update_progress(chat_id, mid, 70, "بانتظار وصول الكود (OTP)...")
            u, d = email.split('@')
            otp = None
            for i in range(12):
                time.sleep(10)
                mails = requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={u}&domain={d}").json()
                if mails:
                    msg = requests.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={u}&domain={d}&id={mails[0]['id']}").json()
                    res = re.findall(r'\b\d{6}\b', msg['body'])
                    if res: otp = res[0]; break
                self.update_progress(chat_id, mid, 70 + i, f"انتظار الكود.. محاولة {i+1}")
            
            if otp:
                wait.until(EC.presence_of_element_located((By.NAME, "email_confirmation_code"))).send_keys(otp)
                time.sleep(2)
                driver.find_element(By.XPATH, "//button[text()='Next']").click()
                cursor.execute('INSERT INTO army (user, pwd) VALUES (?, ?)', (user, pwd))
                conn.commit()
                self.update_progress(chat_id, mid, 100, f"✅ تم التجنيد بنجاح: `{user}`")
            else:
                bot.send_message(chat_id, "❌ فشل: لم يصل كود OTP.")
        except Exception as e:
            driver.save_screenshot("crash.png")
            bot.send_photo(chat_id, open("crash.png", "rb"), caption=f"⚠️ حدث خلل فني:\n`{str(e)[:100]}`", parse_mode="Markdown")
        finally: driver.quit()

    # --- وحدة الهجوم ---
    def follow_attack(self, chat_id, target, amount):
        cursor.execute('SELECT user, pwd FROM army LIMIT ?', (amount,))
        accs = cursor.fetchall()
        status_msg = bot.send_message(chat_id, f"🎯 بدء الهجوم على {target}...")
        mid = status_msg.message_id
        
        completed = 0
        for acc in accs:
            try:
                dr = self.create_driver()
                dr.get("https://www.instagram.com/accounts/login/")
                time.sleep(5)
                WebDriverWait(dr, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(acc[0])
                dr.find_element(By.NAME, "password").send_keys(acc[1])
                dr.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(8)
                dr.get(f"https://www.instagram.com/{target}/")
                time.sleep(4)
                btn = dr.find_element(By.XPATH, "//button[contains(text(), 'Follow')]")
                dr.execute_script("arguments[0].click();", btn)
                completed += 1
                self.update_progress(chat_id, mid, int((completed/len(accs))*100), f"الجندي {acc[0]} نفذ المهمة")
            except Exception as e:
                bot.send_message(chat_id, f"❌ فشل الجندي {acc[0]}: {str(e)[:40]}")
            finally: dr.quit()

engine = UltimateEngine()

@bot.message_handler(commands=['start'])
def start(m):
    cursor.execute('SELECT COUNT(*) FROM army')
    count = cursor.fetchone()[0]
    bot.reply_to(m, f"💀 **OVERLORD SMM CONTROL**\n\n📊 الجيش المتوفر: `{count}`\n\n/gen - تجنيد حساب جديد\n/attack [user] [count] - رشق متابعة")

@bot.message_handler(commands=['gen'])
def gen(m): Thread(target=engine.deploy_soldier, args=(m.chat.id,)).start()

@bot.message_handler(commands=['attack'])
def atk(m):
    args = m.text.split()
    if len(args) == 3: Thread(target=engine.follow_attack, args=(m.chat.id, args[1], int(args[2]))).start()
    else: bot.reply_to(m, "⚠️ استخدم: /attack [target] [count]")

bot.infinity_polling()
