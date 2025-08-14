import telebot
import pandas as pd

# توكن البوت من BotFather
TOKEN = "8216082108:AAFeI7ZP5k-vuLOs0a50__4l7eQuDOGV4Mc"

bot = telebot.TeleBot(TOKEN)

# قراءة ملف الإكسل
# لازم يكون فيه الأعمدة: الفرع، الرقم الوظيفي، الاسم، الحالة الإجتماعية، القيمة المالية
data = pd.read_excel("data.xlsx")

# تخزين البيانات المؤقتة للمستخدمين أثناء المحادثة
user_data = {}

# أمر البداية
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً! 👋\nمن فضلك اختر الفرع التابع له:")
    branches = data['الفرع'].unique()
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for branch in branches:
        markup.add(str(branch))
    bot.send_message(message.chat.id, "اختر الفرع:", reply_markup=markup)

# استقبال الفرع
@bot.message_handler(func=lambda message: message.text in data['الفرع'].astype(str).values)
def get_branch(message):
    user_data[message.chat.id] = {'branch': message.text}
    bot.send_message(message.chat.id, "الرجاء إدخال رقمك الوظيفي:")

# استقبال الرقم الوظيفي وعرض البيانات
@bot.message_handler(func=lambda message: message.text.isdigit())
def get_employee_data(message):
    branch = user_data.get(message.chat.id, {}).get('branch')
    emp_id = int(message.text)

    # البحث عن الموظف
    record = data[(data['الفرع'] == branch) & (data['الرقم الوظيفي'] == emp_id)]

    if not record.empty:
        name = record.iloc[0]['الاسم']
        status = record.iloc[0]['الحالة الإجتماعية']
        amount = record.iloc[0]['القيمة المالية']
        bot.send_message(
            message.chat.id,
            f"👤 الاسم: {name}\n"
            f"📍 الفرع: {branch}\n"
            f"💼 الحالة الإجتماعية: {status}\n"
            f"💰 القيمة المالية: {amount} دينار ليبي"
        )
    else:
        bot.send_message(message.chat.id, "لم يتم العثور على بيانات مطابقة ❌")

# تشغيل البوت
bot.polling(none_stop=True)