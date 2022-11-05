from telebot import types
from dbsql import BotDB
from create_bot import bot
from ref import db_file
from logFile import log

BotDB = BotDB(db_file)


# ======================ТЕСТ==============================
# @bot.message_handler(commands=['test'])  # (обработчик сообщения) прописываем что отслеживает бот(/test)
def get_test(message):
    "Начало работы с тестом, функция получения названия теста"
    log(message)
    bot.send_message(message.chat.id, "Введите название теста:")
    bot.register_next_step_handler(message,
                                   drop_test)  # метод позволяющий передать введенное сообщение внутри обработчика в следующую функцию


def print_test(messange, table, id_question):
    "Функция формирования вопроса с ответами на экране + проверка баллов"
    global messagetoedit
    name_table = table
    # try:
    test = BotDB.drop_test(name_table, id_question)
    test_out = []
    for i in test[0]:
        test_out.append(i)
    test_out_num_q = "Вопрос №" + str(id_question) + "\n" + str(test_out[0])
    CB_text_1 = "A" + ":" + str(id_question) + ":" + name_table
    CB_text_2 = "B" + ":" + str(id_question) + ":" + name_table
    CB_text_3 = "C" + ":" + str(id_question) + ":" + name_table
    CB_text_4 = "D" + ":" + str(id_question) + ":" + name_table
    markup = types.InlineKeyboardMarkup()  # объявление кнопок шаблона InlineKeyboardMarkup
    # https://surik00.gitbooks.io/aiogram-lessons/content/chapter5.html
    # https://qna.habr.com/q/837981
    # InlineKeyboardMarkup — клавиатура привязанная к сообщению, изпользующая обратный вызов (callback_data)
    markup.add(types.InlineKeyboardButton(test_out[1], callback_data=CB_text_1))
    markup.add(types.InlineKeyboardButton(test_out[2], callback_data=CB_text_2))
    markup.add(types.InlineKeyboardButton(test_out[3], callback_data=CB_text_3))
    markup.add(types.InlineKeyboardButton(test_out[4], callback_data=CB_text_4))
    messagetoedit = bot.send_message(messange, test_out_num_q, reply_markup=markup)
    # markup.add(types.InlineKeyboardButton(ТЕКСТ КНОПКИ, callback_data=ТО ЧТО ПОЛУЧИТ КОЛБЕК))
    # callback_data--------->@bot.callback_query_handler
    # except:
    #     print(" print_test ошибка")


def drop_test(message):
    "Функция вывода теста на экран, нужна для вывода 1го вопроса"
    global id_question
    global balls
    balls = 0
    name_table = message.text  # принимаем сообщение, как переменную с названием таблицы
    id_question = 1  # начальный индекс вопроса
    try:
        print_test(message.chat.id, name_table, id_question)  # вызываем функцию формирования вопросов на экране
    except:  # теста нет в базе
        bot.send_message(message.chat.id,
                         "Такого теста не существует" + "\n" + "Уточните название теста в преподавателя")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    "Функция переключения вопроса, формирования результата, подсчёта баллов"
    global id_question
    global balls
    global messagetoedit
    bot.answer_callback_query(call.id)  # убирает состояние загрузки кнопки после нажатия на неё
    user_list = call.data.split(':')
    ans = "answer" + user_list[0]  # создаём строку чтобы по ней вытащить ячейку из sql таблицы
    answer = BotDB.user_answer(ans, user_list[1], user_list[2])[0]  # ответ пользователя
    max = BotDB.max_question_number(user_list[2])
    max_question = max[0]  # максимальное число вопросов в тесте
    markup = types.InlineKeyboardMarkup()  # объявление кнопок шаблона InlineKeyboardMarkup
    try:
        name_table = user_list[2]  # имя переданной бд
        test = BotDB.drop_test(name_table, id_question)
        user_answer = [test[0][0]]
        k = 1
        while k != 5:  # создаю список user_answer, который присылается пользователю, как сообщение после нажатия на кнопку ответа
            if test[0][k] == answer:
                if test[0][k] == test[0][5]:  # проверка правильный ли ответ пользователя
                    user_answer.append(test[0][k] + " ✅")
                    balls += 1
                else:
                    user_answer.append(test[0][k] + " ❌")
            else:
                user_answer.append(test[0][k])
            k += 1
        text = "Вопрос № " + str(id_question) + "\n" + str(user_answer[0]) + "\n" + str(user_answer[1]) + "\n" + (
        user_answer[2]) + "\n" + str(user_answer[3]) + "\n" + str(user_answer[4])
    except:
        print("callback_inline ошибка")

    if id_question < max_question:  # вывод результата вопроса
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=messagetoedit.message_id, text=text)
        id_question += 1
        if id_question != 1:
            print_test(call.message.chat.id, user_list[2], id_question)
    elif id_question == max_question:  # вывод результата теста
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=messagetoedit.message_id, text=text)
        # формирование результатов теста
        if balls % 10 == 1:
            bal = " балл"
        elif (balls % 10 == 2) or (balls % 10 == 3) or (balls % 10 == 4):
            bal = " баллa"
        else:
            bal = " баллов"
        text = "Результат теста: " + "\n" + str(balls) + bal + " из " + str(max_question)
        print(name_table)
        print(call.message.chat.id)
        print(balls)
        BotDB.insert_score_test(name_table, call.message.chat.id, balls)
        bot.send_message(call.message.chat.id, text,
                         reply_markup=markup)  # отправка сообщения с результатом пользователю
        id_question += 1
    else:  # тест пройден
        pass


def register_handlers_test(bot):
    bot.message_handler(commands=['test'])(get_test)
    bot.callback_query_handler(func=lambda call: True)(callback_inline)
