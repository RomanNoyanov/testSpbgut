from telebot import types
from dbsql import BotDB
from create_bot import bot
from ref import db_file
from logFile import log
import openpyxl
import os
BotDB = BotDB(db_file)



# !!!!!!!!!!!!!!!!!!!!!!!11
# сделать функцию, которая отправит шаблон иаблицы для ее заполнения
# !!!!!!!!!!!!!!!!!!!!!!!!1
def read_excel(message):
    try:
        file_info = bot.get_file(message.document.file_id)  # Получение фала от пользователя
        name_file = message.document.file_name # Название файла в формат nnn.xxx
        name_file_s = str(name_file).split(".")

        if name_file_s[1] == "xlsx" or name_file_s[1] == "xls":  # проверка на тип файла
            if (not BotDB.check_test_in_db(name_file_s[0])): # Проверяем есть ли тест с таким названием
                downloaded_file = bot.download_file(file_info.file_path)  # Скачиваем полученный файл
                src = 'files/' + message.document.file_name;  # Ссылка на файл
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)  # Сохраняем файл
                xl = openpyxl.load_workbook(src)
                worksheet = xl.active
                length = int(worksheet.max_row+2) # количесвто записией в таблице
                BotDB.create_test(name_file_s[0])  # Метод создающий новую таблиуц для теста
                BotDB.insert_new_test(name_file_s,length,worksheet) # Метод заполняющий таблицу с новым тестом

            else:bot.reply_to(message, f"Тест с таким названием: '{name_file_s[0]}' уже существует. \nПопробуйте сменить название \nПомните, что название теста будет его ключом доступа")

        else:
            bot.reply_to(message, "Неверный тип данных. \nНеобходим .xlsx или xls")

    except Exception as e:
        BotDB.delete_test(name_file_s[0])
        os.remove(src)
        bot.reply_to(message, "Неверно оформлен файл")
        print(e)


def register_hendlers_excel(bot):
    bot.message_handler(content_types=['document'])(read_excel)
