import telebot  # https://pypi.org/project/pyTelegramBotAPI/0.3.0/
from telebot import types
from create_bot import bot
from dbsql import BotDB
from ref import db_file
from handlers import test as bot_test
from handlers import registration as bot_registration
from logFile import log
from  handlers import importExcel as bot_excel
BotDB = BotDB(db_file)  # адрес  к бд
@bot.message_handler(commands=['start'])  # (обработчик сообщения) прописываем что отслеживает бот (/start)
def start(message):  # функция старт (сообщение)
    log(message)
    if (not BotDB.user_exists(message.from_user.id)):
        # если в методе проверки наличия пользователя нет пользователя, то:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # объявление кнопок шаблона ReplyKeyboardMarkup
        button_reg = types.KeyboardButton('Регистрация')  # кнопка с текстом
        markup.add(button_reg)  # добавляем кнопку в шаблон ПРИ НАЖАТИЕ НА КНОПКУ В БОТ ОПРАВИТСЯ СООБЩЕНИЕ С ТЕКСТОМ
        mess = f'Привет,<b>{message.from_user.first_name}</b> \n Пройдем регистрацию?'
        print(BotDB.user_exists(message.from_user.id))
        bot.send_message(message.chat.id, mess,
                         parse_mode='html',
                         reply_markup=markup)  # arse_mode='html - режим отправки сообщения с html тэгами
    else:
        user = BotDB.get_user(message.chat.id)  # медот в котором получяем пользователей из бд
        for date_user in user:
            name = date_user[2]  # имя
            sur_name = date_user[3]  # фамилия
            group = date_user[4]  # группа
        mess = f"Здравствуйте,{sur_name} {name} из {group}"
        bot.send_message(message.chat.id, mess)


@bot.message_handler(content_types=['sticker'])  # прописываем что отслеживает бот(если пользователь отправил стикер)
def send_message_sticker(message):
    bot.send_message(message.chat.id, 'Стикер то классный, но разве он входит в изучение предмета?')
    # отправляет сообщение, когда пришел стикер


@bot.message_handler(commands=['help'])  # (обработчик сообщения) прописываем что отслеживает бот(/help)
# Здесь должны быть подсказки пользователю
def sey_to_help(message):
    message_help = "Основыне команды:" + "\n" + "/test - введите для начала теста"
    bot.send_message(message.chat.id, message_help)

# ======================ФУНУЦИИ==============================

bot_test.register_handlers_test(bot)  # функция папке handlers запкскающая обработку теста

bot_registration.register_hendlers_reg(bot) # функция папке handlers запкскающая регистрацию

bot_excel.register_hendlers_excel(bot)  # функция папке handlers запкскающая обработку файла excel


if __name__=='__main__':
    bot.polling(none_stop=True) # бот запращивает сообщения без интервала

