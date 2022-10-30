import telebot  # https://pypi.org/project/pyTelegramBotAPI/0.3.0/
import re
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
        bot.send_message(message.chat.id, "Введите ваше имя:", reply_markup = types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_name) # Принимает два обязательных аргументы первый это message, а второй это function, ждёт сообщение пользователя и потом вызывает указанную функцию с аргументом message

    elif get_message == 'info chat message':
        bot.send_message(message.chat.id, message)

    elif get_message == 'мой id':
        bot.send_message(message.chat.id, message.from_user.id)

    else:
        bot.send_message(message.chat.id, "Не понял вас \nДля знакомства с основными командами бота введите /help")

def check_name(message):
    log(message)
    regex = re.compile(r'([А-Яа-яЁё]+)') # регулярное выражение для имени
    name = str(message.text)
    if re.fullmatch(regex, name): # проверка на соответствие строки name шаблону regex
        add_name_user(message)
    else:
        bot.send_message(message.chat.id, "Неверный формат имени, повторите ввод")
        bot.register_next_step_handler(message, check_name)

# https://habr.com/ru/post/349860/


def add_name_user(message):
    log(message)
    global name_user
    name_user = message.text
    bot.send_message(message.chat.id, "Введите вашу фамилию:")
    bot.register_next_step_handler(message, check_surname)
    return name_user


def check_surname(message):
    log(message)
    regex = re.compile(r'([А-Яа-яЁё]+)')  # регулярное выражение для фамилии
    surname = str(message.text)
    if re.fullmatch(regex, surname):
        add_surname_user(message)
    else:
        bot.send_message(message.chat.id, "Неверный формат фамилии, повторите ввод")
        bot.register_next_step_handler(message, check_surname)


def add_surname_user(message):
    log(message)
    global surname_user
    surname_user = message.text
    bot.send_message(message.chat.id, "Введите номер группы:")
    bot.register_next_step_handler(message, add_group_user)
    return surname_user


def add_group_user(message):
    log(message)
    global group_user
    group_user = message.text
    mes = f"Вы успешно зарегистрированны! \nВаше имя: {name_user} \nВаша фамилия: {surname_user} \nВаша группа: {group_user}"
    bot.send_message(message.chat.id, mes)

    if (not BotDB.user_exists(message.from_user.id)):
        try:
            BotDB.add_user(message.from_user.id, name_user, surname_user, group_user)
            print("Успешно!")
            print(f"Новый ученик: {name_user}  {surname_user} из {group_user} ")
        except Exception as e:
            print(e)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированны")


def register_hendlers_reg(bot):
    bot.message_handler(content_types=['text'])(get_user_text)
