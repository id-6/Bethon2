import telebot, requests, random, time, sqlite3, hashlib, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from threading import Thread

# [1] إعداد قاعدة البيانات
conn = sqlite3.connect('insta_army.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS army (user TEXT, pwd TEXT, status TEXT)')
conn.commit()

# [2] الإعدادات - ضع التوكن الخاص بك هنا
BOT_TOKEN = "6193186034:AAHpKPAGwUPi3Jr7-Uv4f5Sz-gmY8tH8bNI"
bot = telebot.TeleBot(BOT_TOKEN)

class OverlordMachine:
    def create_driver(self):
        options = webdriver.ChromeOptions()
        # إذا كنت تستخدم Tor، فعل السطر التالي:
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = webdriver.Chrome(options=options)
        
        # حقن كود تشويش البصمة (Canvas Noise)
        noise_script = """
        const original = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type) {
            const ctx = original.apply(this, arguments);
            if (type === '2d') {
                const fill = ctx.fillText;
                ctx.fillText = function() {
                    ctx.fillStyle = 'rgba(0,0,0,0.01)';
                    fill.apply(this, arguments);
                }
            }
            return ctx;
        };
        """
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": noise_script})

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        return driver

    def human_typing(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.4))

    def deploy(self, chat_id):
        # تجديد هوية تور قبل البدء
        os.system("sudo service tor reload")
        driver = self.create_driver()
        try:
            u_api = requests.get("https://randomuser.me/api/").json()['results'][0]
            username = f"{u_api['login']['username']}_{random.randint(100,999)}"
            password = f"Shadow_{random.randint(10,99)}!X"

            driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(random.uniform(6, 10))

            self.human_typing(driver.find_element(By.NAME, "emailOrPhone"), f"{username}@gmail.com")
            self.human_typing(driver.find_element(By.NAME, "fullName"), f"{u_api['name']['first']} {u_api['name']['last']}")
            self.human_typing(driver.find_element(By.NAME, "username"), username)
            self.human_typing(driver.find_element(By.NAME, "password"), password)
            
            time.sleep(2)
            btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            driver.execute_script("arguments[0].click();", btn)
            
            cursor.execute('INSERT INTO army VALUES (?, ?, ?)', (username, password, 'ACTIVE'))
            conn.commit()
            bot.send_message(chat_id, f"🎯 **تم بنجاح:** `{username}`")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ فشل: {str(e)[:50]}")
        finally:
            driver.quit()

# [3] أوامر التليجرام (Command & Control)
machine = OverlordMachine()

@bot.message_handler(commands=['start'])
def menu(m):
    msg = (
        "💀 **SHADOW CONTROL PANEL** 💀\n\n"
        "🌪️ `/deploy [count]` - إنشاء حسابات\n"
        "🔑 `/show_army` - عرض البيانات\n"
        "📊 `/status` - حالة الجيش"
    )
    bot.reply_to(m, msg, parse_mode="Markdown")

@bot.message_handler(commands=['deploy'])
def handle_deploy(m):
    try:
        count = int(m.text.split()[1])
        bot.reply_to(m, f"🚀 جاري البدء بنشر {count} جندي...")
        for _ in range(count):
            Thread(target=machine.deploy, args=(m.chat.id,)).start()
            time.sleep(random.randint(5, 15))
    except:
        bot.reply_to(m, "⚠️ استخدم: `/deploy 5`")

@bot.message_handler(commands=['show_army'])
def show(m):
    cursor.execute('SELECT user, pwd FROM army')
    accs = cursor.fetchall()
    res = "🔓 **بيانات الجيش:**\n\n"
    for a in accs: res += f"👤 `{a[0]}` | 🔑 `{a[1]}`\n"
    bot.send_message(m.chat.id, res, parse_mode="Markdown")

bot.infinity_polling()
