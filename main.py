import telebot
token = '7213072989:AAEV5PNjtslCkFDJ6EJlKmFt6rIBUJ5gVaY'
bot = telebot.TeleBot (token)
from telebot import types
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton("🚀 Старт")
    action_button = types.KeyboardButton("🥰 Выдай слово")
    markup.add(start_button, action_button)
    bot.send_message(message.chat.id, text="Привет, {0.first_name} 👋\nВоспользуйся кнопками".format(message.from_user), reply_markup=markup)

import random
from dictionary import dictionary

@bot.message_handler(content_types=['text'])
def buttons(message):
    if message.text == "🚀 Старт":
        bot.send_message(message.chat.id, text="Я могу помочь с запоминанием слов. Просто попроси об этом")
    elif message.text == "🥰 Выдай слово":
        bot.send_message(message.chat.id, text=f"{random.choice(dictionary)}")
    else:
        bot.send_message(message.chat.id, text="Я могу отвечать только на нажатие кнопок")

        bot.polling(none_stop=True, interval=0)