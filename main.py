import os
import threading
import asyncio
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, CallbackQueryHandler
)
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "✅ GlovoPromoBot працює!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# --- Вставь свои ссылки!
LINK_PODTV = "https://t.me/+HX9lFRXTtNlmNjdl" 
LINK_18_YES = "https://t.me/+8cmf0XKYgCI2NWY1" 
LINK_18_NO = "https://t.me/+mH1QsMXStwM2NGM1" 
LINK_MAN = "https://t.me/+xEyaki3qCUQwNjNl" 
LINK_WOMAN = "https://t.me/+XQCFoJIST9QwOTE1" 
LINK_UA = "https://t.me/+ZjKExDhWJFU3M2Jl" 
LINK_NOT_UA = "https://t.me/+-tf51XaB-OdhOGM1" 
REGION_LINKS = {
    'east': "https://t.me/+AXPIDA_mm3hjNWY1", 
    'central': "https://t.me/+LQo7v-Ce9S0zMGJl", 
    'west': "https://t.me/+XMx3gIRcCfRiNWNl", 
    'south': "https://t.me/+91tRkW0duIM0MWQ9", 
    'north': "https://t.me/+JgKrbLk05kw4NWI1", 
}

(
    STEP_CONFIRM, STEP_SERVICE, STEP_SUM,
    STEP_FINAL_CONFIRM, STEP_GET_PROMO
) = range(5)

user_data = {}

SERVICES = ["Glovo", "KFC", "McDonald’s", "Сушія", "Dominos Pizza"]
SUMS = ["100 грн", "500 грн", "1000 грн", "2000 грн"]

CERT_BLUR_IMG = {
    "Glovo": "glovo_cert_blur_v1.jpg",
    "KFC": "kfc_cert_blur_v1.jpg",
    "McDonald’s": "mcd_cert_blur_v1.jpg",
    "Сушія": "sushiya_cert_blur_v1.jpg",
    "Dominos Pizza": "dominos_cert_blur_v1.jpg"
}
CERT_FINAL_IMG = {
    "Glovo": "glovo_cert_final.jpg",
    "KFC": "kfc_cert_final.jpg",
    "McDonald’s": "mcd_cert_final.jpg",
    "Сушія": "sushiya_cert_final.jpg",
    "Dominos Pizza": "dominos_cert_final.jpg"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    user_data[chat_id] = {}

    # 1. Сообщение с приветствием (без картинки)
    await context.bot.send_message(
        chat_id,
        "🍔 Вітаємо в Glovo Промокоди 🍔!\n\n"
        "⚠️ Увага!\n"
        "Залишилось 113 із 12 000 промокодів\n\n"
        "🔥 Зараз доступні промокоди на:\n"
        "— Glovo\n— KFC\n— McDonald’s\n— Сушія\n— Dominos Pizza\n\n"
        "На суми: 100, 500, 1000 і 2000 грн\n"
    )

    # 2. Фото + текст + кнопка
    with open("2.jpeg", "rb") as img:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption=(
                "Готові отримати свій промокод прямо зараз?\n"
                "Спочатку підтвердіть, що ви не бот 🤖"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Підтвердити!", url=LINK_PODTV)]
            ])
        )

    await asyncio.sleep(5)
    # 3. Выбор сервиса
    await context.bot.send_message(
        chat_id, "Оберіть сервіс доставки або заклад фастфуду:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(name, callback_data=f"srv_{name}")]
            for name in SERVICES
        ])
    )
    return STEP_SERVICE

async def handle_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    service = query.data.replace("srv_", "")
    user_data[chat_id]["service"] = service
    # 2. Выбор суммы
    await context.bot.send_message(
        chat_id,
        "Ваш промокод майже готовий! Оберіть суму:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(s, callback_data=f"sum_{s}")] for s in SUMS
        ])
    )
    return STEP_SUM

async def handle_sum(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    s = query.data.replace("sum_", "")
    user_data[chat_id]["sum"] = s
    # 3. Проверка + кнопка
    await context.bot.send_message(
        chat_id,
        f"Дякуємо! Перевіримо ваш вибір:\nСервіс — {user_data[chat_id]['service']}, Сума — {s}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Підтвердити", callback_data="final_confirm")]
        ])
    )
    return STEP_FINAL_CONFIRM

async def handle_final_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    service = user_data[chat_id]['service']
    # 3.1 Блюр фото + кнопка “Пройти”
    with open(CERT_BLUR_IMG[service], "rb") as img:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption="Промокод сформовано ✅\nЧерез підозрілу активність ботів, треба пройти перевірку.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Пройти перевірку", url=LINK_PODTV)]
            ])
        )
    await asyncio.sleep(5)
    # 4. Вік
    with open("1.jpeg", "rb") as img:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption="Тобі вже є 18 років?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Так✅", url=LINK_18_YES)],
                [InlineKeyboardButton("Ні❌", url=LINK_18_NO)],
            ])
        )
    await asyncio.sleep(5)
    # 4.1 Стать
    with open("3.jpeg", "rb") as img:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption="Вибери свою стать:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👨 Чоловіча", url=LINK_MAN)],
                [InlineKeyboardButton("👩 Жіноча", url=LINK_WOMAN)],
            ])
        )
    await asyncio.sleep(5)
    # 5. Українець (с фото)
    with open("7.jpg", "rb") as img:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption="Ти з України?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Я українець 🇺🇦", url=LINK_UA)],
                [InlineKeyboardButton("Ні❌", url=LINK_NOT_UA)]
            ])
        )
    await asyncio.sleep(5)
    # 6. Регіон
    with open("4.jpeg", "rb") as img:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption="З якого ти регіону?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🇺🇦 Східна Україна", url=REGION_LINKS['east'])],
                [InlineKeyboardButton("🇺🇦 Центральна Україна", url=REGION_LINKS['central'])],
                [InlineKeyboardButton("🇺🇦 Західна Україна", url=REGION_LINKS['west'])],
                [InlineKeyboardButton("🇺🇦 Південна Україна", url=REGION_LINKS['south'])],
                [InlineKeyboardButton("🇺🇦 Північна Україна", url=REGION_LINKS['north'])],
            ])
        )
    await asyncio.sleep(5)
    # 7. Поздравление + кнопка
    with open("5.jpeg", "rb") as img:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption="🎉 Вітаємо! Ви пройшли перевірку.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Отримати промокод", callback_data="get_promo")]
            ])
        )
    return STEP_GET_PROMO

async def handle_get_promo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    service = user_data[chat_id]['service']
    with open(CERT_FINAL_IMG[service], "rb") as img:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption=(
                f"🎉 Твій промокод готовий! Покажи його на касі у закладі {service}. Сума: {user_data[chat_id]['sum']}"
            )
        )
    return ConversationHandler.END

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STEP_SERVICE: [CallbackQueryHandler(handle_service, pattern=r"^srv_")],
            STEP_SUM: [CallbackQueryHandler(handle_sum, pattern=r"^sum_")],
            STEP_FINAL_CONFIRM: [CallbackQueryHandler(handle_final_confirm, pattern=r"^final_confirm$")],
            STEP_GET_PROMO: [CallbackQueryHandler(handle_get_promo, pattern="get_promo")],
        },
        fallbacks=[CommandHandler('start', start)],
        allow_reentry=True
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
