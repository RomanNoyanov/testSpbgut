import re
import time

from telebot import types

import logFile
from dbsql import BotDB
from create_bot import bot
from ref import db_file
from ref import password
from logFile import log
from handlers import test

BotDB = BotDB(db_file)

# ----------------------РЕГИСТРАЦИЯ-------------------------------------------

# Словарь для передачи данных через функции
dict_name_user_for_users = {}
dict_surname_user_for_users = {}
dict_group_user_for_users = {}

dict_name_teacher_for_teacher = {}
dict_surname_teacher_for_teacher = {}
dict_teacher_patronymic_for_teacher = {}

dict_get_password_calls = {}

reg_dict_message_to_edit = {}


def get_user_text(message):
    """Переработка текста отправленного кнопкой и запуск нужного процесса регистрации"""
    log(message)
    get_message = message.text.strip().lower()
    if get_message == "зарегистрироваться как студент":
        bot.send_message(message.chat.id,
                         "Введите ваше имя:",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_name)
    elif get_message == "зарегистрироваться как преподаватель":
        dict_get_password_calls[message.chat.id] = 0
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


def check_text(text):
    """Функция проверки текста на соответствие общему шаблону"""
    regex = re.compile(r'([А-Яа-яЁё]+)')
    a = re.fullmatch(regex, text)
    return bool(a)


def data(message):
    """Функция вывода зарегистрированные данных пользователя в настоящий момент"""
    try:
        User_data = BotDB.get_user(message.chat.id)
        mes_user = f"Вaши данные: \n" \
                   f"Ваше имя: {User_data[0][2].title()} \n" \
                   f"Ваша фамилия: {User_data[0][3].title()} \n" \
                   f"Ваша группа: {User_data[0][4].title()}"
        bot.send_message(message.chat.id, mes_user)
    except Exception as e:
        bot.send_message(message.chat.id, "Что-то пошло не так :(")
        error_string = "Ошибка registration.py --->data: " + str(e)
        logFile.log_err(message, error_string)


