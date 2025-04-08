import os
import datetime
import pytz
import schedule
import time
from telethon import TelegramClient, events, utils
from telethon.tl.types import PeerChannel
import google.generativeai as genai

# --- Налаштування ---
# Замініть на свої значення
TELEGRAM_API_ID = int(os.environ.get("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))  # ID каналу для аналізу

# Назва каналу для відображення (можна отримати динамічно)
CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "цього каналу")

# Формат дати для виведення
DATE_FORMAT = "%d.%m.%Y"

# Емодзі для різних категорій новин (можете розширити цей список)
EMOJI_MAP = {
    "риба": "🐟",
    "суд": "💼",
    "мер": "🏛️",
    "оштрафував": "⚖️",
    "апеляція": "📄",
    "новини": "📰",
    "важливо": "❗",
    "подія": "📢",
    "інцидент": "🚨",
    "допомога": "🤝",
    "спорт": "⚽",
    "культура": "🎭",
    "технології": "💻",
    "погода": "☀️",
}

# --- Ініціалізація клієнтів ---
telegram_client = TelegramClient('samarytanin_bot', TELEGRAM_API_ID, TELEGRAM_API_HASH)
gemini_client = genai.configure(api_key=GEMINI_API_KEY)
model = gemini_client.generative_model(model_name="gemini-pro")

async def get_daily_posts(channel_id, target_date):
    """Отримує всі дописи за вказану дату з Telegram-каналу."""
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    all_messages = []
    async for message in telegram_client.get_messages(channel_id, limit=None, reverse=True):
        if message.date >= start_of_day and message.date <= end_of_day:
            all_messages.append(message)
        elif message.date < start_of_day:
            break
    return all_messages

async def summarize_text(text):
    """Генерує стислий опис тексту за допомогою Gemini API."""
    try:
        response = await model.generate_content_async(f"Стисло перекажи головну думку цього тексту одним-двома реченнями, зберігаючи інформативний та дружелюбний стиль: {text}")
        if response.parts:
            return response.parts[0].text.strip()
        return None
    except Exception as e:
        print(f"Помилка при самаризації: {e}")
        return None

def get_relevant_emoji(summary):
    """Визначає емодзі на основі змісту самарі."""
    if summary:
        summary_lower = summary.lower()
        for keyword, emoji in EMOJI_MAP.items():
            if keyword in summary_lower:
                return emoji
    return "📰"  # Емодзі за замовчуванням

async def process_daily_summary():
    """Збирає, самаризує та публікує головні новини за минулу добу."""
    kyiv_tz = pytz.timezone('Europe/Kiev')
    now_kyiv = datetime.datetime.now(kyiv_tz)
    yesterday_kyiv = now_kyiv - datetime.timedelta(days=1)
    yesterday_date_str = yesterday_kyiv.strftime(DATE_FORMAT)

    print(f"Розпочинаю збір та самаризацію новин за {yesterday_date_str}...")

    messages = await get_daily_posts(CHANNEL_ID, yesterday_kyiv)
    summary_items = []

    for message in messages:
        if message.text and not message.poll and not message.audio:
            print(f"Аналізую допис від {message.date.astimezone(kyiv_tz).strftime('%H:%M:%S')}: {message.text[:50]}...")
            summary = await summarize_text(message.text)
            if summary:
                emoji = get_relevant_emoji(summary)
                message_link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{message.id}" # Генеруємо посилання на допис
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
    """Основна функція для запуску бота."""
    await telegram_client.connect()
    if not await telegram_client.is_user_authorized():
        await telegram_client.send_code_request(await telegram_client.get_me().phone)
        await telegram_client.sign_in(input('Введіть код: '))

    kyiv_tz = pytz.timezone('Europe/Kiev')
    schedule.every().day.at("09:00").do(lambda: telegram_client.loop.create_task(process_daily_summary()))

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
