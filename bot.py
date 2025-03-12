import telebot
from config import TOKEN
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from extensions import APIException, CurrencyConverter

bot = telebot.TeleBot(TOKEN)

CURRENCIES = {
    "USD": "американский доллар",
    "EUR": "евро",
    "RUB": "российский рубль"
}

user_data = {}

# Функция для создания клавиатуры с валютами
def currency_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for currency in CURRENCIES.keys():
        markup.add(KeyboardButton(currency))
    return markup

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    text = (
        "Привет! Я бот-конвертер валют 💰\n\n"
        "Выберите валюту, которую хотите обменять:"
    )
    bot.send_message(message.chat.id, text, reply_markup=currency_keyboard())
    user_data[message.chat.id] = {}

@bot.message_handler(commands=["values"])
def values(message):
    text = "Доступные валюты:\n" + "\n".join(f"{k} - {v}" for k, v in CURRENCIES.items())
    bot.send_message(message.chat.id, text)

# Обработка выбора базовой валюты
@bot.message_handler(func=lambda message: message.chat.id not in user_data or "base" not in user_data[message.chat.id])
def choose_base_currency(message):
    chat_id = message.chat.id
    if message.text not in CURRENCIES:
        bot.send_message(chat_id, "Выберите валюту из списка!", reply_markup=currency_keyboard())
        return

    user_data[chat_id] = {"base": message.text}
    bot.send_message(chat_id, "Теперь выберите валюту, в которую хотите перевести:", reply_markup=currency_keyboard())

# Обработка выбора валюты перевода
@bot.message_handler(func=lambda message: "base" in user_data.get(message.chat.id, {}) and "quote" not in user_data[message.chat.id])
def choose_quote_currency(message):
    chat_id = message.chat.id
    if message.text not in CURRENCIES:
        bot.send_message(chat_id, "Выберите валюту из списка!", reply_markup=currency_keyboard())
        return

    user_data[chat_id]["quote"] = message.text

    if user_data[chat_id]["quote"] == user_data[chat_id]["base"]:
        bot.send_message(chat_id, "Базовая и целевая валюта не могут совпадать! Выберите другую.", reply_markup=currency_keyboard())
        del user_data[chat_id]["quote"]
        return

    bot.send_message(chat_id, "Введите количество валюты (например, 100):")

# Обработка количества и расчёт курса
@bot.message_handler(func=lambda message: "quote" in user_data.get(message.chat.id, {}))
def get_amount(message):
    chat_id = message.chat.id
    try:
        amount = float(message.text)
        base = user_data[chat_id]["base"]
        quote = user_data[chat_id]["quote"]
        result = CurrencyConverter.get_price(base, quote, amount)
        bot.send_message(chat_id, result)
    except ValueError:
        bot.send_message(chat_id, "Введите корректное число!")
        return
    except APIException as e:
        bot.send_message(chat_id, f"Ошибка: {e}")
        return

    # Очистка данных пользователя и предложение нового расчёта
    user_data.pop(chat_id, None)
    bot.send_message(chat_id, "Хотите сделать новый расчёт? Выберите валюту для обмена:", reply_markup=currency_keyboard())

bot.polling()