from telebot import types
from dbsql import BotDB
from create_bot import bot
from ref import db_file
from logFile import log

BotDB = BotDB(db_file)

# Словарь для передачи данных через функции
test_dict_message_to_edit = {}
dict_id_question = {}
dict_balls = {}
dict_text = {}


# ======================ТЕСТ==============================
# @bot.message_handler(commands=['test'])  # (обработчик сообщения) прописываем что отслеживает бот(/test)
def get_test(message):
    "Начало работы с тестом, функция получения названия теста"
    log(message)
    if (BotDB.teacher_exists(message.from_user.id)) or (BotDB.user_exists(message.from_user.id)):
        bot.send_message(message.chat.id, "Введите название теста:")
        bot.register_next_step_handler(message,
                                       drop_test)
        # метод позволяющий передать введенное сообщение внутри обработчика в следующую функцию
    else:
        bot.send_message(message.chat.id, "Для прохождения теста пройдите регистрацию: введите /start")


def print_test(message_chat_id, name_table, id_question):
    "Функция формирования вопроса с ответами на экране + проверка баллов"
    test = BotDB.drop_test(name_table, id_question)
    test_out = []
    for i in test[0]:
        test_out.append(i)
    test_out_num_q = "Вопрос №" + str(id_question) + "\n" + str(test_out[0])
    keyboard_button_text_1 = "A" + ":" + str(id_question) + ":" + name_table
    keyboard_button_text_2 = "B" + ":" + str(id_question) + ":" + name_table
    keyboard_button_text_3 = "C" + ":" + str(id_question) + ":" + name_table
    keyboard_button_text_4 = "D" + ":" + str(id_question) + ":" + name_table
    markup = types.InlineKeyboardMarkup()  # объявление кнопок шаблона InlineKeyboardMarkup
    # https://surik00.gitbooks.io/aiogram-lessons/content/chapter5.html
    # https://qna.habr.com/q/837981
    # InlineKeyboardMarkup — клавиатура привязанная к сообщению, изпользующая обратный вызов (callback_data)
    markup.add(types.InlineKeyboardButton(test_out[1], callback_data=keyboard_button_text_1))
    markup.add(types.InlineKeyboardButton(test_out[2], callback_data=keyboard_button_text_2))
    markup.add(types.InlineKeyboardButton(test_out[3], callback_data=keyboard_button_text_3))
    markup.add(types.InlineKeyboardButton(test_out[4], callback_data=keyboard_button_text_4))
    test_dict_message_to_edit[message_chat_id] = bot.send_message(message_chat_id, test_out_num_q, reply_markup=markup)
    # markup.add(types.InlineKeyboardButton(ТЕКСТ КНОПКИ, callback_data=ТО ЧТО ПОЛУЧИТ КОЛБЕК))
    # callback_data--------->@bot.callback_query_handler


def drop_test(message):
    "Функция вывода теста на экран, нужна для вывода 1го вопроса"
    dict_balls[message.chat.id] = 0
    name_table = message.text  # принимаем сообщение, как переменную с названием таблицы
    dict_id_question[message.chat.id] = 1  # начальный индекс вопроса

    try:
        print_test(message.chat.id, name_table, dict_id_question.get(message.chat.id))
        # вызываем функцию формирования вопросов на экране
    except:  # теста нет в базе
        msg = bot.send_message(message.chat.id,
                               "Такого теста не существует" + "\n" + "Уточните название теста у преподавателя" + "\n"
                               + "и повторите ввод")
        bot.register_next_step_handler(msg, drop_test)  # ожидает сообщение пользователя и вызывает функцию


def callback_inline(call):
    "Функция переключения вопроса, формирования результата, подсчёта баллов"
    bot.answer_callback_query(call.id)  # убирает состояние загрузки кнопки после нажатия на неё
    user_list = call.data.split(':')
    ans = "answer" + user_list[0]  # создаём строку чтобы по ней вытащить ячейку из sql таблицы
    answer = BotDB.user_answer(ans, user_list[1], user_list[2])[0]  # ответ пользователя
    max = BotDB.max_question_number(user_list[2])
    max_question = max[0]  # максимальное число вопросов в тесте
    markup = types.InlineKeyboardMarkup()  # объявление кнопок шаблона InlineKeyboardMarkup
    try:
        name_table = user_list[2]  # имя переданной бд
        test = BotDB.drop_test(name_table, dict_id_question.get(call.message.chat.id))
        user_answer = [test[0][0]]
        k = 1
        while k != 5:
            # создаю список user_answer, который присылается пользователю, как сообщение после нажатия на кнопку ответа
            if test[0][k] == answer:
                if test[0][k] == test[0][5]:  # проверка правильный ли ответ пользователя
                    user_answer.append(test[0][k] + " ✅")
                    dict_balls[call.message.chat.id] = dict_balls.get(call.message.chat.id) + 1
                else:
                    user_answer.append(test[0][k] + " ❌")
            else:
                user_answer.append(test[0][k])
            k += 1
        dict_text[call.message.chat.id] = "Вопрос № " + str(dict_id_question.get(call.message.chat.id)) + "\n" \
                                          + str(user_answer[0]) + "\n" + str(user_answer[1]) + "\n" \
                                          + (user_answer[2]) + "\n" + str(user_answer[3]) + "\n" + str(user_answer[4])
    except:
        print("callback_inline ошибка")
    message_to_edit = test_dict_message_to_edit.get(call.message.chat.id)
    if dict_id_question.get(call.message.chat.id) < max_question:  # вывод результата вопроса
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=message_to_edit.id,
                              text=dict_text.get(call.message.chat.id))

        dict_id_question[call.message.chat.id] = dict_id_question.get(call.message.chat.id) + 1
        if dict_id_question.get(call.message.chat.id) != 1:
            print_test(call.message.chat.id, user_list[2], dict_id_question.get(call.message.chat.id))
    elif dict_id_question.get(call.message.chat.id) == max_question:  # вывод результата теста
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=message_to_edit.id,
                              text=dict_text.get(call.message.chat.id))

        # формирование результатов теста
        if dict_balls.get(call.message.chat.id) % 10 == 1:
            bal = " балл"
        elif (dict_balls.get(call.message.chat.id) % 10 == 2) \
                or (dict_balls.get(call.message.chat.id) % 10 == 3) \
                or (dict_balls.get(call.message.chat.id) % 10 == 4):
            bal = " баллa"
        else:
            bal = " баллов"
        dict_text[call.message.chat.id] = "Результат теста: " + "\n" \
                                          + str(dict_balls.get(call.message.chat.id)) + bal + " из " + str(max_question)
        BotDB.insert_score_test(name_table, call.message.chat.id, dict_balls.get(call.message.chat.id))
        bot.send_message(call.message.chat.id, dict_text.get(call.message.chat.id),
                         reply_markup=markup)  # отправка сообщения с результатом пользователю
        dict_id_question[call.message.chat.id] = dict_id_question.get(call.message.chat.id) + 1


def register_handlers_test(bot):
    bot.message_handler(commands=['test'])(get_test)
