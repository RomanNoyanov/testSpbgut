import re
from telebot import types
from dbsql import BotDB
from create_bot import bot
from ref import db_file
from ref import password
from logFile import log
from handlers import test

BotDB = BotDB(db_file)

# @bot.message_handler(content_types=['text'])  # (обработчик сообщения)
# ----------------------РЕГИСТРАЦИЯ-------------------------------------------


def get_user_text(message):
    "переработка текста отправленного кнопкой и запуск нужного процесса регистрации"
    log(message)
    get_message = message.text.strip().lower()
    if get_message == "зарегистрироваться как студент":
        bot.send_message(message.chat.id,
                         "Введите ваше имя:",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message,
                                       check_name)
    elif get_message == "зарегистрироваться как преподаватель":
        bot.send_message(message.chat.id,
                         "Введите код доступа:",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message,
                                       get_password)
    elif get_message == 'мой id':
        bot.send_message(message.chat.id,
                         message.from_user.id)
    else:
        bot.send_message(message.chat.id,
                         "Не понял вас \nДля знакомства с основными командами бота введите /help")


def chek_text(text):
    "функция проверки теста на соответствие общему шаблону"
    regex = re.compile(r'([А-Яа-яЁё]+)')
    a = re.fullmatch(regex, text)
    return bool(a)


