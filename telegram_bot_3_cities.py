import asyncio
import logging
import aiosqlite
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import *
from aiogram.utils import executor
from aiogram.utils.exceptions import BadRequest, Unauthorized

API_TOKEN = "8912020304:AAEMZz-qwwZLuZRsnHLFwHYnlORaEPmVBlg"
ADMIN_IDS = [6429744800, 887200615]
ADMIN_USERNAME = "econhsler"
ADMIN_GROUP_ID = -1003966123491
CHANNEL_IDS = {
    "Астана": -1003870562073,
    "Кокшетау": -1003719394507,
    "Караганда": -1004376948907,
}

KASPI_NUMBER = "87774211441"
SUPPORT_LINK = "https://t.me/+z8HohTDdolhlMWNi"
BOT_USERNAME = "cvetamda_bot"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

user_states = {}

# База данных НЕ удаляется при запуске — данные сохраняются между перезапусками


def main_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🛍 Создать объявление", callback_data="create"),
        InlineKeyboardButton("📋 Мои объявления", callback_data="my_ads")
    )
    kb.add(
        InlineKeyboardButton("💰 Баланс", callback_data="balance"),
        InlineKeyboardButton("➕ Пополнить", callback_data="deposit")
    )
    kb.add(
        InlineKeyboardButton("💸 Вывести", callback_data="withdraw"),
        InlineKeyboardButton("⭐️ Отзывы", callback_data="my_reviews")
    )
    kb.add(
        InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        InlineKeyboardButton("💬 Поддержка", url=SUPPORT_LINK)
    )
    return kb


def back_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад в меню", callback_data="back"))


def contact_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add(KeyboardButton("📱 Отправить контакт", request_contact=True))
    return kb


def remove_contact_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Меню"))


def city_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for city in CHANNEL_IDS.keys():
        kb.add(KeyboardButton(city))
    kb.add(KeyboardButton("Отмена"))
    return kb


def ad_type_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("💵 Продаю", callback_data="ad_type_sell"))
    kb.add(InlineKeyboardButton("🆓 Бесплатно", callback_data="ad_type_free"))
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="back"))
    return kb


def condition_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("✨ Новый / не использовался", callback_data="cond_new"))
    kb.add(InlineKeyboardButton("👍 Отличное состояние", callback_data="cond_excellent"))
    kb.add(InlineKeyboardButton("✅ Хорошее состояние", callback_data="cond_good"))
    kb.add(InlineKeyboardButton("⚠️ Есть небольшие дефекты", callback_data="cond_fair"))
    return kb


def freshness_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🌹 Только срезаны / только куплены", callback_data="fresh_fresh"))
    kb.add(InlineKeyboardButton("🌸 1–2 дня", callback_data="fresh_1_2"))
    kb.add(InlineKeyboardButton("🌼 3–5 дней", callback_data="fresh_3_5"))
    kb.add(InlineKeyboardButton("💐 Искусственные / сухоцветы", callback_data="fresh_artificial"))
    return kb


def packaging_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🎁 Подарочная упаковка", callback_data="pack_gift"))
    kb.add(InlineKeyboardButton("📦 Стандартная упаковка", callback_data="pack_standard"))
    kb.add(InlineKeyboardButton("🌿 Без упаковки", callback_data="pack_none"))
    return kb


def bargain_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Торг уместен", callback_data="bargain_yes"),
        InlineKeyboardButton("❌ Цена фиксирована", callback_data="bargain_no")
    )
    return kb


def delivery_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🚚 Есть доставка", callback_data="delivery_yes"))
    kb.add(InlineKeyboardButton("🤝 Только самовывоз", callback_data="delivery_no"))
    kb.add(InlineKeyboardButton("🚚🤝 Доставка и самовывоз", callback_data="delivery_both"))
    return kb


def privacy_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("✅ Да, показывать номер", callback_data="show_phone_yes"))
    kb.add(InlineKeyboardButton("🔒 Нет, скрыть номер", callback_data="show_phone_no"))
    return kb


def confirm_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Опубликовать", callback_data="confirm_ad"),
        InlineKeyboardButton("✏️ Изменить", callback_data="edit_ad")
    )
    kb.add(InlineKeyboardButton("❌ Отменить", callback_data="cancel_ad"))
    return kb


def admin_ad_keyboard(ad_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_ad_{ad_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_ad_{ad_id}")
    )
    return kb


def admin_pay_keyboard(pay_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_pay_{pay_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_pay_{pay_id}")
    )
    return kb


def photos_done_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        KeyboardButton("✅ Завершить загрузку фото")
    )


def rules_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("✅ Я ознакомлен и согласен", callback_data="accept_rules"))
    kb.add(InlineKeyboardButton("❌ Отказаться", callback_data="back"))
    return kb


async def init_db():
    async with aiosqlite.connect("greenline.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ad_type TEXT DEFAULT 'sell',
                city TEXT DEFAULT 'Не указан',
                title TEXT,
                description TEXT,
                photos TEXT,
                price INTEGER DEFAULT 0,
                show_phone INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                views INTEGER DEFAULT 0,
                created_at TEXT,
                condition TEXT DEFAULT '',
                freshness TEXT DEFAULT '',
                packaging TEXT DEFAULT '',
                bargain TEXT DEFAULT '',
                delivery TEXT DEFAULT '',
                channel_msg_id INTEGER DEFAULT 0
            )
        """)

        # На случай если база создавалась раньше без новых колонок
        for col in ['condition', 'freshness', 'packaging', 'bargain', 'delivery']:
            try:
                await db.execute(f"ALTER TABLE ads ADD COLUMN {col} TEXT DEFAULT ''")
            except Exception:
                pass
        try:
            await db.execute("ALTER TABLE ads ADD COLUMN channel_msg_id INTEGER DEFAULT 0")
        except Exception:
            pass

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                is_auth INTEGER DEFAULT 0,
                username TEXT,
                full_name TEXT,
                phone TEXT,
                rating REAL DEFAULT 0,
                deals INTEGER DEFAULT 0,
                join_date TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                type TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
        """)

        await db.commit()


