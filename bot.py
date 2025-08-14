import os
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# قراءة ملف الإكسل
df = pd.read_excel("data.xlsx")  # لازم يكون بنفس اسم الملف

# خطوات المحادثة
CHOOSING_BRANCH, ENTER_ID = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    branches = df["الفرع"].unique().tolist()
    keyboard = [[b] for b in branches]
    await update.message.reply_text(
        "اختر الفرع التابع له:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return CHOOSING_BRANCH

async def choose_branch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    branch = update.message.text
    context.user_data["branch"] = branch
    await update.message.reply_text(f"أدخل رقمك الوظيفي في فرع {branch}:")
    return ENTER_ID

async def enter_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emp_id = update.message.text
    branch = context.user_data["branch"]

    # البحث في الإكسل
    record = df[(df["الفرع"] == branch) & (df["الرقم الوظيفي"] == int(emp_id))]
    if not record.empty:
        name = record.iloc[0]["الاسم"]
        amount = record.iloc[0]["القيمة المالية"]
        await update.message.reply_text(f"الاسم: {name}\nالقيمة المالية: {amount} دينار ليبي")
    else:
        await update.message.reply_text("❌ لم يتم العثور على بياناتك. تأكد من صحة الرقم والفرع.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم الإلغاء.")
    return ConversationHandler.END

def main():
    token = os.getenv("BOT_TOKEN")  # جلب التوكن من متغير البيئة
    app = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_BRANCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_branch)],
            ENTER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_id)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()