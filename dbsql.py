import sqlite3


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def user_exists(self, telegram_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `telegram_id` FROM `users` WHERE `telegram_id` = ?", (telegram_id,))
        return bool(len(result.fetchall()))

    def add_user(self, telegram_id, name_user, surname_user, group_user):
        """Добавляем юзера в базу"""
        self.cursor.execute(
            "INSERT INTO `users` ('telegram_id','name_user','surname_user','group_user') VALUES (?,?,?,?)",
            (telegram_id, name_user, surname_user, group_user))
        return self.conn.commit()

    def get_user(self, telegram_id):
        """Достаем информацию о пользователи"""
        result = self.cursor.execute("SELECT * FROM `users` WHERE `telegram_id` = ?", (telegram_id,))
        return result.fetchall()

    def drop_test(self, name_table, id_question):
        "Достаем вопрос и таблицы name_table и записываем в БД информацию о прохождении ученика"
        result = self.cursor.execute(f"SELECT `questions`,`answerA`,`answerB`,`answerC`,`answerD`,`true_answer` FROM {name_table} WHERE `id_question`=?",
                                     (id_question,))
        return result.fetchall()

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
    #drop_test безлпастно ли ипользовать f ???
    # Как передать в sql name_table???
    #check_test безлпастно ли ипользовать f ???
    # !!!!!!!!!!!!!!!!!!!!!!!!

    def check_test(self, name_table, id_question):
        "Достаем вопрос и таблицы name_table и записываем в БД информацию о прохождении ученика"
        result = self.cursor.execute(f"SELECT `true_answer` FROM {name_table} WHERE `id_question`=?", (id_question,))
        return result.fetchone()


# def question3(message):
#     question2 = message.text
#     sql.execute(f"""UPDATE users SET answer2 = '{question2}' WHERE user_id = {message.chat.id}""")
# ...
#     bot.register_next_step_handler(msg, question4)
