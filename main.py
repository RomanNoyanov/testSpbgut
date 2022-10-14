import telebot  # https://pypi.org/project/pyTelegramBotAPI/0.3.0/
from telebot import types

from dbsql import BotDB
from ref import token

BotDB = BotDB('test_spbgut.db')  # адрес  к бд
bot = telebot.TeleBot(token)  # ссылка на токин для соединения с ботом


@bot.message_handler(commands=['start'])  # (обработчик сообщения) прописываем что отслеживает бот (/start)
def start(message):  # функция старт (сообщение)
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
    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # but = types.KeyboardButton("кнопка")
    # start = types.KeyboardButton("Старт")
    # markup.add(but, start)
    # bot.send_message(message.chat.id, "вот кнопки", reply_markup=markup)


# ======================ТЕСТ==============================
@bot.message_handler(commands=['test'])  # (обработчик сообщения) прописываем что отслеживает бот(/test)
# Начало работы с тестом, функция получения назваия теста
def get_test(message):
    bot.send_message(message.chat.id, "Введите название теста:")
    bot.register_next_step_handler(message, drop_test)
    # медот позволяющий передать введенное сообщение внутри обработчика в следующую функцию


# Функция вывода теста на экран
def drop_test(message):
    name_table = message.text  # принимаем сообщение, как переменную с названием таблицы
    print(name_table)  # просто для проверки вводимых данных  УДАЛИТЬ ПОСЛЕ ПРОВЕРОК !
    id_question = 1
    try:
        print(BotDB.drop_test(name_table, id_question))  # просто для проверки вводимых данных  УДАЛИТЬ ПОСЛЕ ПРОВЕРОК !
        test = BotDB.drop_test(name_table, id_question)
        print(test[0])  # просто для проверки вводимых данных  УДАЛИТЬ ПОСЛЕ ПРОВЕРОК !
        test_out = []
        for i in test[0]:
            test_out.append(i)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
        # Надо что-то придумать и сделать красивым код
        # + добавить счетчик вопроса и баллов
        # !!!!!!!!!!!!!!!!!!!!!!!!
        CB_text_1 = str(test_out[1]) + ":" + str(id_question) + ":" + name_table
        CB_text_2 = str(test_out[2]) + ":" + str(id_question) + ":" + name_table
        CB_text_3 = str(test_out[3]) + ":" + str(id_question) + ":" + name_table
        CB_text_4 = str(test_out[4]) + ":" + str(id_question) + ":" + name_table
        print(CB_text_1)  # просто для проверки вводимых данных  УДАЛИТЬ ПОСЛЕ ПРОВЕРОК !

        markup = types.InlineKeyboardMarkup()  # # объявление кнопок шаблона InlineKeyboardMarkup
        # https://surik00.gitbooks.io/aiogram-lessons/content/chapter5.html
        #https://qna.habr.com/q/837981
        # InlineKeyboardMarkup — клавиатура привязанная к сообщению, изпользующая обратный вызов (callback_data)
        markup.add(types.InlineKeyboardButton(test_out[1], callback_data=CB_text_1))
        markup.add(types.InlineKeyboardButton(test_out[2], callback_data=CB_text_2))
        markup.add(types.InlineKeyboardButton(test_out[3], callback_data=CB_text_3))
        markup.add(types.InlineKeyboardButton(test_out[4], callback_data=CB_text_4))
        bot.send_message(message.chat.id, test_out[0], reply_markup=markup)
        # markup.add(types.InlineKeyboardButton(ТЕКСТ КНОПКИ, callback_data=ТО ЧТО ПОЛУЧИТ КОЛБЕК))
        # callback_data--------->@bot.callback_query_handler

    except:

        bot.send_message(message.chat.id,
                         "Такого теста не существует" + "\n" + "Уточните название теста в преподавателя")
        print("drop_test ошибка")


@bot.callback_query_handler(func=lambda call: call.data.split(":"))
# Через callback_query_handler отлавливаете нажатие на кнопку, и потом делаете обработку этого нажатия

def check_test(call):
    call = call.data.split(":", 3)
    print(call)  # ['1980', '1', 'It_questions_table'] просто для проверки вводимых данных  УДАЛИТЬ ПОСЛЕ ПРОВЕРОК !
    print(call[1])  # НОМЕР ВОПРОСА  1 просто для проверки вводимых данных  УДАЛИТЬ ПОСЛЕ ПРОВЕРОК !
    print(call[0])  # 1980  просто для проверки вводимых данных  УДАЛИТЬ ПОСЛЕ ПРОВЕРОК !
    print(call[2])  # НАЗВАНИЕ ТЕСТА It_questions_table  просто для проверки вводимых данных  УДАЛИТЬ ПОСЛЕ ПРОВЕРОК !
    checkTest = BotDB.check_test(str(call[2]), int(call[1]))  # медот выводит тест по названию теста и номеру вопроса
    print(checkTest[0])
    try:
        if str(call[0]) == str(checkTest[0]):
            print("Yes")
        else:
            print("No")
    except:
        print("check_test ошбка")


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
# Получив правильный ответ или неверный отравить сообщение об этом, увеличить баллы и пойти к следующему вопросу
# !!!!!!!!!!!!!!!!!!!!!!!!

@bot.message_handler(content_types=['text'])  # (обработчик сообщения)
# !!!!!!!!!!!!!!!!!!!
# Регистрацию по хорошему убрать из main
# !!!!!!!!!!!!!!!!!!!
# ----------------------РЕГИСТРАЦИЯ-------------------------------------------
def get_user_text(message):
    get_message = message.text.strip().lower()
    if get_message == "регистрация":
        bot.send_message(message.chat.id, "Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, add_name_user)

    elif get_message == 'info chat message':
        bot.send_message(message.chat.id, message)

    elif get_message == 'мой id':
        bot.send_message(message.chat.id, message.from_user.id)

    else:
        bot.send_message(message.chat.id, "Не понял тебя")


def add_name_user(message):
    global name_user
    name_user = message.text
    print("имя:  ", name_user)
    bot.send_message(message.chat.id, "Ведите вашу фамилию:")
    bot.register_next_step_handler(message, add_surname_user)
    return name_user


def add_surname_user(message):
    global surname_user
    surname_user = message.text
    bot.send_message(message.chat.id, "Выбирите номер группы:")
    bot.register_next_step_handler(message, add_group_user)
    return surname_user


def add_group_user(message):
    global group_user
    group_user = message.text
    mes = f"Ваше имя: {name_user} \nВаша фамилия: {surname_user} \nВаша группа: {group_user}"
    bot.send_message(message.chat.id, mes)

    if (not BotDB.user_exists(message.from_user.id)):
        try:
            BotDB.add_user(message.from_user.id, name_user, surname_user, group_user)
            print("Успешно!")
            print(f"Новый ученик: {name_user}  {surname_user} из {group_user} ")
        except:
            print("Ошибка")
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированны")


# ----------------------КОНЦ ____РЕГИСТРАЦИИ-------------------------------------------


bot.polling(none_stop=True, interval=0)  # бот запращивает сообщения без интервала

# Ноянов Роман
