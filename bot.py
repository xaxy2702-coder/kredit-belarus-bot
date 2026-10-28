"""
Telegram-бот "Кредит Беларусь" для сбора лидов
Автор: finpro.by / Антон Зубков
"""

import logging
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)

BOT_TOKEN = "9144013477:AAGj0nkJAShwdBHYDbQwZUAoCuMvUJjMGm4"
ADMIN_CHAT_ID = "8337294343"

LOG_FILE = os.path.join(os.path.dirname(__file__), "leads.txt")

(
    STATE_START, STATE_GOAL, STATE_AMOUNT, STATE_BUSINESS_TYPE,
    STATE_HISTORY, STATE_COLLATERAL, STATE_NAME, STATE_PHONE, STATE_CONFIRM,
) = range(9)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def kb_goal():
    return ReplyKeyboardMarkup([
        ["💰 Кредит на оборотные средства"],
        ["🏗 Инвестиционный кредит"],
        ["🚛 Лизинг (авто / оборудование)"],
        ["🏦 Банковская гарантия"],
        ["🔄 Рефинансирование кредита"],
        ["❓ Не знаю — нужна консультация"],
    ], resize_keyboard=True, one_time_keyboard=True)

def kb_amount():
    return ReplyKeyboardMarkup([
        ["До 50 000 BYN", "50 000 – 200 000 BYN"],
        ["200 000 – 1 000 000 BYN", "Свыше 1 000 000 BYN"],
    ], resize_keyboard=True, one_time_keyboard=True)

def kb_business():
    return ReplyKeyboardMarkup([
        ["ИП", "ООО / ЧУП"],
        ["ЗАО / ОАО", "Только открываюсь"],
    ], resize_keyboard=True, one_time_keyboard=True)

def kb_history():
    return ReplyKeyboardMarkup([
        ["✅ Да, больше года", "🆕 Менее года"],
        ["❌ Везде отказали", "Впервые обращаюсь"],
    ], resize_keyboard=True, one_time_keyboard=True)

def kb_collateral():
    return ReplyKeyboardMarkup([
        ["✅ Есть залог / поручитель", "❌ Нет залога"],
        ["Не знаю что нужно"],
    ], resize_keyboard=True, one_time_keyboard=True)

def kb_phone():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📱 Отправить номер телефона", request_contact=True)],
        ["Введу вручную"],
    ], resize_keyboard=True, one_time_keyboard=True)

def kb_confirm():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Да, отправить заявку", callback_data="confirm_yes")],
        [InlineKeyboardButton("✏️ Изменить данные", callback_data="confirm_no")],
    ])

