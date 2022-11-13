import sqlite3
from create_bot import bot


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
            (telegram_id, name_user.title(), surname_user.title(), group_user))
        return self.conn.commit()

    def teacher_exists(self, telegram_id):
        """Проверяем, есть ли преподаватель в базе"""
        result = self.cursor.execute("SELECT `telegram_id` FROM `teacher` WHERE `telegram_id` = ?", (telegram_id,))
        return bool(len(result.fetchall()))

    def add_teacher(self, telegram_id, surname_teacher, name_teacher, patronymic_teacher):
        """Добавляем преподавателя в базу"""
        self.cursor.execute(
            "INSERT INTO `teacher` ('telegram_id','surname_teacher','name_teacher','patronymic_teacher') VALUES (?,?,?,?)",
            (telegram_id, surname_teacher.title(), name_teacher.title(), patronymic_teacher.title()))
        return self.conn.commit()

    def get_teacher(self, telegram_id):
        """Достаем информацию о преподавателе"""
        result = self.cursor.execute("SELECT * FROM `teacher` WHERE `telegram_id` = ?", (telegram_id,))
        return result.fetchall()

    def get_user(self, telegram_id):
        """Достаем информацию о пользователе"""
        result = self.cursor.execute("SELECT * FROM `users` WHERE `telegram_id` = ?", (telegram_id,))
        return result.fetchall()

    def drop_test(self, name_table, id_question):
        "Достаем вопрос и таблицы name_table и записываем в БД информацию о прохождении ученика"
        result = self.cursor.execute(
            f"SELECT `questions`,`answerA`,`answerB`,`answerC`,`answerD`,`true_answer` FROM {name_table} WHERE `id_question`=?",
            (id_question,))
        return result.fetchall()

    def max_question_number(self, name_table):
        "Достаем максимальное число вопросов"
        result = self.cursor.execute(f"SELECT MAX(id_question) FROM {name_table}")
        return result.fetchone()

    def user_answer(self, answer, id_question, name_table):
        "Достаем ответ пользователя в виде строки"
        result = self.cursor.execute(f"SELECT {answer} FROM {name_table} WHERE `id_question`=?", (id_question,))
        return result.fetchone()

    def check_test_in_db(self, name_table):
        "Проверка на наличие таблицы в бд"
        result = self.cursor.execute(f"SELECT name FROM sqlite_sequence WHERE name='{name_table}' ")
        return bool(len(result.fetchall()))

    def create_test(self, name_table, telegram_id):
        score_name_table = name_table + "_score"
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

        self.cursor.execute(f"""CREATE TABLE {score_name_table} (
	"score_id"	INTEGER NOT NULL,
	"telegram_id"	INTEGER NOT NULL,
	"score"	INTEGER NOT NULL,
	PRIMARY KEY("score_id" AUTOINCREMENT)
);
""")
        self.cursor.execute("INSERT INTO 'table_techer'('telegram_id','name_table') VALUES(?,?)",
                            (telegram_id, name_table))
        return self.conn.commit()

    def insert_new_test(self, name_file_s, length, worksheet):
        "Заполние нового теста"
        for i in range(3, length + 1):
            questions = worksheet[i][0].value
            answerA = worksheet[i][1].value
            answerB = worksheet[i][2].value
            answerC = worksheet[i][3].value
            answerD = worksheet[i][4].value
            true_answer = worksheet[i][5].value
            self.cursor.execute(
                f"INSERT INTO '{name_file_s[0]}' (`questions`,`answerA`,`answerB`,`answerC`,`answerD`,`true_answer`) VALUES (?,?,?,?,?,?)",
                (questions, answerA, answerB, answerC, answerD, true_answer))
        return self.conn.commit()

    def insert_score_test(self, name_file, telegram_id, balls, ):
        score_name_table = name_file + "_score"
        "Заполнение таблицы с оценками учеников"
        self.cursor.execute(
            f"INSERT INTO '{score_name_table}' (`telegram_id`,`score`) VALUES (?,?)", (telegram_id, balls))
        return self.conn.commit()

    def drop_score_from_table(self, name_file):
        self.cursor.execute(f"SELECT * FROM {name_file}")
        return self.cursor.fetchall()

    def delete_test(self, name_table):
        "Удаление теста"
        score_name_table = name_table + "_score"
        self.cursor.execute(f"DROP TABLE IF EXISTS {name_table};")
        self.cursor.execute(f"DROP TABLE IF EXISTS {score_name_table};")
        self.cursor.execute("DELETE FROM 'table_techer' WHERE name_table=?", (name_table,))
        return self.conn.commit()

    def drop_score_for_user(self, name_table, telegram_id):
        "Вывод личной оценки ученика"
        score_name_table = name_table + "_score"
        self.cursor.execute(f"""  SELECT score
                                  FROM {score_name_table} 
                                  WHERE telegram_id={telegram_id}""")
        return self.cursor.fetchone()

    def drop_score_for_teacher(self, name_table):
        "Вывод всех оценок за тест"
        score_name_table = name_table + "_score"
        self.cursor.execute(f"""SELECT users.surname_user, users.name_user,  users.group_user, {score_name_table}.score
                                FROM users, {score_name_table}
                                WHERE  users.telegram_id = {score_name_table}.telegram_id""")
        return self.cursor.fetchall()

    def drop_name_test_for_teacher(self,telegram_id):
        self.cursor.execute(f"""  SELECT name_table
                                  FROM table_techer
                                  WHERE telegram_id={telegram_id}""")
        return self.cursor.fetchall()

    def update_user_name(self, new_name):
        "функция изменения имени студента"
        telegram_id = new_name.from_user.id
        chat_id = new_name.chat.id
        new_name = new_name.text
        self.cursor.execute("UPDATE `users` SET `name_user` = ? WHERE `telegram_id` = ?",(new_name, telegram_id,))
        bot.send_message(chat_id, "Изменения успешно внесены!")
        return self.conn.commit()

    def update_user_surname(self, new_surname):
        "функция изменения фамилии студента"
        telegram_id = new_surname.from_user.id
        chat_id = new_surname.chat.id
        new_surname = new_surname.text
        self.cursor.execute("UPDATE `users` SET `surname_user` = ? WHERE `telegram_id` = ?", (new_surname, telegram_id,))
        bot.send_message(chat_id, "Изменения успешно внесены!")
        return self.conn.commit()

    def update_user_group(self, new_group):
        "функция изменения группы студента"
        telegram_id = new_group.from_user.id
        chat_id = new_group.chat.id
        new_group = new_group.text
        self.cursor.execute("UPDATE `users` SET `group_user` = ? WHERE `telegram_id` = ?", (new_group, telegram_id,))
        bot.send_message(chat_id, "Изменения успешно внесены!")
        return self.conn.commit()

    def update_teacher_name(self, name):
        "функция изменения имени преподавателя"
        telegram_id = name.from_user.id
        chat_id = name.chat.id
        name = name.text
        self.cursor.execute("UPDATE `teacher` SET `name_teacher` = ? WHERE `telegram_id` = ?",(name, telegram_id,))
        bot.send_message(chat_id, "Изменения успешно внесены!")
        return self.conn.commit()

    def update_teacher_surname(self, surname):
        "функция изменения фамилии преподавателя"
        telegram_id = surname.from_user.id
        chat_id = surname.chat.id
        surname = surname.text
        self.cursor.execute("UPDATE `teacher` SET `surname_teacher` = ? WHERE `telegram_id` = ?",(surname, telegram_id,))
        bot.send_message(chat_id, "Изменения успешно внесены!")
        return self.conn.commit()

    def update_teacher_patronymic(self, patronymic):
        "функция изменения отчества преподавателя"
        chat_id = patronymic.chat.id
        telegram_id = patronymic.from_user.id
        patronymic = patronymic.text
        self.cursor.execute("UPDATE `teacher` SET `patronymic_teacher` = ? WHERE `telegram_id` = ?", (patronymic, telegram_id,))
        bot.send_message(chat_id, "Изменения успешно внесены!")
        return self.conn.commit()
