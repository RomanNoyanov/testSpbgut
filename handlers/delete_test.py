from create_bot import bot
from dbsql import BotDB
from ref import db_file
from handlers import importExcel

BotDB = BotDB(db_file)


@bot.message_handler(commands=['delete'])
def delete(message):
    "Функция обработки команды удаления теста и отправки подсказки преподавателю"
    if BotDB.teacher_exists(message.from_user.id):
        names_table = ""
        name_table = BotDB.drop_name_test_for_teacher(message.from_user.id)
        for i in range(len(name_table)):
            names_table += str(name_table[i][0]) + "\n"
        try:
            msg = bot.send_message(message.chat.id,
                                   "Введите название теста, который хотите удалить\nВаши ключи от тестов:\n" + names_table)
            bot.register_next_step_handler(msg, deleted)
        except:
            print("delete")
            bot.send_message(message.chat.id, "Удаление не завершено")


def deleted(message):
    "Функция удаления теста"
    try:
        name_table = message.text
        print(name_table)
        BotDB.delete_test(name_table)
        bot.send_message(message.chat.id, "Удаление успешно завершено")
    except:
        print("deleted")
        bot.send_message(message.chat.id, "Удаление не завершено")


def register_handlers_delete_test(bot):
    bot.message_handler(content_types=['delete'])(delete)