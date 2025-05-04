import telebot
from telebot import types
from secrets import secrets
import random
from dictionary import dictionary #Словарь
from mudrosti import file # карточки с цитатами

# Получаем токен для бота из отдельной папки
token = secrets.get('BOT_API_TOKEN')
bot = telebot.TeleBot(token)

# Словари для хранения состояния пользователей
user_compliment_index = {}
user_received_compliments = {}
user_card_state = {}

#Обработчик команды /start. Отправляет приветственное сообщение и выводит клавиатуру с кнопками.
#message: Объект сообщения от пользователя, содержащий информацию о чате и пользователе
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    action_buttons = [
        types.KeyboardButton("⚔️Auxilium"),
        types.KeyboardButton("📜Data verbum"),
        types.KeyboardButton("🏺Informatio"),
        types.KeyboardButton("🐺Сitatus")
    ]
    markup.add(*action_buttons)

    bot.send_message(
        message.chat.id,
        text=f"Salve, discipulus(a) {message.from_user.first_name} 👋\nВоспользуйся кнопками.\nИх можно открыть, нажав на квадрат (плитки) рядом со строкой отправки сообщений",
        reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
# Обрабатывает текстовые сообщения от пользователей и выполняет соответствующие действия в зависимости от нажатой кнопки.
# Если пользователь нажимает на кнопку, бот отправляет соответствующее сообщение или выполняет действие.
def buttons(message):#Обработчик текстовых сообщений. Определяет, какую кнопку нажал пользователь, и выполняет соответствующее действие.
    if message.text == "⚔️Auxilium":
        bot.send_message(message.chat.id, text="Вы вызвали помощь. К сожалению, все легионы на данный момент заняты.\n\nЕсли вы хотите получить новую флеш-карту - нажмите на кнопку 📜Data verbum.\n\nЕсли вы хотите узнать о проекте - нажмите на кнопку \n🏺Informatio.\n\nЕсли вы хотите получить крылатое выражение - нажмите на кнопку 🐺Сitatus")

    elif message.text == "📜Data verbum":# Отправляет комплимент (флеш-карту) пользователю.
        index = random.randint(0, len(dictionary) - 1)
        user_compliment_index[message.chat.id] = index
        user_card_state[message.chat.id] = "front"
        send_compliment(message.chat.id, index)
    elif message.text == "🏺Informatio":
        bot.send_message(message.chat.id, text="Этот бот создан студентами-историками в образовательно-просветительских целях")
    elif message.text == "🐺Сitatus":
        random_file = random.choice(file)
        with open(random_file, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, text="Пожалуйста, используйте кнопки.")

@bot.callback_query_handler(func=lambda call: True)#Обработчик callback-запросов
#Обрабатывает нажатия кнопок в инлайн-клавиатуре. В зависимости от нажатой кнопки, функция либо переворачивает карточку с комплиментом, либо повторно отправляет комплимент пользователю.
#call: Объект обратного вызова, содержащий информацию о нажатой кнопке и сообщении.
def callback_query(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == "flip":
        if user_id in user_received_compliments and message_id in user_received_compliments[user_id]:
            user_received_compliments[user_id][message_id]["state"] = "back" if user_received_compliments[user_id][message_id]["state"] == "front" else "front"
            bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=get_compliment_part(user_received_compliments[user_id][message_id]["index"], user_received_compliments[user_id][message_id]["state"]),
                reply_markup=create_inline_markup()
            )

def send_compliment(chat_id, index):
#Отправляет комплимент пользователю и сохраняет его состояние.
#Если пользователь еще не получал комплименты, создается новая запись.
#Комплимент отправляется с инлайн-клавиатурой для взаимодействия.
#Args:
        #chat_id: ID чата пользователя, которому отправляется комплимент.
        #index: Индекс комплимента в словаре.
    if chat_id not in user_received_compliments:
        user_received_compliments[chat_id] = {}
    text = get_compliment_part(index, "front")
    sent_message = bot.send_message(chat_id, text=text, reply_markup=create_inline_markup())
    user_received_compliments[chat_id][sent_message.message_id] = {"index": index, "state": "front", "text": text}


def get_compliment_part(index, state):
    compliment = dictionary[index]
    parts = compliment.split('\n', 1)
    return parts[0] if state == "front" else parts[1] if len(parts) > 1 else "Нет дополнительной информации"
#Получает часть комплимента в зависимости от состояния (лицевая или обратная сторона).
#Разделяет комплимент на части и возвращает соответствующую часть в зависимости от состояния.
#Args:
        #index: Индекс комплимента в словаре.
        #state: Состояние карточки ('front' или 'back').
#Returns:
        #str: Лицевая или обратная часть комплимента.


def create_inline_markup(): #Создает инлайн-клавиатуру с кнопкой для переворота карточки.
    #Returns:
        #InlineKeyboardMarkup: Инлайн-клавиатура с кнопкой.
    markup = types.InlineKeyboardMarkup()
    flip_button = types.InlineKeyboardButton("Перевернуть карточку", callback_data="flip")
    markup.add(flip_button)
    return markup

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)