# def add_name_user(message):
#     global name_user
#     name_user=message.text
#     print("имя:  ",name_user)
#     bot.send_message(message.chat.id, "Ведите вашу фамилию:")
#     bot.register_next_step_handler(message, add_surname_user)
#     return name_user
# def add_surname_user(message):
#     global surname_user
#     surname_user =message.text
#     bot.send_message(message.chat.id, "Выбирите номер группы:")
#     bot.register_next_step_handler(message, add_group_user)
#     return surname_user
#
# def add_group_user(message):
#     global group_user
#     group_user=message.text
#     mes=f"Ваше имя: {name_user} \nВаша фамилия: {surname_user} \nВаша группа: {group_user}"
#     bot.send_message(message.chat.id,mes)
#
#     if (not BotDB.user_exists(message.from_user.id)):
#         try:
#             BotDB.add_user(message.from_user.id,name_user,surname_user,group_user)
#             print("Успешно!")
#             print(f"Новый ученик: {name_user}  {surname_user} из {group_user} ")
#         except:
#             print("Ошибка")
#     else:
#         bot.send_message(message.chat.id,"Вы уже зарегистрированны")