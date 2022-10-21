from telebot import types
from dbsql import BotDB
from create_bot import bot
from ref import db_file
BotDB = BotDB(db_file)
# ======================ТЕСТ==============================
#@bot.message_handler(commands=['test'])  # (обработчик сообщения) прописываем что отслеживает бот(/test)
# Начало работы с тестом, функция получения назваия теста
# Начало работы с тестом, функция получения назваия теста
def get_test(message):
    bot.send_message(message.chat.id, "Введите название теста:")
    bot.register_next_step_handler(message, drop_test)
    # медот позволяющий передать введенное сообщение внутри обработчика в следующую функцию


def print_test(messange, table, id_question):
    name_table = table
    # try:
    test = BotDB.drop_test(name_table, id_question)
    test_out = []
    for i in test[0]:
        test_out.append(i)
    test_out_num_q = "Вопрос №" + str(id_question) + "\n" + str(test_out[0])
    CB_text_1 = str(test_out[1]) + ":" + str(id_question) + ":" + name_table
    CB_text_2 = str(test_out[2]) + ":" + str(id_question) + ":" + name_table
    CB_text_3 = str(test_out[3]) + ":" + str(id_question) + ":" + name_table
    CB_text_4 = str(test_out[4]) + ":" + str(id_question) + ":" + name_table
    markup = types.InlineKeyboardMarkup() # объявление кнопок шаблона InlineKeyboardMarkup
    # https://surik00.gitbooks.io/aiogram-lessons/content/chapter5.html
    #https://qna.habr.com/q/837981
    # InlineKeyboardMarkup — клавиатура привязанная к сообщению, изпользующая обратный вызов (callback_data)
    markup.add(types.InlineKeyboardButton(test_out[1], callback_data=CB_text_1))
    markup.add(types.InlineKeyboardButton(test_out[2], callback_data=CB_text_2))
    markup.add(types.InlineKeyboardButton(test_out[3], callback_data=CB_text_3))
    markup.add(types.InlineKeyboardButton(test_out[4], callback_data=CB_text_4))
    bot.send_message(messange, test_out_num_q, reply_markup=markup)
    # markup.add(types.InlineKeyboardButton(ТЕКСТ КНОПКИ, callback_data=ТО ЧТО ПОЛУЧИТ КОЛБЕК))
    # callback_data--------->@bot.callback_query_handler
    # except:
    #     print(" print_test ошибка")

# Функция вывода теста на экран
def drop_test(message): # нужно для вывода 1го вопроса
    global id_question
    global balls
    balls = 0
    name_table = message.text # принимаем сообщение, как переменную с названием таблицы
    print(name_table) # просто для проверки вводимых данных  УДАЛИТЬ ПОСЛЕ ПРОВЕРОК !
    id_question = 1
    # try:
    print_test(message.chat.id, name_table, id_question = 1)
    # except:
    #     bot.send_message(message.chat.id,
    #                      "Такого теста не существует" + "\n" + "Уточните название теста в преподавателя")
    #     print("drop_test ошибка")


@bot.callback_query_handler(func=lambda call: True)
# эта функция переклюния вопроса
def callback_inline(call):
    global id_question
    global balls
    bot.answer_callback_query(call.id) # убирает состояние загрузки кнопки после нажатия на неё
    user_list = call.data.split(':')
    answer = user_list[0]
    max = BotDB.max_question_number(user_list[2])
    max_question = max[0] # максимальное число вопросов в тесте
    markup = types.InlineKeyboardMarkup() # объявление кнопок шаблона InlineKeyboardMarkup
    try:
        name_table = user_list[2]  # имя переданной бд
        test = BotDB.drop_test(name_table, id_question)
        user_answer = [test[0][0]]
        k = 1
        while k != 5:  # создаю список user_answer, который присылается пользователю, как сообщение после нажатия на кнопку ответа
            if test[0][k] == answer:
                if test[0][k] == test[0][5]:
                    user_answer.append(test[0][k] + " ✅")
                    balls+=1
                else:
                    user_answer.append(test[0][k] + " ❌")
            else:
                user_answer.append(test[0][k])
            k += 1
        text = "Вопрос № " + str(id_question) + "\n" + str(user_answer[0]) + "\n" + str(user_answer[1]) + "\n" + (user_answer[2]) + "\n" + str(user_answer[3]) + "\n" + str(user_answer[4])
    except:
        print("check_test ошибка")

    if id_question < max_question:
        bot.send_message(call.message.chat.id, text, reply_markup=markup)
        id_question += 1
        if id_question != 1:
            print_test(call.message.chat.id, "It_questions_table",id_question)
    elif id_question == max_question:
        bot.send_message(call.message.chat.id, text, reply_markup=markup)
        if balls % 10 == 1:
            bal = " балл"
        elif (balls % 10 == 2) or (balls % 10 == 3) or (balls % 10 == 4):
            bal = " баллa"
        else:
            bal =" баллов"
        text = "Результат теста: " + "\n" + str(balls) + bal
        bot.send_message(call.message.chat.id, text, reply_markup=markup)
        id_question += 1
    else: # тест уже прошли
        pass


def register_handlers_test(bot):
    bot.message_handler(commands=['test'])(get_test)
    bot.callback_query_handler(func=lambda call: True)(callback_inline)
