import telebot  # https://pypi.org/project/pyTelegramBotAPI/0.3.0/
from telebot import types
from create_bot import bot
from dbsql import BotDB
from ref import db_file
from handlers import test as bot_test
from handlers import registration as bot_registration
from logFile import log
from handlers import importExcel as bot_excel

BotDB = BotDB(db_file)  # адрес к бд


@bot.message_handler(commands=['start'])  # (обработчик сообщения) прописываем что отслеживает бот (/start)
def start(message):
    "функция старта, отслеживает сообщение '/start', предлагает регистрацию новому пользователю"
    log(message)
    if (not BotDB.user_exists(message.from_user.id)) and (not BotDB.teacher_exists(message.from_user.id)):
        # если в методе проверки наличия пользователя нет пользователя, то:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # объявление кнопок шаблона ReplyKeyboardMarkup
        btn1 = types.KeyboardButton("Зарегистрироваться как студент")
        btn2 = types.KeyboardButton("Зарегистрироваться как преподаватель")
        markup.add(btn1).add(btn2)  # добавляем кнопку в шаблон ПРИ НАЖАТИИ НА КНОПКУ В БОТ ОПРАВИТСЯ СООБЩЕНИЕ С ТЕКСТОМ
        mess = f'Привет,<b>{message.from_user.first_name}</b> \n Пройдем регистрацию?'
        bot.send_message(message.chat.id, mess,
                         parse_mode='html',
                         reply_markup=markup)  # arse_mode='html - режим отправки сообщения с html тэгами
    else:
        if BotDB.user_exists(message.from_user.id):
            user = BotDB.get_user(message.chat.id)  # метод, в котором получаем пользователей из бд
            for date_user in user:
                name = date_user[2]  # имя
                sur_name = date_user[3]  # фамилия
                group = date_user[4]  # группа
            mess = f"Здравствуйте, {sur_name} {name} из {group}"

        elif BotDB.teacher_exists(message.from_user.id):
            teacher = BotDB.get_teacher(message.chat.id)  # метод, в котором получаем пользователей из бд
            for date_teacher in teacher:
                teacher_surname = date_teacher[3]  # имя
                teacher_patronymic = date_teacher[4]  # отчество
            mess = f"Здравствуйте, {teacher_surname} {teacher_patronymic}"

        bot.send_message(message.chat.id, mess)


@bot.message_handler(content_types=['sticker'])  # прописываем что отслеживает бот(если пользователь отправил стикер)
def send_message_sticker(message):
    "функция, отправляющая сообщение, когда пришел стикер"
    bot.send_message(message.chat.id, 'Стикер то классный, но разве он входит в изучение предмета?')


@bot.message_handler(commands=['help'])  # (обработчик сообщения) прописываем что отслеживает бот(/help)
def sey_to_help(message):
    if BotDB.teacher_exists(message.from_user.id):
        "функция, отправляющая подсказки пользователю"
        message_help = "Основные команды:\n" + \
                       "/test - введите для начала работы с тестом\n" + \
                       "/format_test - введите для просмотра шаблона нового теста"
    elif BotDB.user_exists(message.from_user.id):
        "функция, отправляющая подсказки пользователю"
        message_help = "Основные команды:" + "\n" + "/test - введите для начала работы с тестом"
    bot.send_message(message.chat.id, message_help)


# ======================ФУНКЦИИ==============================

bot_test.register_handlers_test(bot)  # функция папке handlers запускающая обработку теста

bot_registration.register_hendlers_reg(bot)  # функция папке handlers запускающая регистрацию

bot_excel.register_hendlers_excel(bot)  # функция папке handlers запускающая обработку файла excel

if __name__ == '__main__':
    bot.polling(none_stop=True)  # бот запрашивает сообщения без интервала
