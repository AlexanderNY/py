import asyncio
import psycopg2
from telethon import TelegramClient, sync, events
import re

# Use your own values from my.telegram.org
api_id = 15723016
api_hash = 'fd10c198eaa94bc4fe3f82415eb46ee6'
client = TelegramClient('Pulchrum', api_id, api_hash, system_version="4.16.30-vxASPA")

# def WritetoDB(sender, text):
#     f = open('message.txt', 'a')
#     string = str(sender) + "|" + str(text) + "|0\n"
#     f.write(string)
#     f.close()

def replaceMessage(message):
    REPLACEMENTS = [
        ("🔸", "💥"),
        ("Blast", "😤"),
        ("♨️", ""),
        ("💉", ""),
        ("🧩", ""),
        ("⚱️", ""),
        ("📊", ""),
        ("🏦", ""),
        ("🌆", ""),
        ("🔘", ""),
        ("🌏", ""),
        ("🔴", "💥"),
        ("🟢", "💥"),
        ("🕵️‍♀️", ""),
        ("🪨", ""),
        ("🛒", ""),
        ("😔", ""),
        ("💪♀️", ""),
        ("📉", "💥"),
        ("📈", "💥"),
        ("📰", ""),
        ("💻", ""),
        ("📜", "💥"),
        ("⚠️", "💥"),
        ("🛢", ""),
        ("👉", ""),

        ("Что да как? \n", ""),
        # ("🔥Акции и инвестиции\n", ""),

    ]

    for old, new in REPLACEMENTS:
        message = message.replace(old, new)
    # RegExp= "Обзор важных событий на утро 2 февраля: \n([^#]*)#новости\n"
    message = re.sub(r"Обзор важных событий на утро([^#]*)#новости\n", "", message)
    message = re.sub(r"([^🔥]*)🔥Акции и инвестиции\n\n", "", message)
    message = re.sub(r"Комментируйте на Смартлабе:*", "", message)

    return (message)


def DBprocessing():
    connection = psycopg2.connect(dbname='db_bot', user='postgres',
                                  password='1qaz!QAZ', host='localhost')
    cursor = connection.cursor()
    SQLquery = "SELECT ID, TEXT FROM MESSAGES WHERE (STATUS=0 AND (TYPE=2 OR TYPE=3 OR TYPE=4))"

    cursor.execute(SQLquery)
    selectedrecords = cursor.fetchall()

    for row in selectedrecords:
        id = row[0]
        text = replaceMessage(row[1])
        status = 1
        cursor.execute(f"UPDATE MESSAGES SET TEXT = '{text}', STATUS = {status} WHERE id = {id}")

    connection.commit()
    cursor.close()
    connection.close()

def ReadfromDB()


def WritetoDB(senderid, sendertitle, text, status=0, type=0):
    #f = open('message.txt', 'a')
    #string = str(sender) + "|" + str(text) + "|0\n"
    #f.write(string)
    #f.close()
    SQLquery = f"INSERT INTO MESSAGES (SENDERID,SENDERNAME,TEXT,STATUS,TYPE, TIMER) VALUES ('{senderid}', '{sendertitle}', '{text}', {status}, {type}, CURRENT_TIMESTAMP)"

    connection = psycopg2.connect(dbname='db_bot', user='postgres',
                                  password='1qaz!QAZ', host='localhost')
    cursor = connection.cursor()
    cursor.execute(SQLquery)

    connection.commit()
    cursor.close()
    connection.close()

def main():
    @client.on(events.NewMessage(chats=[-1001677806302,-1001496320800,-1001411610346]))
    async def handler(event):
        if 'hello' in event.raw_text:
            text = event.raw_text
            sender = await event.get_sender()
            status = 0
            type = 1
            WritetoDB(sender.id, sender.title, text, status, type)
        elif 'Обзор важных событий на' in event.raw_text:
            text = event.raw_text
            sender = await event.get_sender()
            status = 0
            type = 2
            WritetoDB(sender.id, sender.title, text, status, type)
        elif 'Что да как? \n' in event.raw_text:
            text = event.raw_text
            sender = await event.get_sender()
            status = 0
            type = 3
            WritetoDB(sender.id, sender.title, text, status, type)
        elif '🔥Акции и инвестиции\n' in event.raw_text:
            text = event.raw_text
            sender = await event.get_sender()
            status = 0
            type = 4
            WritetoDB(sender.id, sender.title, text, status, type)
        else:
            senderid = '0'
            text = "--------"
            sendername = "--------"
            status = 2
            type = 0
            WritetoDB(senderid, sendername, text, status, type)


    client.start()
    client.run_until_disconnected()


if __name__ == '__main__':
    main()
