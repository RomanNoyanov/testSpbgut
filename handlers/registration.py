import telebot  # https://pypi.org/project/pyTelegramBotAPI/0.3.0/
import re
from telebot import types
from dbsql import BotDB
from create_bot import bot
from ref import db_file
from ref import password
from logFile import log

# НАДО СДЕЛАТЬ УДАЛЕНИЕ ДАННЫХ, МАЛО ЛИ ВВЕЛИ С ОШИБКОЙ

BotDB = BotDB(db_file)
#@bot.message_handler(content_types=['text'])  # (обработчик сообщения)
# ----------------------РЕГИСТРАЦИЯ-------------------------------------------
def get_user_text(message):
    "переработка текста отправленного кнопкой и запуск нужного процесса регистрации"
    log(message)
    get_message = message.text.strip().lower()
    if get_message == "зарегистрироваться как студент":
        bot.send_message(message.chat.id, "Введите ваше имя:", reply_markup = types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_name) # Принимает два обязательных аргументы первый это message, а второй это function, ждёт сообщение пользователя и потом вызывает указанную функцию с аргументом message

    elif get_message == "зарегистрироваться как преподаватель":
        bot.send_message(message.chat.id, "Введите код доступа:", reply_markup = types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_password)

    elif get_message == 'мой id':
        bot.send_message(message.chat.id, message.from_user.id)

    else:
        bot.send_message(message.chat.id, "Не понял вас \nДля знакомства с основными командами бота введите /help")

def check_name(message):
    "функция проверки имени на соответствие шаблону, при несовпадении требует повторный ввод"
    log(message)
    regex = re.compile(r'([А-Яа-яЁё]+)') # регулярное выражение для имени
    name = str(message.text)
    if re.fullmatch(regex, name):
        add_name_user(message)
    else:
        bot.send_message(message.chat.id, "Неверный формат имени, повторите ввод")
        bot.register_next_step_handler(message, check_name)

# https://habr.com/ru/post/349860/


def add_name_user(message):
    "функция утверждения имени, просит ввести фамилию и отправляет его на проверку"
    log(message)
    global name_user
    name_user = message.text
    bot.send_message(message.chat.id, "Введите вашу фамилию:")
    bot.register_next_step_handler(message, check_surname)
    return name_user


def check_surname(message):
    "функция проверяет фамилию на соответствие шаблону, просит повторный ввод, если фамилия некорректна"
    log(message)
    regex = re.compile(r'([А-Яа-яЁё]+)')  # регулярное выражение фамилии
    surname = str(message.text)
    if re.fullmatch(regex, surname):
        add_surname_user(message)
    else:
        bot.send_message(message.chat.id, "Неверный формат фамилии, повторите ввод")
        bot.register_next_step_handler(message, check_surname)


def add_surname_user(message):
    "функция утверждает фамилию, просит ввести номер группы"
    log(message)
    global surname_user
    surname_user = message.text
    bot.send_message(message.chat.id, "Введите номер группы:")
    bot.register_next_step_handler(message, add_group_user)
    return surname_user


def add_group_user(message):
    "функция утверждает группу, завершает процесс регистрации"
    log(message)
    global group_user
    group_user = message.text
    mes = f"Вы успешно зарегистрированны! \nВаше имя: {name_user.title()} \nВаша фамилия: {surname_user.title()} \nВаша группа: {group_user.title()}"
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

# -------------------------------------------РЕЖИМ ПРЕПОДАВАТЕЛЯ-------------------------------------------
def get_password(message):
    "функция проверяет код преподавателя, при совпадении начинает процесс регистрации"
    log(message)
    get_message = message.text.strip().lower()
    if get_message == password:
        bot.send_message(message.chat.id, "Введите вашу фамилию:", reply_markup = types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_teacher_surname)
    else:
        bot.send_message(message.chat.id, "Неверный код \nПовторите попытку") # добавить выход на начало регистрации, мало ли студент зайдёт
        bot.register_next_step_handler(message, get_password)

# функции для фамилии преподавателя

def check_teacher_surname(message):
    "функция проверяет фамилию на соответствие шаблону, просит повторный ввод, если фамилия некорректна"
    log(message)
    regex = re.compile(r'([А-Яа-яЁё]+)')  # регулярное выражение фамилии
    teacher_surname = str(message.text)
    if re.fullmatch(regex, teacher_surname):
        add_teacher_surname(message)
    else:
        bot.send_message(message.chat.id, "Неверный формат фамилии, повторите ввод")
        bot.register_next_step_handler(message, check_teacher_surname)

def add_teacher_surname(message):
    "функция утверждает фамилию, просит ввести имя и отправляет его на проверку"
    log(message)
    global teacher_surname
    teacher_surname = message.text
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, check_teacher_name)
    return teacher_surname

# функции для имени преподавателя

def check_teacher_name(message):
    "функция проверяет имя на соответствие шаблону, просит повторный ввод, если имя некорректно"
    log(message)
    regex = re.compile(r'([А-Яа-яЁё]+)') # регулярное выражение для имени
    teacher_name = str(message.text)
    if re.fullmatch(regex, teacher_name):
        add_teacher_name(message)
    else:
        bot.send_message(message.chat.id, "Неверный формат имени, повторите ввод")
        bot.register_next_step_handler(message, check_teacher_name)

def add_teacher_name(message):
    "функция утверждает имя, просит ввести отчество и отправляет его на проверку"
    log(message)
    global teacher_name
    teacher_name = message.text
    bot.send_message(message.chat.id, "Введите ваше отчество:")
    bot.register_next_step_handler(message, check_teacher_patronymic)
    return teacher_name

# функции для отчества преподавателя

def check_teacher_patronymic(message):
    "функция проверяет отчество на соответствие шаблону, просит повторный ввод, если отчество некорректно"
    log(message)
    regex = re.compile(r'([А-Яа-яЁё]+)')  # регулярное выражение отчества
    teacher_patronymic = str(message.text)
    if re.fullmatch(regex, teacher_patronymic):
        add_teacher_patronymic(message)
    else:
        bot.send_message(message.chat.id, "Неверный формат отчества, повторите ввод")
        bot.register_next_step_handler(message, check_teacher_patronymic)

def add_teacher_patronymic(message):
    "функция утверждает отчество, завершает процесс регистрации"
    log(message)
    global teacher_patronymic
    teacher_patronymic = message.text
    mes = f"Вы успешно зарегистрированны! \nВаша фамилия: {teacher_surname.title()} \nВаше имя: {teacher_name.title()} \nВаше отчество: {teacher_patronymic.title()}"
    bot.send_message(message.chat.id, mes)

    if (not BotDB.user_exists(message.from_user.id)):
        try:
            BotDB.add_teacher(message.from_user.id, teacher_surname, teacher_name, teacher_patronymic)
            print("Успешно!")
            print(f"Новый преподаватель: {teacher_name}  {teacher_surname}  {teacher_patronymic} ")
        except Exception as e:
            print(e)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированны")


def register_hendlers_reg(bot):
    bot.message_handler(content_types=['text'])(get_user_text)