def check_name(message):
    """Функция проверки имени на соответствие шаблону, при несовпадении требует повторный ввод"""
    log(message)
    name = str(message.text)
    if check_text(name):
        try:
            if BotDB.user_exists(message.from_user.id):  # для изменения зарегистрированных данных
                BotDB.update_user_name(message)
                bot.send_message(message.chat.id, "Изменения успешно внесены!")
                data(message)
                D = {"Имя": "имя", "Фамилию": "фамилия",
                     "Группу": "группа", "Завершить изменения": "стоп"}
                message_to_edit = bot.send_message(message.chat.id,
                                                   text="Что бы вы хотели изменить?",
                                                   reply_markup=weather_key(D),
                                                   parse_mode='Markdown')
                reg_dict_message_to_edit[message.chat.id] = message_to_edit
            else:  # для внесения данных регистрации
                add_name_user(message)
        except Exception as e:
            bot.send_message(message.chat.id, "Что-то пошло не так :(")
            error_string = "Ошибка registration.py --->check_name: " + str(e)
            logFile.log_err(message, error_string)

    else:
        bot.send_message(message.chat.id,
                         "Неверный формат имени, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_name)


# https://habr.com/ru/post/349860/


def add_name_user(message):
    """Функция утверждения имени, просит ввести фамилию и отправляет его на проверку"""
    log(message)
    name_user = message.text
    dict_name_user_for_users[message.from_user.id] = name_user
    bot.send_message(message.chat.id,
                     "Введите вашу фамилию:")
    bot.register_next_step_handler(message, check_surname)


def check_surname(message):
    """Функция проверяет фамилию на соответствие шаблону, просит повторный ввод, если фамилия некорректна"""
    log(message)
    surname = str(message.text)
    if check_text(surname):
        try:
            if BotDB.user_exists(message.from_user.id):
                BotDB.update_user_surname(message)
                bot.send_message(message.chat.id, "Изменения успешно внесены!")
                data(message)
                D = {"Имя": "имя", "Фамилию": "фамилия",
                     "Группу": "группа", "Завершить изменения": "стоп"}
                message_to_edit = bot.send_message(message.chat.id,
                                                   text="Что бы вы хотели изменить?",
                                                   reply_markup=weather_key(D),
                                                   parse_mode='Markdown')
                reg_dict_message_to_edit[message.chat.id] = message_to_edit
            else:
                add_surname_user(message)
        except Exception as e:
            bot.send_message(message.chat.id, "Что-то пошло не так :(")
            error_string = "Ошибка registration.py --->check_surname: " + str(e)
            logFile.log_err(message, error_string)


    else:
        bot.send_message(message.chat.id,
                         "Неверный формат фамилии, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_surname)


def add_surname_user(message):
    """Функция утверждает фамилию, просит ввести номер группы"""
    log(message)
    surname_user = message.text
    dict_surname_user_for_users[message.from_user.id] = surname_user
    bot.send_message(message.chat.id,
                     "Введите номер группы:")
    bot.register_next_step_handler(message,
                                   add_group_user)


def up_group_user(message):
    try:
        BotDB.update_user_group(message)
        bot.send_message(message.chat.id, "Изменения успешно внесены!")
        data(message)
        D = {"Имя": "имя", "Фамилию": "фамилия",
             "Группу": "группа", "Завершить изменения": "стоп"}
        message_to_edit = bot.send_message(message.chat.id,
                                           text="Что бы вы хотели изменить?",
                                           reply_markup=weather_key(D),
                                           parse_mode='Markdown')
        reg_dict_message_to_edit[message.chat.id] = message_to_edit
    except Exception as e:
        bot.send_message(message.chat.id, "Что-то пошло не так :(")
        error_string = "Ошибка registration.py --->up_group_user: " + str(e)
        logFile.log_err(message, error_string)


def weather_key(dictionary):
    """Функция, отвечающая за изменение клавиатуры в зависимости от аргумента функции"""
    weather = types.InlineKeyboardMarkup(row_width=2)
    for key in dictionary:
        weather.add(types.InlineKeyboardButton(text=key, callback_data=dictionary[key]))
    return weather


def add_group_user(message):
    """Функция утверждает группу, завершает процесс регистрации"""
    log(message)

    D = {"Завершить процесс регистрации": "завершить",
         "Изменить данные": "изменить"}

    group_user = message.text
    dict_group_user_for_users[message.from_user.id] = group_user
    # reg_list[name_user,surname_user,group_user]

    name_user = str(dict_name_user_for_users.get(message.chat.id))
    surname_user = str(dict_surname_user_for_users.get(message.chat.id))
    group_user = str(dict_group_user_for_users.get(message.chat.id))

    mes = f"Ваше имя: {name_user.title()} \n" \
          f"Ваша фамилия: {surname_user.title()} \n" \
          f"Ваша группа: {group_user.title()} \n"

    reg_dict_message_to_edit[message.chat.id] = bot.send_message(message.chat.id,
                                                                 "Проверьте данные на корректность\n" + mes +
                                                                 "❗После завершения процесса регистрации " +
                                                                 "данные изменить невозможно",
                                                                 reply_markup=weather_key(D))

    if not BotDB.user_exists(message.from_user.id):
        try:
            name_user = str(dict_name_user_for_users.get(message.from_user.id))
            surname_user = str(dict_surname_user_for_users.get(message.from_user.id))
            group_user = str(dict_group_user_for_users.get(message.from_user.id))

            BotDB.add_user(message.from_user.id, name_user, surname_user, group_user)
        except Exception as e:
            bot.send_message(message.chat.id, "Что-то пошло не так :(")
            error_string = "Ошибка registration.py --->add_group_user: " + str(e)
            logFile.log_err(message, error_string)
    else:
        bot.send_message(message.chat.id,
                         "Вы уже зарегистрированны")


# -------------------------------------------РЕЖИМ ПРЕПОДАВАТЕЛЯ-------------------------------------------


def get_password(message):
    """Функция проверяет код преподавателя, при совпадении начинает процесс регистрации"""
    log(message)
    dict_get_password_calls[message.chat.id] += 1
    get_message = message.text.strip().lower()
    if get_message == password:
        bot.send_message(message.chat.id, "Введите вашу фамилию:",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_teacher_surname)
    else:
        if dict_get_password_calls[message.chat.id] < 4:
            bot.send_message(message.chat.id,
                             "Неверный код \nПовторите попытку\nОсталось попыток: "
                             + str(4 - dict_get_password_calls[message.chat.id]))
            bot.register_next_step_handler(message,
                                           get_password)
        else:
            bot.send_message(message.chat.id,
                             "Неверный код \n Начните регистрацию заново, введите /start")
            dict_get_password_calls[message.chat.id] = 0


def data_teacher(message):
    """Функция выводит зарегистрированные данные преподавателя в настоящий момент"""
    try:
        teacher_data = BotDB.get_teacher(message.chat.id)
        mes_user = f"Вaши данные: \n" \
                   f"Ваша фамилия: {teacher_data[0][2].title()} \n" \
                   f"Ваше имя: {teacher_data[0][3].title()} \n" \
                   f"Ваше отчество: {teacher_data[0][4].title()}"
        bot.send_message(message.chat.id, mes_user)
    except Exception as e:
        bot.send_message(message.chat.id, "Что-то пошло не так :(")
        error_string = "Ошибка registration.py --->data_teacher: " + str(e)
        logFile.log_err(message, error_string)


def check_teacher_surname(message):
    """Функция проверяет фамилию на соответствие шаблону, просит повторный ввод, если фамилия некорректна"""
    log(message)
    teacher_surname = str(message.text)
    if check_text(teacher_surname):
        try:
            if BotDB.teacher_exists(message.from_user.id):
                BotDB.update_teacher_surname(message)
                data_teacher(message)
                bot.send_message(message.chat.id, "Изменения успешно внесены!")
                D = {"Фамилию": "п_фамилия", "Имя": "п_имя", "Отчество": "п_отчество", "Завершить изменения": "стоп"}
                message_to_edit = bot.send_message(message.chat.id,
                                                   text="Что бы вы хотели изменить?",
                                                   reply_markup=weather_key(D),
                                                   parse_mode='Markdown')
                reg_dict_message_to_edit[message.chat.id] = message_to_edit
            else:
                add_teacher_surname(message)
        except Exception as e:
            bot.send_message(message.chat.id, "Что-то пошло не так :(")
            error_string = "Ошибка registration.py --->check_teacher_surname: " + str(e)
            logFile.log_err(message, error_string)

    else:
        bot.send_message(message.chat.id,
                         "Неверный формат фамилии, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_teacher_surname)


def add_teacher_surname(message):
    """Функция утверждает фамилию, просит ввести имя и отправляет его на проверку"""
    log(message)
    teacher_surname = message.text
    dict_surname_teacher_for_teacher[message.from_user.id] = teacher_surname
    bot.send_message(message.chat.id,
                     "Введите ваше имя:")
    bot.register_next_step_handler(message,
                                   check_teacher_name)


def check_teacher_name(message):
    """Функция проверяет имя на соответствие шаблону, просит повторный ввод, если имя некорректно"""
    log(message)
    teacher_name = str(message.text)
    if check_text(teacher_name):
        try:
            if BotDB.teacher_exists(message.from_user.id):
                BotDB.update_teacher_name(message)
                data_teacher(message)
                bot.send_message(message.chat.id, "Изменения успешно внесены!")
                D = {"Фамилию": "п_фамилия", "Имя": "п_имя", "Отчество": "п_отчество", "Завершить изменения": "стоп"}
                message_to_edit = bot.send_message(message.chat.id,
                                                   text="Что бы вы хотели изменить?",
                                                   reply_markup=weather_key(D),
                                                   parse_mode='Markdown')
                reg_dict_message_to_edit[message.chat.id] = message_to_edit
            else:
                add_teacher_name(message)
        except Exception as e:
            bot.send_message(message.chat.id, "Что-то пошло не так :(")
            error_string = "Ошибка registration.py --->check_teacher_name: " + str(e)
            logFile.log_err(message, error_string)

    else:
        bot.send_message(message.chat.id,
                         "Неверный формат имени, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_teacher_name)


def add_teacher_name(message):
    """Функция утверждает имя, просит ввести отчество и отправляет его на проверку"""
    log(message)
    teacher_name = message.text
    dict_name_teacher_for_teacher[message.from_user.id] = teacher_name
    bot.send_message(message.chat.id,
                     "Введите ваше отчество:")
    bot.register_next_step_handler(message,
                                   check_teacher_patronymic)


def check_teacher_patronymic(message):
    """Функция проверяет отчество на соответствие шаблону, просит повторный ввод, если отчество некорректно"""
    log(message)
    teacher_patronymic = str(message.text)
    if check_text(teacher_patronymic):
        try:
            if BotDB.teacher_exists(message.from_user.id):
                BotDB.update_teacher_patronymic(message)
                data_teacher(message)
                bot.send_message(message.chat.id, "Изменения успешно внесены!")
                D = {"Фамилию": "п_фамилия", "Имя": "п_имя", "Отчество": "п_отчество", "Завершить изменения": "стоп"}
                message_to_edit = bot.send_message(message.chat.id,
                                                   text="Что бы вы хотели изменить?",
                                                   reply_markup=weather_key(D),
                                                   parse_mode='Markdown')
                reg_dict_message_to_edit[message.chat.id] = message_to_edit
            else:
                add_teacher_patronymic(message)
        except Exception as e:
            bot.send_message(message.chat.id, "Что-то пошло не так :(")
            error_string = "Ошибка registration.py --->check_teacher_patronymic: " + str(e)
            logFile.log_err(message, error_string)
    else:
        bot.send_message(message.chat.id,
                         "Неверный формат отчества, повторите ввод")
        bot.register_next_step_handler(message,
                                       check_teacher_patronymic)


def add_teacher_patronymic(message):
    """Функция утверждает отчество, завершает процесс регистрации"""
    log(message)
    D = {"Завершить процесс регистрации": "п_завершить", "Изменить данные": "п_изменить"}

    teacher_patronymic = message.text
    dict_teacher_patronymic_for_teacher[message.from_user.id] = teacher_patronymic
    # reg_list_for_teacher[teacher_surname,teacher_name,teacher_patronymic]

    teacher_surname = str(dict_surname_teacher_for_teacher.get(message.chat.id)).title()
    teacher_name = str(dict_name_teacher_for_teacher.get(message.chat.id)).title()
    teacher_patronymic = str(dict_teacher_patronymic_for_teacher.get(message.chat.id)).title()
    mes = f"Вы успешно зарегистрированны! \n" \
          f"Ваша фамилия: {teacher_surname.title()} \n" \
          f"Ваше имя: {teacher_name.title()} \n" \
          f"Ваше отчество: {teacher_patronymic.title()} \n"
    reg_dict_message_to_edit[message.chat.id] = bot.send_message(message.chat.id,
                                                                 "Проверьте данные на корректность\n❗" + mes +
                                                                 "После завершения процесса регистрации " +
                                                                 "данные изменить невозможно",
                                                                 reply_markup=weather_key(D))

    if not BotDB.teacher_exists(message.from_user.id):
        try:
            teacher_surname = str(dict_surname_teacher_for_teacher.get(message.from_user.id))
            teacher_name = str(dict_name_teacher_for_teacher.get(message.from_user.id))
            teacher_patronymic = str(dict_teacher_patronymic_for_teacher.get(message.from_user.id))
            BotDB.add_teacher(message.from_user.id, teacher_surname,
                              teacher_name, teacher_patronymic)
        except Exception as e:
            bot.send_message(message.chat.id, "Что-то пошло не так :(")
            error_string = "Ошибка registration.py --->add_teacher_patronymic: " + str(e)
            logFile.log_err(message, error_string)
    else:
        bot.send_message(message.chat.id,
                         "Вы уже зарегистрированны")


# ------------------------------------------- ОБРАБОТКА КНОПОК -------------------------------------------


@bot.callback_query_handler(func=lambda call: True)
def completion_registration(call):
    """Функция обработки кнопок при регистрации"""
    data = call.data
    bot.answer_callback_query(call.id)
    if call.data == "завершить":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        name_user = str(dict_name_user_for_users.get(call.message.chat.id)).title()
        surname_user = str(dict_surname_user_for_users.get(call.message.chat.id)).title()
        group_user = str(dict_group_user_for_users.get(call.message.chat.id))

        mes = f"Вы успешно зарегистрированны! \n" \
              f"Ваше имя: {name_user.title()} \n" \
              f"Ваша фамилия: {surname_user.title()} \n" \
              f"Ваша группа: {group_user.title()}"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=message_to_edit.message_id, text=mes)
        bot.send_message(call.message.chat.id, "Для ознакомления с основными функциями бота введите\n/help")

    elif call.data == "изменить":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)

        D = {"Имя": "имя", "Фамилию": "фамилия",
             "Группу": "группа", "Завершить изменения": "стоп"}
        reg_dict_message_to_edit[call.message.chat.id] = bot.edit_message_text(chat_id=call.message.chat.id,
                                                                               message_id=message_to_edit.message_id,
                                                                               text="Что бы вы хотели изменить?",
                                                                               reply_markup=weather_key(D),
                                                                               parse_mode='Markdown')
    elif data == "имя":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        bot.delete_message(call.message.chat.id, message_to_edit.message_id)
        msg = bot.send_message(call.message.chat.id,
                               "Введите новое имя")
        bot.register_next_step_handler(msg,
                                       check_name)  # функция внесения изменений в бд
    elif data == "фамилия":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        bot.delete_message(call.message.chat.id, message_to_edit.message_id)
        msg = bot.send_message(call.message.chat.id,
                               "Введите новую фамилию")
        bot.register_next_step_handler(msg,
                                       check_surname)  # функция внесения изменений в бд
    elif data == "группа":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        bot.delete_message(call.message.chat.id, message_to_edit.message_id)
        msg = bot.send_message(call.message.chat.id,
                               "Введите новую группу")
        bot.register_next_step_handler(msg,
                                       up_group_user)  # функция внесения изменений в бд
    elif data == "стоп":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        reg_dict_message_to_edit[call.message.chat.id] = bot.edit_message_text(chat_id=call.message.chat.id,
                                                                               message_id=message_to_edit.message_id,
                                                                               text="Изменения завершены")
        bot.send_message(call.message.chat.id,
                         "Для ознакомления с основными функциями бота введите\n/help")

    elif call.data == "п_завершить":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        teacher_surname = str(dict_surname_teacher_for_teacher.get(call.message.chat.id))
        teacher_name = str(dict_name_teacher_for_teacher.get(call.message.chat.id))
        teacher_patronymic = str(dict_teacher_patronymic_for_teacher.get(call.message.chat.id))
        mes = f"Вы успешно зарегистрированны! \n" \
              f"Ваша фамилия: {teacher_surname.title()} \n" \
              f"Ваше имя: {teacher_name.title()} \n" \
              f"Ваше отчество: {teacher_patronymic.title()}"

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=message_to_edit.message_id,
                              text=mes)

        bot.send_message(call.message.chat.id, "Для ознакомления с основными функциями бота введите\n/help")

    elif call.data == "п_изменить":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        D = {"Фамилию": "п_фамилия", "Имя": "п_имя", "Отчество": "п_отчество", "Завершить изменения": "стоп"}
        reg_dict_message_to_edit[call.message.chat.id] = bot.edit_message_text(chat_id=call.message.chat.id,
                                                                               message_id=message_to_edit.message_id,
                                                                               text="Что бы вы хотели изменить?",
                                                                               reply_markup=weather_key(D),
                                                                               parse_mode='Markdown')

    elif data == "п_имя":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        bot.delete_message(call.message.chat.id, message_to_edit.message_id)
        msg = bot.send_message(call.message.chat.id,
                               "Введите новое имя")
        bot.register_next_step_handler(msg,
                                       check_teacher_name)  # функция внесения в бд
    elif data == "п_фамилия":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        bot.delete_message(call.message.chat.id, message_to_edit.message_id)
        msg = bot.send_message(call.message.chat.id,
                               "Введите новую фамилию")
        bot.register_next_step_handler(msg,
                                       check_teacher_surname)  # функция внесения в бд
    elif data == "п_отчество":
        message_to_edit = reg_dict_message_to_edit.get(call.message.chat.id)
        bot.delete_message(call.message.chat.id, message_to_edit.message_id)
        msg = bot.send_message(call.message.chat.id,
                               "Введите новое отчество")
        bot.register_next_step_handler(msg,
                                       check_teacher_patronymic)
    else:
        test.callback_inline(call)


def register_handlers_reg(bot):
    bot.message_handler(content_types=['text'])(get_user_text)
