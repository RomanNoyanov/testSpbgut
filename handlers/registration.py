import telebot  # https://pypi.org/project/pyTelegramBotAPI/0.3.0/
from telebot import types
from dbsql import BotDB
from create_bot import bot
from ref import db_file
from logFile import log

BotDB = BotDB(db_file)
#@bot.message_handler(content_types=['text'])  # (обработчик сообщения)
# ----------------------РЕГИСТРАЦИЯ-------------------------------------------
def get_user_text(message):
    log(message)
    get_message = message.text.strip().lower()
    if get_message == "регистрация":
        bot.send_message(message.chat.id, "Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, add_name_user)

    elif get_message == 'info chat message':
        bot.send_message(message.chat.id, message)

    elif get_message == 'мой id':
        bot.send_message(message.chat.id, message.from_user.id)

    else:
        bot.send_message(message.chat.id, "Не понял тебя")

def add_name_user(message):
    log(message)
    global name_user
    name_user = message.text
    bot.send_message(message.chat.id, "Ведите вашу фамилию:")
    bot.register_next_step_handler(message, add_surname_user)
    return name_user


def add_surname_user(message):
    log(message)
    global surname_user
    surname_user = message.text
    bot.send_message(message.chat.id, "Выбирите номер группы:")
    bot.register_next_step_handler(message, add_group_user)
    return surname_user


def add_group_user(message):
    log(message)
    global group_user
    group_user = message.text
    mes = f"Ваше имя: {name_user} \nВаша фамилия: {surname_user} \nВаша группа: {group_user}"
    bot.send_message(message.chat.id, mes)

    if (not BotDB.user_exists(message.from_user.id)):
        try:
            BotDB.add_user(message.from_user.id, name_user, surname_user, group_user)
            print("Успешно!")
            print(f"Новый ученик: {name_user}  {surname_user} из {group_user} ")
        except:
            print("Ошибка")
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированны")


def register_hendlers_reg(bot):
    bot.message_handler(content_types=['text'])(get_user_text)