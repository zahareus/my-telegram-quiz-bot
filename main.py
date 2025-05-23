import os
import datetime
import pytz
import time
from telethon import TelegramClient
import openai
from flask import Flask
from threading import Thread
import asyncio

# --- Налаштування ---
TELEGRAM_API_ID = int(os.environ.get("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
SCHEDULED_TIME = os.environ.get("SCHEDULED_TIME", "09:00")

CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "цього каналу")
DATE_FORMAT = "%d.%m.%Y"
EMOJI_MAP = {
    "риба": "🐟", "суд": "💼", "мер": "🏛️", "оштрафував": "⚖️", "апеляція": "📄",
    "новини": "📰", "важливо": "❗", "подія": "📢", "інцидент": "🚨", "допомога": "🤝",
    "спорт": "⚽", "культура": "🎭", "технології": "💻", "погода": "☀️",
}

TG_PHONE = os.environ.get("TG_PHONE")
TG_PASSWORD = os.environ.get("TG_PASSWORD", None)
TG_LOGIN_CODE = os.environ.get("TG_LOGIN_CODE", None)

# --- Ініціалізація клієнтів ---
telegram_client = TelegramClient('samarytanin_bot', TELEGRAM_API_ID, TELEGRAM_API_HASH)
telegram_user = TelegramClient('user_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
openai.api_key = OPENAI_API_KEY

# --- Flask для Render.com ---
app = Flask(__name__)

@app.route('/')
def hello():
    return "Бот Самаритянин запущено!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- Функції бота ---
async def get_daily_posts(channel_id, target_date):
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    async def code_callback():
        print("Waiting for the code TG_LOGIN_CODE...")
        while True:
            code = os.environ.get("TG_LOGIN_CODE", None)
            if code:
                print(f"Recieved code: {code}")
                return code
            await asyncio.sleep(1)

    all_messages = []
    await telegram_user.start(phone=TG_PHONE, password=TG_PASSWORD, code_callback=code_callback)
    for message in await telegram_user.get_messages(channel_id, limit=None, reverse=True):
        if message.date >= start_of_day and message.date <= end_of_day:
            all_messages.append(message)
        elif message.date < start_of_day:
            break
    await telegram_user.disconnect()
    return all_messages

async def summarize_text(text):
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти - дружелюбний та інформативний бот, який стисло переказує головні новини."},
                {"role": "user", "content": f"Стисло перекажи головну думку цього тексту одним-двома реченнями: {text}"},
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Помилка при самаризації OpenAI: {e}")
        return None

def get_relevant_emoji(summary):
    if summary:
        summary_lower = summary.lower()
        for keyword, emoji in EMOJI_MAP.items():
            if keyword in summary_lower:
                return emoji
    return "📰"

async def process_daily_summary():
    kyiv_tz = pytz.timezone('Europe/Kiev')
    now_kyiv = datetime.datetime.now(kyiv_tz)
    yesterday_kyiv = now_kyiv - datetime.timedelta(days=1)
    yesterday_date_str = yesterday_kyiv.strftime(DATE_FORMAT)

    print(f"Розпочинаю збір та самаризацію новин за {yesterday_date_str}...")

    messages = await get_daily_posts(CHANNEL_ID, yesterday_kyiv)
    summary_items = []

    for message in messages:
        if message.text:
            if "Повітряна тривога" in message.text or "Відбій повітряної тривоги" in message.text or "Натисність на файл speech.mp3 нижче" in message.text:
                print(f"Пропускаю повідомлення: {message.text[:50]}...")
                continue
        if message.text and not message.poll and not message.audio:
            print(f"Аналізую допис від {message.date.astimezone(kyiv_tz).strftime('%H:%M:%S')}: {message.text[:50]}...")
            summary = await summarize_text(message.text)
            if summary:
                emoji = get_relevant_emoji(summary)
                message_link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{message.id}"
                summary_items.append(f"{emoji} {summary} ([посилання]({message_link}))")

    if summary_items:
        summary_text = f"Головні новини за {yesterday_date_str}:\n\n" + "\n\n".join(summary_items)
        try:
            await telegram_client.send_message(CHANNEL_ID, summary_text, link_preview=False)
            print(f"Самарі за {yesterday_date_str} успішно опубліковано в {CHANNEL_NAME}.")
        except Exception as e:
            print(f"Помилка при публікації самарі: {e}")
    else:
        print(f"За {yesterday_date_str} не знайдено текстових дописів для самаризації в {CHANNEL_NAME}.")

async def main():
    print("Функція main запущена!")
    try:
        print("Спроба підключення до Telegram...")
        await telegram_client.start(bot_token=BOT_TOKEN)
        if telegram_client.is_connected():
            print("Підключення до Telegram успішне!")
            try:
                # await telegram_client.send_message(CHANNEL_ID, "Це тестове повідомлення від бота.")
                print(f"Тестове повідомлення успішно надіслано до каналу {CHANNEL_ID}")
            except Exception as e:
                print(f"Помилка при надсиланні тестового повідомлення: {e}")
        else:
            print("Підключення до Telegram не встановлено.")
    except ConnectionError as ce:
        print(f"Помилка ConnectionError під час підключення до Telegram: {ce}")
        return
    except Exception as e:
        print(f"Інша помилка під час підключення до Telegram: {e}")
        return

    kyiv_tz = pytz.timezone('Europe/Kiev')

    while True:
        now_kyiv = datetime.datetime.now(kyiv_tz).time()
        scheduled_hour, scheduled_minute = map(int, SCHEDULED_TIME.split(':'))
        scheduled_time_obj = datetime.time(scheduled_hour, scheduled_minute)

        print(f"Поточний київський час: {now_kyiv.hour}:{now_kyiv.minute}:{now_kyiv.second}")
        print(f"Запланований час: {scheduled_time_obj.hour}:{scheduled_time_obj.minute}")

        if now_kyiv.hour == scheduled_time_obj.hour and now_kyiv.minute == scheduled_time_obj.minute and now_kyiv.second < 60:
            print("Час співпав, запускаю process_daily_summary()")
            await process_daily_summary()
            await asyncio.sleep(60 * 60 * 24) # Запускати лише раз на день

        await asyncio.sleep(60)


if __name__ == "__main__":
    import asyncio
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(telegram_client.disconnect())
        pass
