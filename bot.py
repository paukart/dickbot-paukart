import config
import psycopg2
import vk_api
import random
from datetime import datetime, timezone, timedelta
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
vk_session = vk_api.VkApi(token = config.BOT_TOKEN)
longpoll = VkBotLongPoll(vk_session, 157485528)

timezone_offset = -8.0  # Pacific Standard Time (UTC−08:00)
tzinfo = timezone(timedelta(hours=timezone_offset))

db_connection = psycopg2.connect(config.URI, sslmode="require")
db_object = db_connection.cursor()

def sender(id, text):
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})

def get_name(user_id):
    result = vk_session.method('users.get', {'user_ids': user_id})
    return result

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:
            id = event.chat_id
            msg = event.object.message['text'].lower()
            user_id = event.object.message['from_id']
            if msg == '/писька':
                db_object.execute(f"SELECT vk_id FROM users WHERE vk_id = {user_id}")
                result = db_object.fetchone()
                if not result:
                    penis_size = random.randint(10, 15)
                    get_fio = get_name(user_id)
                    db_object.execute("INSERT INTO users(vk_id, fio, penis_size, last_play) VALUES (%s, %s, %s, now())", (user_id, get_fio[0]['first_name']+' '+get_fio[0]['last_name'], penis_size))
                    db_connection.commit()
                    sender(id, 'Я тебя тут раньше не видел, твой начальный пенис равен '+str(penis_size)+' см')
                elif result:
                    db_object.execute(f"SELECT last_play FROM users WHERE vk_id = {user_id}")
                    play_date = db_object.fetchone()
                    if play_date[0].strftime('%Y-%m-%d') != datetime.today().strftime('%Y-%m-%d'):
                        penis_size = random.randint(1,10)
                        solution = random.randint(0,100)
                        if (solution <= 58):
                            db_object.execute("UPDATE users SET penis_size = penis_size + %s, last_play = now() WHERE vk_id = %s", (penis_size, user_id))
                            db_connection.commit()
                            sender(id, 'Поздравляю, твой пенис сегодня вырос на '+str(penis_size)+' см')
                        if (solution >= 59 and solution <= 95):
                            db_object.execute("UPDATE users SET penis_size = penis_size - %s, last_play = now() WHERE vk_id = %s", (penis_size, user_id))
                            db_connection.commit()
                            sender(id, 'Ужас, твой пенис уменьшился на '+str(penis_size)+' см')
                        if (solution > 95):
                            db_object.execute("UPDATE users SET penis_size = 0, last_play = now() WHERE vk_id = %s", [user_id])
                            db_connection.commit()
                            sender(id, 'Тут не до шуток, у тебя отвалилась писька(')
                    else:
                        sender(id, 'Эй, ты уже играл сегодня!')
            if msg == '/топ2':
                db_object.execute(f"SELECT fio, penis_size FROM users ORDER BY penis_size DESC")
                top = db_object.fetchall()
                top_list = ''
                for row in top:
                    temp1 = str(row[0])+" - "+str(row[1])+' см\n'
                    temp2 = top_list
                    top_list = temp2 + temp1
                sender(id, top_list)
