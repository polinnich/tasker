import telebot
import psycopg2

conn = psycopg2.connect(
   database="postgres", user='', password='', host='', port= ''
)

token = ""
bot = telebot.TeleBot(token)

HELP = """
Команды бота: 
/help - вывести справку
/add - добавить задачу(пример: /add продукты купить шоколадку, "продукты" тут как список) 
/all - показать конкретный список задач (/all продукты)
/delete - убрать задачу из списка (/delete продукты купить шоколадку)
/lists - показать все списки задач
"""

def select(query):
    cursor = conn.cursor()
    cursor.execute(query)
    res = cursor.fetchall()
    cursor.close()
    return res

def insert(query):
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()

def add_task(spisok,task,userid):
    spisok = spisok.lower()
    res = select(f'select listid from lists where userid = \'{userid}\' and listname = \'{spisok}\'')
    if len(res) != 0:
        listid=res[0][0]
        insert(f"insert into tasks (listid, task) VALUES (\'{listid}\',\'{task}\') ")
    else:
        insert(f"insert into lists (userid, listname) VALUES (\'{userid}\',\'{spisok}\') ")
        res = select(f'select listid from lists where userid = \'{userid}\' and listname = \'{spisok}\'')
        listid = res[0][0]
        insert(f"insert into tasks (listid, task) VALUES ({listid},\'{task}\') ")

@bot.message_handler(commands = ["help"])
def help_message(message):
    bot.send_message(message.chat.id, HELP)

@bot.message_handler(commands = ["add"])
def todo_message(message):
    command = message.text.split(maxsplit = 2)
    spisok =  command[1]
    task = command[2]
    add_task(spisok, task, message.chat.id)
    sms = "Задача " + task + " добавлена в список: " + spisok
    bot.send_message(message.chat.id, sms)

@bot.message_handler(commands = ["all"])
def showall_message(message):
    command = message.text.split(maxsplit = 1)
    spisok = str.lower(command[1])
    sms = ""
    listid = select(f'select listid from lists where listname = \'{spisok}\' and userid = \'{message.chat.id}\'')
    if len(listid) != 0:
        tasks = select(f'select task from tasks where listid = {listid[0][0]}')
        sms = spisok.upper() + "\n"
        for task in tasks:
            sms = sms + " - " + task[0] + "\n"
    else:
        sms = "Такого списка задач нет"
    bot.send_message(message.chat.id, sms)

@bot.message_handler(commands = ["delete"])
def deleting_message(message):
    command = message.text.split(maxsplit = 2)
    spisok = str.lower(command[1])
    task = command[2]
    sms = ""
    listid = select(f'select listid from lists where listname = \'{spisok}\' and userid = \'{message.chat.id}\'')
    if len(listid) != 0:
        sms = spisok.upper()
        task_db = select(f'select task from tasks where listid = {listid[0][0]}')
        if len(task_db) != 0:
            insert(f'delete from tasks where task = \'{task}\' and listid = {listid[0][0]}')
            sms = "В списке " + sms + " задача " + task + " удалена" +"\n"
        else:
            sms = "В списке " + sms + " такой задачи нет" 
    else:
        sms = "Такого списка задач нет"
    bot.send_message(message.chat.id, sms)

@bot.message_handler(commands = ["lists"])
def lists_message(message):
    lists = select(f'select listname from lists where userid = \'{message.chat.id}\'')
    if len(lists) != 0:
        sms = ""
        for spisok in lists:
            sms = sms + spisok[0].upper() + "\n"
    else:
        sms = "Вы еще не создали ни одного списка задач, вызовите /help для справки"
    bot.send_message(message.chat.id, sms)

bot.infinity_polling()   
