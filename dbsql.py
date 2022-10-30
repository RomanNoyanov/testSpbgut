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


    def max_question_number(self,name_table):
        "Достаем максимальное число вопросов"
        result = self.cursor.execute(f"SELECT MAX(id_question) FROM {name_table}")
        return result.fetchone()


    def user_answer(self, answer, id_question, name_table):
        "Достаем ответ пользователя в виде строки"
        result = self.cursor.execute(f"SELECT {answer} FROM {name_table} WHERE `id_question`=?", (id_question,))
        return result.fetchone()


    def check_test_in_db(self,name_table):
        "Проверка на наличие таблицы в бд"
        result=self.cursor.execute(f"SELECT name FROM sqlite_sequence WHERE name='{name_table}' ")
        return bool(len(result.fetchall()))

    def create_test(self,name_table):
        "Создаем новую таблицу из excel файла пользователя"
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS '{name_table}' 
        ('id_question'	INTEGER,
        'questions'	TEXT NOT NULL,
        'answerA'	TEXT,
        'answerB'	TEXT,
	    'answerC'	TEXT,
	    'answerD'	TEXT,
	    'true_answer'	TEXT NOT NULL,
	    PRIMARY KEY("id_question" AUTOINCREMENT));""")
        return self.conn.commit()


    def insert_new_test(self,name_file_s, length, worksheet):
        "Заполение нового теста"
        for i in range(3,length):
            questions=worksheet[i][0].value
            answerA=worksheet[i][1].value
            answerB=worksheet[i][2].value
            answerC=worksheet[i][3].value
            answerD=worksheet[i][4].value
            true_answer=worksheet[i][5].value
            self.cursor.execute(f"INSERT INTO '{name_file_s[0]}' (`questions`,`answerA`,`answerB`,`answerC`,`answerD`,`true_answer`) VALUES (?,?,?,?,?,?)",(questions,answerA,answerB,answerC,answerD,true_answer))
        return self.conn.commit()

    def delete_test(self,name_file_s):
        self.cursor.execute(f"DROP TABLE IF EXISTS {name_file_s};")
        return self.conn.commit()
