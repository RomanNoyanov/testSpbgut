from create_bot import bot
from dbsql import BotDB
from ref import db_file
from logFile import log

BotDB = BotDB(db_file)


def drop_file(message):
    "Функция для вывода шаблона теста"
    if BotDB.teacher_exists(message.from_user.id):
        file = open("files/Pattern_test_Excel.xlsx", "rb")
        bot.send_document(message.chat.id, file)


def register_handlers_dropPatternTest(bot):
    bot.message_handler(commands=['pattern'])(drop_file)