async def is_auth(user_id):
    async with aiosqlite.connect("greenline.db") as db:
        cur = await db.execute("SELECT is_auth FROM users WHERE user_id=?", (user_id,))
        res = await cur.fetchone()
        return bool(res and res[0] == 1)


async def get_balance(user_id):
    async with aiosqlite.connect("greenline.db") as db:
        cur = await db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        res = await cur.fetchone()
        return res[0] if res else 0


async def get_user(user_id):
    async with aiosqlite.connect("greenline.db") as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return await cur.fetchone()


async def get_ad(ad_id):
    async with aiosqlite.connect("greenline.db") as db:
        cur = await db.execute("SELECT * FROM ads WHERE id=?", (ad_id,))
        return await cur.fetchone()


RULES_TEXT = """📋 <b>ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА ПУБЛИКАЦИИ</b>

1️⃣ Размещать объявления строго по теме бота — продажа букетов, цветов и сопутствующих товаров.

2️⃣ Фото должны полностью соответствовать объявлению. Спам, фейк и чужие фото — запрещены.

3️⃣ Категорически запрещена нецензурная лексика в названии и описании.

4️⃣ Объявления без указания цены подлежат немедленному удалению.

5️⃣ Запрещено вводить покупателей в заблуждение — ложная информация, чужие фото и т.д.

⚠️ <b>ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ:</b>
Администрация бота выступает исключительно как информационный посредник. Все сделки совершаются на ваш страх и риск.

🚫 <b>НАКАЗАНИЕ:</b>
За нарушение правил — моментальный бан без возможности восстановления.

Незнание правил не освобождает от ответственности."""


# ===================== СТАРТ =====================

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    args = message.get_args()

    if args and args.startswith("buy_"):
        try:
            ad_id = int(args.split("_")[1])
        except (ValueError, IndexError):
            await message.answer("❌ Неверная ссылка.")
            return

        if not await is_auth(user_id):
            await message.answer(
                "👋 Добро пожаловать!\n\nДля просмотра объявления сначала авторизуйтесь.",
                reply_markup=contact_keyboard()
            )
            return

        ad = await get_ad(ad_id)
        if not ad or ad[9] != 'active':
            if ad and ad[9] == 'sold':
                await message.answer("🔴 Это объявление уже продано.")
            else:
                await message.answer("❌ Объявление не найдено или уже снято с продажи.")
            return

        photos = json.loads(ad[6]) if ad[6] else []
        seller = await get_user(ad[1])
        seller_username = seller[3] if seller and seller[3] else None

        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton("💬 Написать админу", url=f"https://t.me/{ADMIN_USERNAME}"))
        if seller_username:
            kb.add(InlineKeyboardButton("🛒 Написать продавцу", url=f"https://t.me/{seller_username}"))
        else:
            kb.add(InlineKeyboardButton("🛒 Написать продавцу", url=f"tg://user?id={ad[1]}"))

        caption = f"<b>{ad[4]}</b>\n\n{ad[5]}\n\n<b>{ad[7]} ₸</b>\n{ad[3]}"
        if photos:
            await message.answer_photo(photos[0], caption=caption, reply_markup=kb)
        else:
            await message.answer(caption, reply_markup=kb)
        return

    async with aiosqlite.connect("greenline.db") as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = await cur.fetchone()

        if not user:
            await db.execute("""
                INSERT INTO users (user_id, balance, is_auth, username, full_name, phone, rating, deals, join_date)
                VALUES (?, 0, 0, ?, ?, ?, 0, 0, ?)
            """, (user_id, username, full_name, "", datetime.now().strftime("%d.%m.%Y")))
            await db.commit()
            await message.answer(
                "👋 Добро пожаловать!\n\n"
                "📱 Для начала отправьте номер телефона:",
                reply_markup=contact_keyboard()
            )
        else:
            # Обновляем username на случай если он сменился
            await db.execute("UPDATE users SET username=? WHERE user_id=?", (username, user_id))
            await db.commit()

            if user[2] == 0:
                await message.answer("📱 Отправьте номер телефона:", reply_markup=contact_keyboard())
            else:
                await message.answer("👋 С возвращением!", reply_markup=remove_contact_keyboard())
                await message.answer("🏠 Главное меню", reply_markup=main_keyboard())


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def get_contact(message: types.Message):
    user_id = message.from_user.id
    phone = message.contact.phone_number

    async with aiosqlite.connect("greenline.db") as db:
        await db.execute("UPDATE users SET is_auth=1, phone=? WHERE user_id=?", (phone, user_id))
        await db.commit()

    await message.answer("✅ Номер подтверждён!", reply_markup=remove_contact_keyboard())
    await message.answer("🏠 Главное меню", reply_markup=main_keyboard())


@dp.message_handler(lambda m: m.text == "Меню")
async def menu_command(message: types.Message):
    if await is_auth(message.from_user.id):
        await message.answer("🏠 Главное меню", reply_markup=main_keyboard())


# ===================== НАВИГАЦИЯ =====================

