from dbsql import BotDB
from create_bot import bot
from ref import db_file
import openpyxl
import os

BotDB = BotDB(db_file)


# !!!!!!!!!!!!!!!!!!!!!!!!
# сделать функцию, которая отправит шаблон таблицы для ее заполнения
# !!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=['document'])
def start_read(message):
    "функция обработки записи теста и отправки подсказки преподавателю"
    msg = bot.send_message(message.chat.id,"Отправьте файл с тестом в формате xlsx или xls")
    bot.register_next_step_handler(msg, read_excel)


def read_excel(message):
    if BotDB.teacher_exists(message.from_user.id):
        try:
            file_info = bot.get_file(message.document.file_id)  # Получение файла от пользователя
            name_file = message.document.file_name  # Название файла в формат nnn.xxx
            name_file_s = str(name_file).split(".")

            if name_file_s[1] == "xlsx" or name_file_s[1] == "xls":  # проверка на тип файла
                if (not BotDB.check_test_in_db(name_file_s[0])):  # Проверяем есть ли тест с таким названием
                    downloaded_file = bot.download_file(file_info.file_path)  # Скачиваем полученный файл
                    src = 'files/' + message.document.file_name;  # Ссылка на файл
                    with open(src, 'wb') as new_file:
                        new_file.write(downloaded_file)  # Сохраняем файл
                    xl = openpyxl.load_workbook(src)
                    worksheet = xl.active
                    length = int(worksheet.max_row)  # количество записей в таблице
                    BotDB.create_test(name_file_s[0], message.from_user.id)  # Метод создающий новую таблицу для теста
                    BotDB.insert_new_test(name_file_s, length, worksheet)  # Метод заполняющий таблицу с новым тестом
                    bot.reply_to(message, f" Cоздали новый тест! \nКод для запуска: {name_file_s[0]}")

                else:
                    bot.reply_to(message,
                                 f"Тест с таким названием: '{name_file_s[0]}' уже существует. \nПопробуйте сменить название \nПомните, что название теста будет его ключом доступа")

            else:
                bot.reply_to(message, "Неверный тип данных. \nНеобходим .xlsx или xls")

        except Exception as e:
            BotDB.delete_test(name_file_s[0])
            print(worksheet)
            print(length)
            os.remove(src)
            bot.reply_to(message, "Неверно оформлен файл")
            print(e)

    else:
        pass


def register_handlers_excel(bot):
    bot.message_handler(content_types=['document'])(start_read)
