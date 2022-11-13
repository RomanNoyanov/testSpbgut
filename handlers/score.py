from dbsql import BotDB
from create_bot import bot
from ref import db_file

BotDB = BotDB(db_file)


def drop_score(message):
    if BotDB.teacher_exists(message.from_user.id):
        names_table=""
        name_table=BotDB.drop_name_test_for_teacher(message.from_user.id)
        for i in range(len(name_table)):
            names_table += str(name_table[i][0]) + "\n"


        bot.send_message(message.chat.id, "Введите ключ от теста для получения баллов\nВаши ключи от тестов:\n"+names_table)
        bot.register_next_step_handler(message, print_score_for_teacher)
    else:
        bot.send_message(message.chat.id, "Введите ключ от теста для получения баллов")
        bot.register_next_step_handler(message, print_score_for_teacher)


def print_score_for_user(message):
    "Функция для вывода персональной оценки за тест"
    name_table = message.text
    name_table_score = name_table + "_score"
    if (BotDB.check_test_in_db(name_table_score)):
        score = BotDB.drop_score_for_user(name_table, message.chat.id, )
        bot.send_message(message.chat.id, f"Ваши баллы за тест {name_table}: {score[0]}")
    else:
        bot.send_message(message.chat.id, "Такого теста не существует")


def print_score_for_teacher(message):
    "Функция для вывода всех оценок учеников за тест"
    max_balls = BotDB.max_question_number(message.text)
    score = "Название теста: " + message.text + "\n" + "Максимальное количество баллов за тест: " + str(max_balls[0]) + "\n"
    name_table = message.text
    name_table_score = name_table + "_score"
    if (BotDB.check_test_in_db(name_table_score)):
        scor = BotDB.drop_score_for_teacher(name_table)
        for i in range(len(scor)):
            for j in range(4):
                if j == 3:
                    score += "БАЛЛЫ ЗА ТЕСТ: " + str(scor[i][j])
                else:
                    score += str(scor[i][j]) + " "
            score += "\n"

        bot.send_message(message.chat.id, f" {score}")
    else:
        bot.send_message(message.chat.id, "Такого теста не существует")


def register_handlers_score(bot):
    bot.message_handler(commands=['score'])(drop_score)
