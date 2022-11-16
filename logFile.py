import datetime

def log(message):
    dt=datetime.datetime.now()
    s=(" Сообщение от {0} {1} (id = {2}) СООБЩЕНИЕ: {3}".format(message.from_user.first_name,
                                                                message.from_user.last_name,
                                                                str(message.from_user.id), message.text))
    file = open("log.txt", 'a', encoding='utf-8')
    file.write(str(dt)+ str(s)+"\n")
    file.close()