@dp.callback_query_handler(lambda c: c.data == "back")
async def go_back(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer("🏠 Главное меню", reply_markup=main_keyboard())


@dp.callback_query_handler(lambda c: c.data == "cancel_ad")
async def cancel_ad(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    await call.message.edit_text("❌ Создание объявления отменено.")
    await call.message.answer("🏠 Главное меню", reply_markup=main_keyboard())


@dp.message_handler(lambda m: m.text == "❌ Отмена")
async def cancel_creation(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    await message.answer("❌ Отменено.", reply_markup=ReplyKeyboardRemove())
    await message.answer("🏠 Главное меню", reply_markup=main_keyboard())


# ===================== СОЗДАНИЕ ОБЪЯВЛЕНИЯ =====================

@dp.callback_query_handler(lambda c: c.data == "create")
async def create_ad_start(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id

    if not await is_auth(user_id):
        await call.message.answer("⚠️ Сначала авторизуйтесь через /start")
        return

    user_states[user_id] = {"step": "rules", "photos": []}
    await call.message.edit_text(RULES_TEXT, reply_markup=rules_keyboard())


@dp.callback_query_handler(lambda c: c.data == "accept_rules")
async def accept_rules(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id

    if user_id not in user_states:
        user_states[user_id] = {"photos": []}

    user_states[user_id]["step"] = "ad_type"

    intro_text = (
        "🛍 <b>Создание объявления</b>\n\n"
        "Несколько простых шагов:\n\n"
        "1️⃣ Тип объявления\n"
        "2️⃣ Город\n"
        "3️⃣ Название\n"
        "4️⃣ Описание\n"
        "5️⃣ Состояние, свежесть, упаковка\n"
        "6️⃣ Торг и доставка\n"
        "7️⃣ Фото и цена\n\n"
        "⏱ Займёт 3–4 минуты!\n\n"
        "Выберите тип объявления:"
    )

    await call.message.edit_text(intro_text, reply_markup=ad_type_keyboard())


@dp.callback_query_handler(lambda c: c.data.startswith("ad_type_"))
async def process_ad_type(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id

    if user_id not in user_states:
        return

    ad_type = call.data.replace("ad_type_", "")
    user_states[user_id]["ad_type"] = ad_type
    user_states[user_id]["step"] = "city"

    type_names = {"sell": "Продажа", "free": "Бесплатно"}
    await call.message.edit_text(
        f"✅ Тип: <b>{type_names.get(ad_type)}</b>\n\n"
        "2️⃣ <b>Шаг 2 — Выбор города</b>"
    )
    await call.message.answer("📍 В каком городе?", reply_markup=city_keyboard())


@dp.message_handler(lambda m: m.text in CHANNEL_IDS.keys())
async def process_city(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id].get("step") != "city":
        return

    city = message.text
    user_states[user_id]["city"] = city
    user_states[user_id]["step"] = "title"
    await message.answer(
        f"Город: {city}\n\n"
        "Шаг 3 — Название товара\n\n"
        "Введите краткое и понятное название.\n"
        "Например: «Букет из 25 роз», «Пионы свежие»\n\n"
        "Минимум 3 символа.",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.callback_query_handler(lambda c: c.data.startswith("cond_"))
async def process_condition(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    if user_id not in user_states:
        return

    cond_map = {
        "cond_new": "✨ Новый / не использовался",
        "cond_excellent": "👍 Отличное состояние",
        "cond_good": "✅ Хорошее состояние",
        "cond_fair": "⚠️ Есть небольшие дефекты"
    }
    user_states[user_id]["condition"] = cond_map.get(call.data, "—")
    user_states[user_id]["step"] = "freshness"

    await call.message.edit_text(
        f"✅ Состояние: <b>{cond_map.get(call.data)}</b>\n\n"
        "🌹 <b>Свежесть</b>\n\n"
        "Выберите свежесть цветов:",
        reply_markup=freshness_keyboard()
    )


@dp.callback_query_handler(lambda c: c.data.startswith("fresh_"))
async def process_freshness(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    if user_id not in user_states:
        return

    fresh_map = {
        "fresh_fresh": "🌹 Только срезаны / только куплены",
        "fresh_1_2": "🌸 1–2 дня",
        "fresh_3_5": "🌼 3–5 дней",
        "fresh_artificial": "💐 Искусственные / сухоцветы"
    }
    user_states[user_id]["freshness"] = fresh_map.get(call.data, "—")
    user_states[user_id]["step"] = "packaging"

    await call.message.edit_text(
        f"✅ Свежесть: <b>{fresh_map.get(call.data)}</b>\n\n"
        "🎁 <b>Упаковка</b>\n\n"
        "Выберите тип упаковки:",
        reply_markup=packaging_keyboard()
    )


@dp.callback_query_handler(lambda c: c.data.startswith("pack_"))
async def process_packaging(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    if user_id not in user_states:
        return

    pack_map = {
        "pack_gift": "🎁 Подарочная упаковка",
        "pack_standard": "📦 Стандартная упаковка",
        "pack_none": "🌿 Без упаковки"
    }
    user_states[user_id]["packaging"] = pack_map.get(call.data, "—")
    user_states[user_id]["step"] = "bargain"

    await call.message.edit_text(
        f"✅ Упаковка: <b>{pack_map.get(call.data)}</b>\n\n"
        "💬 <b>Торг</b>\n\n"
        "Торг уместен?",
        reply_markup=bargain_keyboard()
    )


@dp.callback_query_handler(lambda c: c.data.startswith("bargain_"))
async def process_bargain(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    if user_id not in user_states:
        return

    bargain_map = {
        "bargain_yes": "✅ Торг уместен",
        "bargain_no": "❌ Цена фиксирована"
    }
    user_states[user_id]["bargain"] = bargain_map.get(call.data, "—")
    user_states[user_id]["step"] = "delivery"

    await call.message.edit_text(
        f"✅ Торг: <b>{bargain_map.get(call.data)}</b>\n\n"
        "🚚 <b>Доставка</b>\n\n"
        "Как покупатель может получить товар?",
        reply_markup=delivery_keyboard()
    )


@dp.callback_query_handler(lambda c: c.data.startswith("delivery_"))
async def process_delivery(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    if user_id not in user_states:
        return

    delivery_map = {
        "delivery_yes": "🚚 Есть доставка",
        "delivery_no": "🤝 Только самовывоз",
        "delivery_both": "🚚🤝 Доставка и самовывоз"
    }
    user_states[user_id]["delivery"] = delivery_map.get(call.data, "—")
    user_states[user_id]["step"] = "photos"

    await call.message.edit_text(
        f"✅ Доставка: <b>{delivery_map.get(call.data)}</b>\n\n"
        "📸 <b>Фотографии товара</b>\n\n"
        "Загрузите качественные фото — хорошие снимки привлекают больше покупателей.\n\n"
        "📌 <i>До 10 фотографий. Когда закончите — нажмите «Завершить загрузку фото».</i>"
    )
    await call.message.answer("👇 Отправляйте фото:", reply_markup=photos_done_keyboard())


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id].get("step") != "photos":
        return

    photos = user_states[user_id].get("photos", [])
    if len(photos) >= 10:
        await message.answer("⚠️ Максимум 10 фотографий.")
        return

    photos.append(message.photo[-1].file_id)
    user_states[user_id]["photos"] = photos

    await message.answer(
        f"📸 Фото {len(photos)}/10 добавлено!\n\n"
        f"{'Можете добавить ещё или нажмите кнопку ниже.' if len(photos) < 10 else '✅ Лимит достигнут. Нажмите кнопку ниже.'}",
        reply_markup=photos_done_keyboard()
    )


@dp.message_handler(lambda m: m.text == "✅ Завершить загрузку фото")
async def finish_photos(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id].get("step") != "photos":
        return

    photos = user_states[user_id].get("photos", [])
    if not photos:
        await message.answer("⚠️ Добавьте хотя бы одно фото!")
        return

    user_states[user_id]["step"] = "price"
    await message.answer(
        f"✅ <b>{len(photos)} фото добавлено!</b>\n\n"
        "💰 <b>Цена</b>\n\n"
        "Введите цену товара в тенге.\n\n"
        "📌 <i>Только цифры. Минимум 10 ₸.</i>",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.callback_query_handler(lambda c: c.data in ["show_phone_yes", "show_phone_no"])
async def process_privacy(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id

    if user_id not in user_states:
        return

    show_phone = 1 if call.data == "show_phone_yes" else 0
    user_states[user_id]["show_phone"] = show_phone
    user_states[user_id]["step"] = "confirm"

    data = user_states[user_id]
    type_names = {"sell": "Продаю", "free": "Бесплатно"}

    desc = data.get('description', '')[:200]
    if len(data.get('description', '')) > 200:
        desc += "..."

    preview = (
        f"👀 <b>Предпросмотр объявления</b>\n\n"
        f"{type_names.get(data.get('ad_type'), 'Продаю')} | {data.get('city', 'Не указан')}\n\n"
        f"<b>{data.get('title', 'Без названия')}</b>\n\n"
        f"{desc}\n\n"
        f"🔍 Состояние: {data.get('condition', '—')}\n"
        f"🌹 Свежесть: {data.get('freshness', '—')}\n"
        f"🎁 Упаковка: {data.get('packaging', '—')}\n"
        f"💬 Торг: {data.get('bargain', '—')}\n"
        f"🚚 Доставка: {data.get('delivery', '—')}\n\n"
        f"💰 <b>{data.get('price', 0)} ₸</b>\n"
        f"📞 Номер: {'Виден покупателю' if show_phone else 'Скрыт'}\n"
        f"📸 Фото: {len(data.get('photos', []))} шт.\n\n"
        f"Всё верно? Нажмите <b>«Опубликовать»</b> для отправки на модерацию."
    )

    await call.message.edit_text(preview, reply_markup=confirm_keyboard())


@dp.callback_query_handler(lambda c: c.data == "confirm_ad")
async def confirm_and_publish(call: types.CallbackQuery):
    await call.answer("⏳ Отправляем...")
    user_id = call.from_user.id

    if user_id not in user_states:
        await call.message.edit_text("⚠️ Сессия истекла. Начните заново.")
        return

    data = user_states[user_id]
    photos = data.get("photos", [])

    if not photos:
        await call.message.edit_text("📸 Добавьте хотя бы одно фото!")
        return

    try:
        async with aiosqlite.connect("greenline.db") as db:
            await db.execute("""
                INSERT INTO ads (user_id, ad_type, city, title, description, photos, price, show_phone, status, created_at, condition, freshness, packaging, bargain, delivery)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                data.get("ad_type", "sell"),
                data.get("city", "Не указан"),
                data["title"],
                data["description"],
                json.dumps(photos),
                data["price"],
                data.get("show_phone", 0),
                datetime.now().strftime("%d.%m.%Y %H:%M"),
                data.get("condition", ""),
                data.get("freshness", ""),
                data.get("packaging", ""),
                data.get("bargain", ""),
                data.get("delivery", "")
            ))
            cur = await db.execute("SELECT last_insert_rowid()")
            row = await cur.fetchone()
            ad_id = row[0]
            await db.commit()

        seller = await get_user(user_id)
        seller_username = seller[3] if seller and seller[3] else None
        seller_phone = seller[5] if seller else "не указан"
        show_phone = data.get("show_phone", 0)

        type_names = {"sell": "Продажа", "free": "Бесплатно"}
        admin_text = (
            f"🆕 <b>НОВОЕ ОБЪЯВЛЕНИЕ #{ad_id}</b>\n\n"
            f"👤 Продавец: @{seller_username or user_id}\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"📞 Телефон: {'<code>' + seller_phone + '</code> — ВИДЕН' if show_phone and seller_phone != 'не указан' else 'скрыт'}\n\n"
            f"{type_names.get(data.get('ad_type'), 'Продажа')} — <b>{data['title']}</b>\n"
            f"📍 {data['city']} | 💰 {data['price']} ₸\n\n"
            f"🔍 {data.get('condition', '—')}\n"
            f"🌹 {data.get('freshness', '—')}\n"
            f"🎁 {data.get('packaging', '—')}\n"
            f"💬 {data.get('bargain', '—')}\n"
            f"🚚 {data.get('delivery', '—')}\n\n"
            f"{data['description'][:300]}{'...' if len(data['description']) > 300 else ''}\n\n"
            f"📸 Фото: {len(photos)} шт."
        )

        try:
            await bot.send_photo(
                ADMIN_GROUP_ID,
                photo=photos[0],
                caption=admin_text,
                reply_markup=admin_ad_keyboard(ad_id)
            )
            for i, photo in enumerate(photos[1:4], 2):
                try:
                    await bot.send_photo(ADMIN_GROUP_ID, photo, caption=f"📸 Фото {i} к объявлению #{ad_id}")
                except Exception as e:
                    logging.warning(f"Не удалось отправить доп. фото: {e}")
        except Exception as e:
            logging.error(f"Не удалось отправить объявление в админ-группу: {e}")
            await call.message.edit_text(
                "⚠️ Объявление сохранено, но не удалось уведомить администратора.\n"
                "Свяжитесь с поддержкой.",
                reply_markup=main_keyboard()
            )
            del user_states[user_id]
            return

        await call.message.edit_text(
            f"✅ <b>Объявление #{ad_id} отправлено на модерацию!</b>\n\n"
            f"Обычно проверка занимает несколько минут.\n"
            f"Мы уведомим вас после публикации. 🙌",
            reply_markup=main_keyboard()
        )

        del user_states[user_id]

    except Exception as e:
        logging.error(f"Ошибка confirm_ad: {e}")
        await call.message.edit_text(f"⚠️ Ошибка при отправке: {str(e)[:200]}")


# ===================== ОДОБРЕНИЕ / ОТКЛОНЕНИЕ ОБЪЯВЛЕНИЙ =====================

@dp.callback_query_handler(lambda c: c.data.startswith("approve_ad_"))
async def approve_ad(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("🚫 Нет прав!", show_alert=True)
        return

    await call.answer("⏳ Публикую...")
    ad_id = int(call.data.split("_")[2])

    try:
        async with aiosqlite.connect("greenline.db") as db:
            cur = await db.execute("SELECT * FROM ads WHERE id=? AND status='pending'", (ad_id,))
            ad = await cur.fetchone()

            if not ad:
                await call.answer("⚠️ Уже обработано", show_alert=True)
                return

            photos = json.loads(ad[6]) if ad[6] else []
            if not photos:
                await call.answer("⚠️ Нет фото!", show_alert=True)
                return

            cur_user = await db.execute("SELECT username, user_id FROM users WHERE user_id=?", (ad[1],))
            user_row = await cur_user.fetchone()
            seller_username = user_row[0] if user_row and user_row[0] else None
            seller_id = user_row[1] if user_row else ad[1]

            type_label = {"sell": "Продажа", "free": "Бесплатно"}.get(ad[2], "Продажа")
            channel_id = CHANNEL_IDS.get(ad[3])

            if not channel_id:
                await call.answer("⚠️ Для этого города не указан канал", show_alert=True)
                return

            def strip_emoji(text):
                import re
                return re.sub(r"[^\w\s.,!?;:@#+-]", "", str(text)).strip()

            extra = ""
            try:
                if ad[12]: extra += f"\n{strip_emoji(ad[12])}"
                if ad[13]: extra += f"\n{strip_emoji(ad[13])}"
                if ad[14]: extra += f"\n{strip_emoji(ad[14])}"
                if ad[15]: extra += f"\n{strip_emoji(ad[15])}"
                if ad[16]: extra += f"\n{strip_emoji(ad[16])}"
            except IndexError:
                pass

            channel_caption = (
                f"{type_label}\n"
                f"<b>{ad[4]}</b>\n\n"
                f"{ad[5]}"
                f"{extra}\n\n"
                f"<b>{ad[7]} ₸</b>\n"
                f"{ad[3]}"
            )

            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(InlineKeyboardButton("💬 Написать админу", url=f"https://t.me/{ADMIN_USERNAME}"))
            if seller_username:
                kb.add(InlineKeyboardButton("🛒 Написать продавцу", url=f"https://t.me/{seller_username}"))
            else:
                kb.add(InlineKeyboardButton("🛒 Написать продавцу", url=f"tg://user?id={seller_id}"))
            kb.add(InlineKeyboardButton("🛍 Разместить своё объявление", url=f"https://t.me/{BOT_USERNAME}"))

            async def send_to_channel(reply_markup):
                if len(photos) == 1:
                    return await bot.send_photo(channel_id, photo=photos[0], caption=channel_caption, reply_markup=reply_markup)
                else:
                    media_group = []
                    for i, photo in enumerate(photos[:10]):
                        if i == 0:
                            media_group.append(InputMediaPhoto(media=photo, caption=channel_caption, parse_mode='HTML'))
                        else:
                            media_group.append(InputMediaPhoto(media=photo))
                    sent = await bot.send_media_group(channel_id, media=media_group)
                    btn_msg = await bot.send_message(channel_id, "👇", reply_markup=reply_markup, reply_to_message_id=sent[0].message_id)
                    return sent[0]

            try:
                sent_msg = await send_to_channel(kb)
                channel_msg_id = sent_msg.message_id if hasattr(sent_msg, 'message_id') else sent_msg[0].message_id
            except BadRequest as e:
                logging.error(f"Ошибка при публикации с кнопками: {e}")
                # Убираем кнопку продавца и пробуем снова
                fallback_kb = InlineKeyboardMarkup(row_width=1)
                fallback_kb.add(InlineKeyboardButton("💬 Написать админу", url=f"https://t.me/{ADMIN_USERNAME}"))
                fallback_kb.add(InlineKeyboardButton("🛍 Разместить своё объявление", url=f"https://t.me/{BOT_USERNAME}"))
                sent_msg = await send_to_channel(fallback_kb)
                channel_msg_id = sent_msg.message_id if hasattr(sent_msg, 'message_id') else sent_msg[0].message_id

            await db.execute("UPDATE ads SET status='active', channel_msg_id=? WHERE id=?", (channel_msg_id, ad_id))
            await db.commit()

            try:
                await bot.send_message(
                    ad[1],
                    f"✅ Ваше объявление <b>#{ad_id}</b> опубликовано в канале!\n\nЖелаем успешных продаж! 🙌"
                )
            except Exception as e:
                logging.warning(f"Не удалось уведомить продавца: {e}")

            try:
                await call.message.edit_caption(
                    caption=call.message.caption + "\n\n✅ ОПУБЛИКОВАНО",
                    reply_markup=None
                )
            except Exception:
                pass

    except Exception as e:
        logging.error(f"Ошибка approve_ad: {e}")
        await call.answer(f"⚠️ Ошибка: {str(e)[:100]}", show_alert=True)


@dp.callback_query_handler(lambda c: c.data.startswith("reject_ad_"))
async def reject_ad(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("🚫 Нет прав!", show_alert=True)
        return

    await call.answer()
    ad_id = int(call.data.split("_")[2])

    try:
        async with aiosqlite.connect("greenline.db") as db:
            cur = await db.execute("SELECT user_id FROM ads WHERE id=?", (ad_id,))
            row = await cur.fetchone()

            if row:
                await db.execute("UPDATE ads SET status='rejected' WHERE id=?", (ad_id,))
                await db.commit()

                try:
                    await bot.send_message(
                        row[0],
                        f"❌ Ваше объявление <b>#{ad_id}</b> отклонено.\n\n"
                        f"Проверьте соответствие правилам и попробуйте снова."
                    )
                except Exception as e:
                    logging.warning(f"Не удалось уведомить продавца об отклонении: {e}")

                try:
                    await call.message.edit_caption(
                        caption=call.message.caption + "\n\n❌ ОТКЛОНЕНО",
                        reply_markup=None
                    )
                except Exception:
                    pass
    except Exception as e:
        logging.error(f"Ошибка reject_ad: {e}")


# ===================== ОПЛАТЫ =====================

@dp.callback_query_handler(lambda c: c.data == "deposit")
async def deposit(call: types.CallbackQuery):
    await call.answer()
    user_states[call.from_user.id] = {"step": "deposit_city"}
    await call.message.edit_text(
        "➕ <b>Пополнение баланса</b>\n\n"
        "Сначала выберите город, к которому относится заявка:"
    )
    await call.message.answer("📍 Выберите город:", reply_markup=city_keyboard())


@dp.callback_query_handler(lambda c: c.data == "withdraw")
async def withdraw(call: types.CallbackQuery):
    await call.answer()
    bal = await get_balance(call.from_user.id)
    if bal < 500:
        await call.message.edit_text(
            f"💰 Баланс: <b>{bal} ₸</b>\n\n"
            f"⚠️ Для вывода нужно минимум <b>500 ₸</b>.",
            reply_markup=back_keyboard()
        )
    else:
        user_states[call.from_user.id] = {"step": "withdraw_city"}
        await call.message.edit_text(
            f"💸 <b>Вывод средств</b>\n\n"
            f"Доступно: <b>{bal} ₸</b>\n\n"
            "Сначала выберите город, к которому относится заявка:"
        )
        await call.message.answer("📍 Выберите город:", reply_markup=city_keyboard())


@dp.callback_query_handler(lambda c: c.data.startswith("approve_pay_"))
async def approve_pay(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("🚫 Нет прав!", show_alert=True)
        return

    await call.answer()
    pay_id = int(call.data.split("_")[2])

    try:
        async with aiosqlite.connect("greenline.db") as db:
            # БАГ ИСПРАВЛЕН: раньше фильтр был только по type='deposit',
            # из-за чего одобрение withdraw-заявок ломалось ("не найдено")
            cur = await db.execute("SELECT user_id, amount, status, type FROM payments WHERE id=?", (pay_id,))
            payment = await cur.fetchone()

            if not payment:
                await call.answer("⚠️ Платёж не найден", show_alert=True)
                return

            if payment[2] == 'done':
                await call.answer("⚠️ Уже подтверждено", show_alert=True)
                return

            user_id, amount, status, pay_type = payment

            if pay_type == 'deposit':
                await db.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
                notify_text = f"✅ Баланс пополнен на <b>{amount} ₸</b>!\n\nМожете размещать объявления 🛍"
            else:  # withdraw
                await db.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
                notify_text = f"✅ Вывод <b>{amount} ₸</b> подтверждён администратором!\n\nСредства будут переведены в ближайшее время."

            await db.execute("UPDATE payments SET status='done' WHERE id=?", (pay_id,))
            await db.commit()

            try:
                await bot.send_message(user_id, notify_text, reply_markup=main_keyboard())
            except Exception as e:
                logging.warning(f"Не удалось уведомить пользователя о платеже: {e}")

            try:
                await call.message.edit_text(
                    call.message.text + "\n\n✅ ПОДТВЕРЖДЕНО",
                    reply_markup=None
                )
            except Exception:
                pass

            await call.answer(f"✅ Операция #{pay_id} подтверждена!", show_alert=True)

    except Exception as e:
        logging.error(f"Ошибка approve_pay: {e}")
        await call.answer(f"⚠️ Ошибка: {str(e)[:100]}", show_alert=True)


@dp.callback_query_handler(lambda c: c.data.startswith("reject_pay_"))
async def reject_pay(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("🚫 Нет прав!", show_alert=True)
        return

    await call.answer()
    pay_id = int(call.data.split("_")[2])

    try:
        async with aiosqlite.connect("greenline.db") as db:
            cur = await db.execute("SELECT user_id, status FROM payments WHERE id=?", (pay_id,))
            payment = await cur.fetchone()

            if not payment:
                await call.answer("⚠️ Платёж не найден", show_alert=True)
                return

            if payment[1] == 'done':
                await call.answer("⚠️ Уже обработано, нельзя отклонить", show_alert=True)
                return

            await db.execute("UPDATE payments SET status='rejected' WHERE id=?", (pay_id,))
            await db.commit()

            try:
                await bot.send_message(
                    payment[0],
                    f"❌ Заявка #{pay_id} отклонена.\n\n"
                    f"Если это ошибка — обратитесь в поддержку."
                )
            except Exception as e:
                logging.warning(f"Не удалось уведомить пользователя об отклонении: {e}")

            try:
                await call.message.edit_text(
                    call.message.text + "\n\n❌ ОТКЛОНЕНО",
                    reply_markup=None
                )
            except Exception:
                pass

    except Exception as e:
        logging.error(f"Ошибка reject_pay: {e}")


# ===================== ОБЫЧНЫЙ ТЕКСТ (ВВОД ДАННЫХ) =====================

@dp.message_handler(lambda m: not m.text.startswith('/'))
async def handle_text(message: types.Message):
    user_id = message.from_user.id

    if not await is_auth(user_id):
        await message.answer("👋 Введите /start для начала работы.")
        return

    if user_id not in user_states:
        await message.answer("🏠 Главное меню", reply_markup=main_keyboard())
        return

    step = user_states[user_id].get("step")
    text = message.text

    if step == "deposit_city":
        if text not in CHANNEL_IDS:
            await message.answer("⚠️ Выберите город кнопкой ниже.", reply_markup=city_keyboard())
            return

        user_states[user_id]["city"] = text
        user_states[user_id]["step"] = "deposit_amount"
        await message.answer(
            f"📍 Город: <b>{text}</b>\n\n"
            "Введите сумму пополнения в тенге:\n\n"
            "📌 <i>Минимум 100 ₸</i>",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    if step == "withdraw_city":
        if text not in CHANNEL_IDS:
            await message.answer("⚠️ Выберите город кнопкой ниже.", reply_markup=city_keyboard())
            return

        user_states[user_id]["city"] = text
        user_states[user_id]["step"] = "withdraw_amount"
        bal = await get_balance(user_id)
        await message.answer(
            f"📍 Город: <b>{text}</b>\n\n"
            f"Доступно: <b>{bal} ₸</b>\n\n"
            "Введите сумму вывода в тенге:\n\n"
            "📌 <i>Минимум 500 ₸</i>",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    if step == "title":
        if len(text) < 3:
            await message.answer("⚠️ Название слишком короткое — минимум <b>3 символа</b>.")
            return
        user_states[user_id]["title"] = text
        user_states[user_id]["step"] = "description"
        await message.answer(
            "✅ <b>Название принято!</b>\n\n"
            "4️⃣ <b>Шаг 4 — Описание товара</b>\n\n"
            "Расскажите подробнее о товаре.\n\n"
            "📌 <i>Минимум 10 символов, максимум 500 символов.</i>"
        )
        return

    if step == "description":
        if len(text) < 10:
            await message.answer(
                f"⚠️ Описание слишком короткое!\n\n"
                f"Минимум <b>10 символов</b>. Сейчас: {len(text)}. Напишите подробнее."
            )
            return
        if len(text) > 500:
            await message.answer(
                f"⚠️ Описание слишком длинное!\n\n"
                f"Максимум <b>500 символов</b>. Сейчас: {len(text)}. Сократите текст ✂️"
            )
            return
        user_states[user_id]["description"] = text
        user_states[user_id]["step"] = "condition"
        await message.answer(
            "✅ <b>Описание принято!</b>\n\n"
            "5️⃣ <b>Состояние товара</b>\n\n"
            "Выберите состояние:",
            reply_markup=condition_keyboard()
        )
        return

    if step == "price":
        try:
            price = int(text.replace(" ", "").replace(",", ""))
            if price < 10:
                raise ValueError()
        except ValueError:
            await message.answer("⚠️ Введите корректную цену (только цифры, минимум 10 ₸).")
            return

        user_states[user_id]["price"] = price
        user_states[user_id]["step"] = "privacy"
        await message.answer(
            f"✅ <b>Цена: {price} ₸</b>\n\n"
            "📞 <b>Последний шаг!</b>\n\n"
            "Показывать ваш номер телефона покупателям?",
            reply_markup=privacy_keyboard()
        )
        return

    if step == "deposit_amount":
        try:
            amount = int(text.strip().replace(" ", ""))
            if amount < 100:
                await message.answer("⚠️ Минимальная сумма пополнения — <b>100 ₸</b>")
                return
        except ValueError:
            await message.answer("⚠️ Введите сумму цифрами")
            return

        async with aiosqlite.connect("greenline.db") as db:
            await db.execute(
                "INSERT INTO payments (user_id, amount, type, created_at) VALUES (?, ?, 'deposit', ?)",
                (user_id, amount, datetime.now().strftime("%d.%m.%Y %H:%M"))
            )
            cur = await db.execute("SELECT last_insert_rowid()")
            row = await cur.fetchone()
            pay_id = row[0]
            await db.commit()

        await message.answer(
            f"✅ <b>Заявка #{pay_id} создана!</b>\n\n"
            f"Переведите <b>{amount} ₸</b> на номер:\n"
            f"<code>{KASPI_NUMBER}</code>\n\n"
            f"📝 В комментарии обязательно укажите:\n"
            f"<b>#{pay_id}</b>\n\n"
            f"После оплаты ожидайте подтверждения от администратора.",
            reply_markup=main_keyboard()
        )

        user = await get_user(user_id)
        city = user_states[user_id].get("city", "Не указан")
        try:
            await bot.send_message(
                ADMIN_GROUP_ID,
                f"💰 <b>Пополнение #{pay_id}</b>\n"
                f"📍 Город: <b>{city}</b>\n"
                f"👤 @{user[3] if user and user[3] else user_id}\n"
                f"🆔 <code>{user_id}</code>\n"
                f"💵 {amount} ₸",
                reply_markup=admin_pay_keyboard(pay_id)
            )
        except Exception as e:
            logging.error(f"Не удалось отправить заявку на пополнение в группу: {e}")

        del user_states[user_id]
        return

    if step == "withdraw_amount":
        try:
            amount = int(text.replace(" ", ""))
            if amount < 500:
                await message.answer("⚠️ Минимальная сумма вывода — <b>500 ₸</b>")
                return
        except ValueError:
            await message.answer("⚠️ Введите сумму цифрами")
            return

        balance = await get_balance(user_id)
        if balance < amount:
            await message.answer(f"⚠️ Недостаточно средств. Ваш баланс: <b>{balance} ₸</b>")
            return

        async with aiosqlite.connect("greenline.db") as db:
            await db.execute(
                "INSERT INTO payments (user_id, amount, type, created_at) VALUES (?, ?, 'withdraw', ?)",
                (user_id, amount, datetime.now().strftime("%d.%m.%Y %H:%M"))
            )
            cur = await db.execute("SELECT last_insert_rowid()")
            row = await cur.fetchone()
            pay_id = row[0]
            await db.commit()

        await message.answer(f"✅ Заявка на вывод #{pay_id} создана!", reply_markup=main_keyboard())

        user = await get_user(user_id)
        city = user_states[user_id].get("city", "Не указан")
        try:
            await bot.send_message(
                ADMIN_GROUP_ID,
                f"💸 <b>Вывод #{pay_id}</b>\n"
                f"📍 Город: <b>{city}</b>\n"
                f"👤 @{user[3] if user and user[3] else user_id}\n"
                f"🆔 <code>{user_id}</code>\n"
                f"💵 {amount} ₸",
                reply_markup=admin_pay_keyboard(pay_id)
            )
        except Exception as e:
            logging.error(f"Не удалось отправить заявку на вывод в группу: {e}")

        del user_states[user_id]


# ===================== ПРОЧИЕ КНОПКИ МЕНЮ =====================

@dp.callback_query_handler(lambda c: c.data == "edit_ad")
async def edit_ad(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    await call.message.edit_text("✏️ Начните создание объявления заново.")
    await call.message.answer("🏠 Главное меню", reply_markup=main_keyboard())


@dp.callback_query_handler(lambda c: c.data == "profile")
async def profile(call: types.CallbackQuery):
    await call.answer()
    user = await get_user(call.from_user.id)
    balance = await get_balance(call.from_user.id)
    text = (
        f"👤 <b>Профиль</b>\n\n"
        f"Имя: {user[4] if user and user[4] else '—'}\n"
        f"📞 Телефон: {user[5] if user and user[5] else '—'}\n"
        f"💰 Баланс: <b>{balance} ₸</b>\n"
        f"📅 Дата регистрации: {user[8] if user and user[8] else '—'}"
    )
    await call.message.edit_text(text, reply_markup=back_keyboard())


@dp.callback_query_handler(lambda c: c.data == "balance")
async def balance_handler(call: types.CallbackQuery):
    await call.answer()
    bal = await get_balance(call.from_user.id)
    await call.message.edit_text(
        f"💰 <b>Ваш баланс</b>\n\n<b>{bal} ₸</b>",
        reply_markup=back_keyboard()
    )


@dp.callback_query_handler(lambda c: c.data == "my_ads")
async def my_ads(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    async with aiosqlite.connect("greenline.db") as db:
        cur = await db.execute(
            "SELECT id, title, price, status FROM ads WHERE user_id=? ORDER BY id DESC LIMIT 15",
            (user_id,)
        )
        ads = await cur.fetchall()

    if not ads:
        await call.message.edit_text(
            "📋 <b>Мои объявления</b>\n\nУ вас пока нет объявлений.",
            reply_markup=back_keyboard()
        )
        return

    status_map = {"pending": "⏳", "active": "✅", "rejected": "❌", "sold": "🔴"}
    kb = InlineKeyboardMarkup(row_width=1)
    for ad in ads:
        ad_id, title, price, status = ad
        label = f"{status_map.get(status, '•')} #{ad_id} — {title[:25]} — {price} ₸"
        kb.add(InlineKeyboardButton(label, callback_data=f"view_ad_{ad_id}"))
    kb.add(InlineKeyboardButton("◀️ Назад в меню", callback_data="back"))

    await call.message.edit_text(
        "📋 <b>Мои объявления</b>\n\nВыберите объявление для управления:",
        reply_markup=kb
    )


@dp.callback_query_handler(lambda c: c.data.startswith("view_ad_"))
async def view_ad(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    ad_id = int(call.data.split("_")[2])

    ad = await get_ad(ad_id)
    if not ad or ad[1] != user_id:
        await call.answer("⚠️ Объявление не найдено", show_alert=True)
        return

    status_names = {"pending": "⏳ На модерации", "active": "✅ Активно", "rejected": "❌ Отклонено", "sold": "🔴 Продано"}
    text = (
        f"<b>{ad[4]}</b>\n\n"
        f"{ad[5]}\n\n"
        f"💰 <b>{ad[7]} ₸</b>\n"
        f"📍 {ad[3]}\n"
        f"📌 Статус: {status_names.get(ad[9], ad[9])}"
    )

    kb = InlineKeyboardMarkup(row_width=1)
    if ad[9] == 'active':
        kb.add(InlineKeyboardButton("🔴 Отметить как продано", callback_data=f"sold_ad_{ad_id}"))
    kb.add(InlineKeyboardButton("◀️ К списку объявлений", callback_data="my_ads"))

    await call.message.edit_text(text, reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("sold_ad_"))
async def mark_as_sold(call: types.CallbackQuery):
    await call.answer("⏳ Обрабатываю...")
    user_id = call.from_user.id
    ad_id = int(call.data.split("_")[2])

    ad = await get_ad(ad_id)
    if not ad or ad[1] != user_id:
        await call.answer("⚠️ Объявление не найдено", show_alert=True)
        return

    if ad[9] != 'active':
        await call.answer("⚠️ Это объявление нельзя отметить как проданное", show_alert=True)
        return

    channel_msg_id = ad[17] if len(ad) > 17 else 0
    channel_id = CHANNEL_IDS.get(ad[3])

    if not channel_id:
        await call.answer("⚠️ Для города объявления не указан канал", show_alert=True)
        return

    # Убираем кнопки и дописываем "ПРОДАНО" в посте канала
    if channel_msg_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=channel_id,
                message_id=channel_msg_id,
                reply_markup=None
            )
        except Exception as e:
            logging.warning(f"Не удалось убрать кнопки в канале: {e}")

        try:
            type_label = {"sell": "Продажа", "free": "Бесплатно"}.get(ad[2], "Продажа")
            extra = ""
            try:
                if ad[12]: extra += f"\n{ad[12]}"
                if ad[13]: extra += f"\n{ad[13]}"
                if ad[14]: extra += f"\n{ad[14]}"
                if ad[15]: extra += f"\n{ad[15]}"
                if ad[16]: extra += f"\n{ad[16]}"
            except IndexError:
                pass

            sold_caption = (
                f"<b>ПРОДАНО</b>\n\n"
                f"{type_label}\n"
                f"<b>{ad[4]}</b>\n\n"
                f"{ad[5]}"
                f"{extra}\n\n"
                f"<b>{ad[7]} ₸</b>\n"
                f"{ad[3]}"
            )

            await bot.edit_message_caption(
                chat_id=channel_id,
                message_id=channel_msg_id,
                caption=sold_caption
            )
        except Exception as e:
            logging.warning(f"Не удалось отредактировать подпись в канале: {e}")

    async with aiosqlite.connect("greenline.db") as db:
        await db.execute("UPDATE ads SET status='sold' WHERE id=?", (ad_id,))
        await db.commit()

    await call.message.edit_text(
        f"✅ <b>Объявление #{ad_id} отмечено как проданное!</b>\n\n"
        f"Пост в канале обновлён — кнопки покупки убраны, добавлена пометка «ПРОДАНО».",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("◀️ К списку объявлений", callback_data="my_ads")
        )
    )


@dp.callback_query_handler(lambda c: c.data == "my_reviews")
async def my_reviews(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "⭐️ <b>Отзывы</b>\n\nРаздел отзывов скоро будет доступен.",
        reply_markup=back_keyboard()
    )


async def on_startup(dp):
    await init_db()
    logging.info("База данных инициализирована, бот запущен ✅")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)