def check_name(message):
    "функция проверки имени на соответствие шаблону, при несовпадении требует повторный ввод"
    log(message)
    name = str(message.text)
    if chek_text(name):
        if BotDB.user_exists(message.from_user.id): #для изменения зарегистрированных данных данных
            BotDB.update_user_name(message)
        else: # для внесения данных регистрации
            add_name_user(message)
    else:
        bot.send_message(message.chat.id,
                         "Неверный формат имени, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_name)

# https://habr.com/ru/post/349860/


def add_name_user(message):
    "функция утверждения имени, просит ввести фамилию и отправляет его на проверку"
    log(message)
    global name_user
    name_user = message.text
    bot.send_message(message.chat.id,
                     "Введите вашу фамилию:")
    bot.register_next_step_handler(message, check_surname)
    return name_user


def check_surname(message):
    "функция проверяет фамилию на соответствие шаблону, просит повторный ввод, если фамилия некорректна"
    log(message)
    surname = str(message.text)
    if chek_text(surname):
        if BotDB.user_exists(message.from_user.id):
            BotDB.update_user_surname(message)
        else:
            add_surname_user(message)
    else:
        bot.send_message(message.chat.id,
                         "Неверный формат фамилии, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_surname)


def add_surname_user(message):
    "функция утверждает фамилию, просит ввести номер группы"
    log(message)
    global surname_user
    surname_user = message.text
    bot.send_message(message.chat.id,
                     "Введите номер группы:")
    bot.register_next_step_handler(message,
                                   add_group_user)
    return surname_user


def weather_key(dictionary):
    "функция, отвечающая за динамическое изменение клавиатуры"
    weather = types.InlineKeyboardMarkup(row_width=2)
    for key in dictionary:
        weather.add(types.InlineKeyboardButton(text=key,
                                               callback_data=dictionary[key]))
    return weather


def add_group_user(message):
    "функция утверждает группу, завершает процесс регистрации"
    log(message)
    global group_user
    global messagetoedit
    D = {"Завершить процесс регистрации": "завершить",
         "Изменить данные":"изменить"}
    messagetoedit = bot.send_message(message.chat.id,
                                     "Проверьте данные на корректность\n❗После завершения процесса регистрации данные изменить невозможно",
                                     reply_markup = weather_key(D))
    group_user = message.text

    if not BotDB.user_exists(message.from_user.id):
        try:
            BotDB.add_user(message.from_user.id, name_user,
                                    surname_user, group_user)
        except Exception as e:
            print(e)
    else:
        bot.send_message(message.chat.id,
                         "Вы уже зарегистрированны")


# -------------------------------------------РЕЖИМ ПРЕПОДАВАТЕЛЯ-------------------------------------------
def get_password(message):
    "функция проверяет код преподавателя, при совпадении начинает процесс регистрации"
    log(message)
    get_message = message.text.strip().lower()
    if get_message == password:
        bot.send_message(message.chat.id, "Введите вашу фамилию:",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_teacher_surname)
    else:
        bot.send_message(message.chat.id,
                         "Неверный код \nПовторите попытку")  # добавить выход на начало регистрации, мало ли студент зайдёт
        bot.register_next_step_handler(message,
                                       get_password)


def check_teacher_surname(message):
    "функция проверяет фамилию на соответствие шаблону, просит повторный ввод, если фамилия некорректна"
    log(message)
    teacher_surname = str(message.text)
    if chek_text(teacher_surname):
        if BotDB.teacher_exists(message.from_user.id):
            BotDB.update_teacher_surname(message)

        else:
            add_teacher_surname(message)
    else:
        bot.send_message(message.chat.id,
                         "Неверный формат фамилии, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_teacher_surname)


def add_teacher_surname(message):
    "функция утверждает фамилию, просит ввести имя и отправляет его на проверку"
    log(message)
    global teacher_surname
    teacher_surname = message.text
    bot.send_message(message.chat.id,
                     "Введите ваше имя:")
    bot.register_next_step_handler(message,
                                   check_teacher_name)
    return teacher_surname


def check_teacher_name(message):
    "функция проверяет имя на соответствие шаблону, просит повторный ввод, если имя некорректно"
    log(message)
    teacher_name = str(message.text)
    if chek_text(teacher_name):
        if BotDB.teacher_exists(message.from_user.id):
            BotDB.update_teacher_name(message)
        else:
            add_teacher_name(message)
    else:
        bot.send_message(message.chat.id,
                         "Неверный формат имени, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_teacher_name)


def add_teacher_name(message):
    "функция утверждает имя, просит ввести отчество и отправляет его на проверку"
    log(message)
    global teacher_name
    teacher_name = message.text
    bot.send_message(message.chat.id,
                     "Введите ваше отчество:")
    bot.register_next_step_handler(message,
                                   check_teacher_patronymic)
    return teacher_name


def check_teacher_patronymic(message):
    "функция проверяет отчество на соответствие шаблону, просит повторный ввод, если отчество некорректно"
    log(message)
    teacher_patronymic = str(message.text)
    if chek_text(teacher_patronymic):
        if BotDB.teacher_exists(message.from_user.id):
            BotDB.update_teacher_patronymic(message)
        else:
            add_teacher_patronymic(message)
    else:
        bot.send_message(message.chat.id,
                         "Неверный формат отчества, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_teacher_patronymic)


def add_teacher_patronymic(message):
    "функция утверждает отчество, завершает процесс регистрации"
    log(message)
    global teacher_patronymic
    global messagetoedit
    D = {"Завершить процесс регистрации": "п_завершить", "Изменить данные": "п_изменить"}
    messagetoedit = bot.send_message(message.chat.id,
                                     "Проверьте данные на корректность\n❗После завершения процесса регистрации данные изменить невозможно",
                                     reply_markup=weather_key(D))
    teacher_patronymic = message.text

    if (not BotDB.teacher_exists(message.from_user.id)):
        try:
            BotDB.add_teacher(message.from_user.id, teacher_surname,
                              teacher_name, teacher_patronymic)
            print("Успешно!")
            print(f"Новый преподаватель: {teacher_name}  {teacher_surname}  {teacher_patronymic} ")
        except Exception as e:
            print(e)
    else:
        bot.send_message(message.chat.id,
                         "Вы уже зарегистрированны")


@bot.callback_query_handler(func=lambda call: True)
def completion_registration(call):
    "функция обработки кнопок при регистрации"
    global messagetoedit
    global name_user
    global surname_user
    global group_user
    global teacher_surname
    global teacher_name
    global teacher_patronomic
    print(call)
    data = call.data
    bot.answer_callback_query(call.id)
    if call.data == "завершить":
        mes = f"Вы успешно зарегистрированны! \nВаше имя: {name_user.title()} \nВаша фамилия: {surname_user.title()} \nВаша группа: {group_user.title()}"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=messagetoedit.message_id, text=mes)
        bot.send_message(call.message.chat.id, "Для ознакомления с основными функциями бота введите\n/help")

    elif call.data == "изменить":
        D = {"Имя": "имя", "Фамилию": "фамилия",
             "Группу": "группа", "Завершить изменения": "стоп"}
        messagetoedit = bot.edit_message_text(chat_id=call.message.chat.id, message_id=messagetoedit.message_id,
                                              text="Что бы вы хотели изменить?", reply_markup=weather_key(D),
                                              parse_mode='Markdown')
    elif data == "имя":
        msg = bot.send_message(call.message.chat.id,
                               "Введите новое имя")
        bot.register_next_step_handler(msg,
                                       check_name)# функция внесения изменений в бд
    elif data == "фамилия":
        msg = bot.send_message(call.message.chat.id,
                               "Введите новую фамилию")
        bot.register_next_step_handler(msg,
                                       check_surname) # функция внесения изменений в бд
    elif data == "группа":
        msg = bot.send_message(call.message.chat.id,
                               "Введите новую группу")
        bot.register_next_step_handler(msg,
                                       BotDB.update_user_group) # функция внесения изменений в бд
    elif data == "стоп":
        messagetoedit = bot.edit_message_text(chat_id=call.message.chat.id,
                                              message_id=messagetoedit.message_id,
                                              text="Изменения завершены")
        bot.send_message(call.message.chat.id,
                         "Для ознакомления с основными функциями бота введите\n/help")

    elif call.data == "п_завершить":
        mes = f"Вы успешно зарегистрированны! \nВаша фамилия: {teacher_surname.title()} \nВаше имя: {teacher_name.title()} \nВаше отчество: {teacher_patronymic.title()}"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=messagetoedit.message_id,
                              text=mes)
        bot.send_message(call.message.chat.id, "Для ознакомления с основными функциями бота введите\n/help")

    elif call.data == "п_изменить":
        D = {"Фамилию": "п_фамилия","Имя": "п_имя", "Отчество": "п_отчество", "Завершить изменения": "стоп"}
        messagetoedit = bot.edit_message_text(chat_id=call.message.chat.id, message_id=messagetoedit.message_id,
                                              text="Что бы вы хотели изменить?", reply_markup=weather_key(D),
                                              parse_mode='Markdown')
    elif data == "п_имя":
        msg = bot.send_message(call.message.chat.id,
                               "Введите новое имя")
        bot.register_next_step_handler(msg,
                                       check_teacher_name)  # функция внесения в бд
    elif data == "п_фамилия":
        msg = bot.send_message(call.message.chat.id,
                               "Введите новую фамилию")
        bot.register_next_step_handler(msg,
                                       check_teacher_surname)  # функция внесения в бд
    elif data == "п_отчество":
        msg = bot.send_message(call.message.chat.id,
                               "Введите новое отчество")
        bot.register_next_step_handler(msg,
                                       check_teacher_patronymic)
    else:
        test.callback_inline(call)


def register_handlers_reg(bot):
    bot.message_handler(content_types=['text'])(get_user_text)
    #@bot.callback_query_handler(func=lambda call: True)(completion_registration)
