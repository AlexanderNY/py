import asyncio
import psycopg2
from telethon import TelegramClient, sync, events
import re
import zipfile
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime


# Use your own values from my.telegram.org
api_id = 15723016
api_hash = 'fd10c198eaa94bc4fe3f82415eb46ee6'
client = TelegramClient('Pulchrum', api_id, api_hash, system_version="4.16.30-vxASPA")

# Proxy for selenium webdriver
PROXY_HOST = '38.154.89.230'  # rotating proxy or host
PROXY_PORT = 8000 # port
PROXY_USER = 'nSMJ7N' # username
PROXY_PASS = 'HQhCVD' # password

# def WritetoDB(sender, text):
#     f = open('message.txt', 'a')
#     string = str(sender) + "|" + str(text) + "|0\n"
#     f.write(string)
#     f.close()

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"76.0.0"
}
"""

background_js = """
let config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };
chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}
chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    chrome_options = webdriver.ChromeOptions()

    if use_proxy:
        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

        chrome_options.add_extension(plugin_file)

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    s = Service(
        executable_path='K:/Project/chromedriver-win64/chromedriver.exe'
    )
    driver = webdriver.Chrome(
        service=s,
        options=chrome_options
    )
    return driver


async def getHeatmap():
    try:
        driver = get_chromedriver(use_proxy=False,
                                  user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        driver.get('https://smart-lab.ru/q/map/')
        await asyncio.sleep(10)
        s = datetime.now()
        path_to_file = 'K:/Project/py/bot/images/' + s.strftime("%d_%m_%Y") + '/smartlab'
        if not os.path.exists(path_to_file):
            os.makedirs(path_to_file)
        ts = s.strftime(("%f"))
        hour = s.strftime(("%H"))
        path = path_to_file + '/hmmb' + ts + '.jpg'
        catch = driver.find_element("xpath", "/html/body/div[1]/main/div[3]")  # мосбиржа
        catch.screenshot(path)
        # совмещен гет и пост - нужно поменять
        await client.send_message(-1002009872429, "текущая обстановка на московской бирже", file=path)

        path = path_to_file + '/hmsb' + ts + '.jpg'
        catch = driver.find_element("xpath", "/html/body/div[1]/main/div[5]")  # спббиржа
        catch.screenshot(path)
        # совмещен гет и пост - нужно поменять
        await client.send_message(-1002009872429, "текущая обстановка на СПБ бирже", file=path)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

    return int(hour)
# messages processing

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
        ("☕️", ""),
        ("☕", ""),
        ("Что да как? \n", ""),
        ("Что да как? \n\n", ""),
        # ("🔥Акции и инвестиции\n", ""),

    ]

    for old, new in REPLACEMENTS:
        message = message.replace(old, new)
    # RegExp= "Обзор важных событий на утро 2 февраля: \n([^#]*)#новости\n"
    message = re.sub(r"Обзор важных событий на утро([^#]*)#новости\n", "", message)
    message = re.sub(r"([^🔥]*)🔥Акции и инвестиции\n\n", "", message)
    message = re.sub(r"Комментируйте на Смартлабе:*", "", message)
    message = re.sub(r"Пишите свои мысли в комментарии:*", "", message)
    message = re.sub(r"Пишите свое мнение в комментарии, все графики в источнике:", "", message)
    message = re.sub(r"Автор: *", "", message)
    return (message)


async def DBprocessing():
    connection = psycopg2.connect(dbname='db_bot', user='postgres',
                                  password='1qaz!QAZ', host='localhost')
    cursor = connection.cursor()
    SQLquery = "SELECT ID, TEXT FROM MESSAGES WHERE (STATUS=0 AND (TYPE=2))"

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

async def DBposting():
    connection = psycopg2.connect(dbname='db_bot', user='postgres',
                                  password='1qaz!QAZ', host='localhost')
    cursor = connection.cursor()
    SQLquery = "SELECT ID, TEXT, IMAGE FROM MESSAGES WHERE (STATUS=1 AND (TYPE=2))"

    cursor.execute(SQLquery)
    selectedrecords = cursor.fetchall()

    for row in selectedrecords:
        id = row[0]
        text = row[1]
        image = "K:/Project/py/bot" + str(row[2])
        # change this shit!!!!

        if image == '' or len(text)>= 1000:
            await client.send_message(-1002009872429, text)
        else:
            await client.send_message(-1002009872429, text, file=image)

        status = 8


        cursor.execute(f"UPDATE MESSAGES SET STATUS = {status} WHERE id = {id}")
        await asyncio.sleep(20)

    connection.commit()
    cursor.close()
    connection.close()