def save_lead(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = (f"\n{'='*50}\n📅 {timestamp}\n👤 {data.get('name','—')}\n"
            f"📞 {data.get('phone','—')}\n🎯 {data.get('goal','—')}\n"
            f"💵 {data.get('amount','—')}\n🏢 {data.get('business_type','—')}\n"
            f"📋 {data.get('history','—')}\n🔒 {data.get('collateral','—')}\n"
            f"🆔 @{data.get('username','—')}\n")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

async def notify_admin(context, data):
    msg = (f"🔔 *Новый лид — Кредит Беларусь*\n\n"
           f"👤 *Имя:* {data.get('name','—')}\n"
           f"📞 *Телефон:* {data.get('phone','—')}\n"
           f"🎯 *Цель:* {data.get('goal','—')}\n"
           f"💵 *Сумма:* {data.get('amount','—')}\n"
           f"🏢 *Форма:* {data.get('business_type','—')}\n"
           f"📋 *История:* {data.get('history','—')}\n"
           f"🔒 *Залог:* {data.get('collateral','—')}\n"
           f"🆔 *TG:* @{data.get('username','—')}\n🌐 finpro.by")
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка уведомления: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data['tg_id'] = update.effective_user.id
    context.user_data['username'] = update.effective_user.username or ""
    await update.message.reply_text(
        "👋 Привет! Я помогу вам получить кредит, лизинг или банковскую гарантию для бизнеса в Беларуси.\n\n"
        "Меня зовут *Антон Зубков* — кредитный консультант, 10+ лет в банковском финансировании.\n\n"
        "✅ Первичная консультация — *бесплатно*\n"
        "✅ 95% заявок одобряются\n"
        "✅ Одобрение для ИП — от 3 часов\n\n"
        "Давайте подберём финансирование. Это займёт 1 минуту 👇",
        parse_mode="Markdown")
    await update.message.reply_text("🎯 *Что вам нужно?*", parse_mode="Markdown", reply_markup=kb_goal())
    return STATE_GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal'] = update.message.text
    await update.message.reply_text("💵 *Какая сумма вам нужна?*", parse_mode="Markdown", reply_markup=kb_amount())
    return STATE_AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = update.message.text
    await update.message.reply_text("🏢 *Форма вашего бизнеса?*", parse_mode="Markdown", reply_markup=kb_business())
    return STATE_BUSINESS_TYPE

async def get_business_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['business_type'] = update.message.text
    await update.message.reply_text("📋 *Кредитная история бизнеса:*", parse_mode="Markdown", reply_markup=kb_history())
    return STATE_HISTORY

async def get_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = update.message.text
    await update.message.reply_text("🔒 *Есть залог или поручитель?*", parse_mode="Markdown", reply_markup=kb_collateral())
    return STATE_COLLATERAL

async def get_collateral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['collateral'] = update.message.text
    await update.message.reply_text("👤 *Как вас зовут?*\n\nВведите имя и фамилию:", parse_mode="Markdown",
                                     reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True))
    return STATE_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📞 *Укажите номер телефона:*", parse_mode="Markdown", reply_markup=kb_phone())
    return STATE_PHONE

async def get_phone_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number
    if not phone.startswith("+"): phone = "+" + phone
    context.user_data['phone'] = phone
    return await show_summary(update, context)

async def get_phone_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text.strip()
    return await show_summary(update, context)

async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    summary = (f"📋 *Проверьте заявку:*\n\n"
               f"👤 {d.get('name')}\n📞 {d.get('phone')}\n"
               f"🎯 {d.get('goal')}\n💵 {d.get('amount')}\n"
               f"🏢 {d.get('business_type')}\n📋 {d.get('history')}\n"
               f"🔒 {d.get('collateral')}\n\nВсё верно?")
    await update.message.reply_text(summary, parse_mode="Markdown", reply_markup=kb_confirm())
    return STATE_CONFIRM

async def confirm_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    save_lead(context.user_data)
    await notify_admin(context, context.user_data)
    await query.edit_message_text(
        f"✅ *Заявка принята!*\n\nАнтон свяжется с вами по номеру {context.user_data.get('phone')}.\n\n"
        f"🌐 [finpro.by](https://finpro.by)\n📞 +375 (29) 114-88-35\n✈️ @finproby",
        parse_mode="Markdown", disable_web_page_preview=True)
    return ConversationHandler.END

async def confirm_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("↩️ Начнём заново. Нажмите /start")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено. /start — начать заново\n📞 +375 (29) 114-88-35")
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *Кредит Беларусь — finpro.by*\n\nКредиты, лизинг, гарантии для бизнеса.\n\n"
        "📞 +375 (29) 114-88-35\n✈️ @finproby\n🌐 finpro.by\n\n/start — подать заявку",
        parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STATE_GOAL:          [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal)],
            STATE_AMOUNT:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            STATE_BUSINESS_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_business_type)],
            STATE_HISTORY:       [MessageHandler(filters.TEXT & ~filters.COMMAND, get_history)],
            STATE_COLLATERAL:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_collateral)],
            STATE_NAME:          [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            STATE_PHONE: [
                MessageHandler(filters.CONTACT, get_phone_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone_text),
            ],
            STATE_CONFIRM: [
                CallbackQueryHandler(confirm_yes, pattern="confirm_yes"),
                CallbackQueryHandler(confirm_no, pattern="confirm_no"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_command))
    print("🤖 Бот 'Кредит Беларусь' запущен! Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