async def CheckDB(type):
    connection = psycopg2.connect(dbname='db_bot', user='postgres',
                                  password='1qaz!QAZ', host='localhost')
    cursor = connection.cursor()
    if type == 0:
        SQLquery = "SELECT COUNT (ID) FROM MESSAGES WHERE (STATUS=0)"
    elif type == 1:
        SQLquery = "SELECT COUNT (ID) FROM MESSAGES WHERE (STATUS=1)"

    cursor.execute(SQLquery)
    quantity = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return(quantity)

async def WritetoDB(senderid, sendertitle, text, status=0, type=0, image=''):
    #f = open('message.txt', 'a')
    #string = str(sender) + "|" + str(text) + "|0\n"
    #f.write(string)
    #f.close()
    SQLquery = f"INSERT INTO MESSAGES (SENDERID,SENDERNAME,TEXT,STATUS,TYPE,IMAGE,TIMER) VALUES ('{senderid}', '{sendertitle}', '{text}', {status}, {type}, '{image}', CURRENT_TIMESTAMP)"

    connection = psycopg2.connect(dbname='db_bot', user='postgres',
                                  password='1qaz!QAZ', host='localhost')
    cursor = connection.cursor()
    cursor.execute(SQLquery)

    connection.commit()
    cursor.close()
    connection.close()


@client.on(events.NewMessage(chats=[-1001677806302,-1001496320800,-1001411610346, -1001063908560]))

async def handler(event):
    # тестовое слово с командой 1
    if 'hello 1' in event.raw_text:
        text = event.raw_text
        sender = await event.get_sender()
        status = 0
        type = 1
        image = "/images/static/1.jpg"
        await WritetoDB(sender.id, sender.title, text, status, type, image)
    # Мастерская финансов
    elif 'Обзор важных событий на' in event.raw_text:
        text = event.raw_text
        sender = await event.get_sender()
        status = 0
        type = 2
        image = "/images/static/masters.jpg"
        await WritetoDB(sender.id, sender.title, text, status, type, image)
    # Профита нет. А если найду?
    elif 'Что да как? \n' in event.raw_text:
        text = event.raw_text
        sender = await event.get_sender()
        status = 0
        type = 2
        image = "/images/static/profit.jpg"
        await WritetoDB(sender.id, sender.title, text, status, type, image)
    # СМАРТЛАБ
    elif '🔥Акции и инвестиции\n' in event.raw_text:
        text = event.raw_text
        sender = await event.get_sender()
        status = 0
        type = 2
        image = "/images/static/smartlab.jpg"
        await WritetoDB(sender.id, sender.title, text, status, type, image)
    # Сигналы для торговли
    elif 'Какие события нас ждут сегодня? Доброе утро' in event.raw_text:
        text = event.raw_text
        sender = await event.get_sender()
        status = 0
        type = 2
        image = "/images/static/signal.jpg"
        await WritetoDB(sender.id, sender.title, text, status, type, image)
    # после теста необходимо удалить
    else:
        senderid = '0'
        text = "--------"
        sendername = "--------"
        status = 2
        type = 0
        image = "/images/static/2.jpg"
        await WritetoDB(senderid, sendername, text, status, type, image)

async def main():
    async with client:
        lastHour=0
        while True:
            unProcessedQuantity = 0
            unPostedQuantity = 0
            unProcessedQuantity = await CheckDB(0)
            if unProcessedQuantity > 0:
                await DBprocessing()
                print('processed')

            await asyncio.sleep(10)

            unPostedQuantity = await CheckDB(1)
            if unPostedQuantity >0:
                await DBposting()
                print('ready for send ', unPostedQuantity)
            print(unProcessedQuantity,"-",unPostedQuantity)
            currentHour = int(datetime.now().strftime("%H"))
            if currentHour > 9 and currentHour > lastHour and currentHour <19 :
                lastHour = await getHeatmap()
                print('heatmap start')


            await asyncio.sleep(300)

if __name__ == '__main__':

    asyncio.run(main())