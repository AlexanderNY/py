#
from ENV import *
import os
import asyncio
import psycopg2
from telethon import TelegramClient, sync, events
import re
import zipfile
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from urllib import request
from time import sleep
from datetime import datetime
#todo try DeeplTranslator instead GoogleTranslator
from deep_translator import GoogleTranslator

# Use your own values from my.telegram.org
#api_id = 15723016
#api_hash = 'fd10c198eaa94bc4fe3f82415eb46ee6'
client = TelegramClient('Pulchrum', api_id, api_hash, system_version="4.16.30-vxASPA")
#make message from html
client.parse_mode = 'html'
# Proxy for selenium webdriver
#PROXY_HOST = '38.154.89.230'  # rotating proxy or host
#PROXY_PORT = 8000 # port
#PROXY_USER = 'nSMJ7N' # username
#PROXY_PASS = 'HQhCVD' # password

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
        executable_path=DRIVER_PATH
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
        #hardcode
        driver.get('https://smart-lab.ru/q/map/')
        await asyncio.sleep(10)
        s = datetime.now()
        path_to_file = path_to_bot + '/images/' + s.strftime("%d_%m_%Y") + '/smartlab'
        if not os.path.exists(path_to_file):
            os.makedirs(path_to_file)
        ts = s.strftime(("%f"))
        hour = s.strftime(("%H"))


        path = path_to_file + '/hmmb' + ts + '.png'
        catch = driver.find_element("xpath", "/html/body/div[1]/main/div[3]")  # мосбиржа
        catch.screenshot(path)
        #tg channel hardcoded
        # совмещен гет и пост - нужно поменять
        await client.send_message(channel_to_post, "текущая обстановка на московской бирже", file=path)

        path = path_to_file + '/hmsb' + ts + '.png'
        catch = driver.find_element("xpath", "/html/body/div[1]/main/div[5]")  # спббиржа
        catch.screenshot(path)
        # совмещен гет и пост - нужно поменять
        await client.send_message(channel_to_post, "текущая обстановка на СПБ бирже", file=path)

        path = path_to_file + '/hmcom' + ts + '.png'
        catch = driver.find_element("xpath", "/html/body/div[1]/main/div[8]")  # комментарии на смартлаб
        catch.screenshot(path)
        # совмещен гет и пост - нужно поменять
        await client.send_message(channel_to_post, "ТОП тем по количеству комментариев на смартлаб", file=path)

        print('done heatmap')
        driver.close()
        driver.quit()

    except Exception as ex:
        print(ex)
    finally:
        s = datetime.now()
        hour = s.strftime(("%H"))
    return int(hour)


async def getTwitterMessages():
    hdr = {'User-Agent': 'Yandex'}

#hardcode
    #PROXY_HOST = '5.101.34.214'  # rotating proxy or host
    #PROXY_PORT = 8000  # port
    #PROXY_USER = 'QncvkH'  # username
    #PROXY_PASS = 'j3U9yK'  # password

    proxy_url = 'https://'+ PROXY_USER + ':' + PROXY_PASS +'@' + PROXY_HOST + ':' + str(PROXY_PORT)
    proxy = request.ProxyHandler({
        'https': proxy_url,
        'http': proxy_url
    })
    try:
        driver = get_chromedriver(use_proxy=True,
                                  user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        driver.implicitly_wait(25)
        #hardcode
        url = "https://x.com/"
        driver.get(url)
        await asyncio.sleep(10)

        try:
            # Find and input enter button
            enter_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//a[@href='/login']")))
            enter_button.click()
            # Find and input the username
            username_input = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
            username_input.send_keys(tw_username)
            username_input.send_keys(Keys.ENTER)
            # Find and input the password
            password_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
            password_input.send_keys(tw_password)
            password_input.send_keys(Keys.ENTER)
            sleep(1)
        except:
            sleep(10)
        # finally:
        #    sleep(1)

        # twitter scrape

        # click  home
        # <a href="/home" aria-label="Home" role="link" class="css-175oi2r r-6koalj r-eqz5dr r-16y2uox r-1habvwh r-oyd9sg r-13qz1uu r-1ny4l3l r-1loqt21" data-testid="AppTabBar_Home_Link"><div class="css-175oi2r r-sdzlij r-dnmrzs r-1awozwy r-18u37iz r-1777fci r-xyw6el r-o7ynqc r-6416eg"><div class="css-175oi2r"><svg viewBox="0 0 24 24" aria-hidden="true" class="r-4qtqp9 r-yyyyoo r-dnmrzs r-bnwqim r-1plcrui r-lrvibr r-18jsvk2 r-lwhw9o r-cnnz9e"><g><path d="M21.591 7.146L12.52 1.157c-.316-.21-.724-.21-1.04 0l-9.071 5.99c-.26.173-.409.456-.409.757v13.183c0 .502.418.913.929.913H9.14c.51 0 .929-.41.929-.913v-7.075h3.909v7.075c0 .502.417.913.928.913h6.165c.511 0 .929-.41.929-.913V7.904c0-.301-.158-.584-.408-.758z"></path></g></svg></div><div dir="ltr" class="css-1rynq56 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-qvutc0 r-37j5jr r-adyw6z r-135wba7 r-b88u0q r-88pszg r-1joea0r r-18jsvk2" style="text-overflow: unset;"><span class="css-1qaijid r-bcqeeo r-qvutc0 r-poiln3" style="text-overflow: unset;">Home</span></div></div></a>
        home_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//a[@href='/home']")))
        home_button.click()
        sleep(1)
        # click folowing
        # <a href="/home" role="tab" aria-selected="true" class="css-175oi2r r-1awozwy r-6koalj r-eqz5dr r-16y2uox r-1h3ijdo r-1777fci r-s8bhmr r-i023vh r-1qhn6m8 r-o7ynqc r-6416eg r-1ny4l3l r-1loqt21"><div class="css-175oi2r"><div dir="ltr" class="css-1rynq56 r-bcqeeo r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-b88u0q r-1awozwy r-6koalj r-18u37iz r-1pi2tsx r-1777fci r-1l7z4oj r-95jzfe r-bnwqim" style="text-overflow: unset; color: rgb(15, 20, 25);"><span class="css-1qaijid r-bcqeeo r-qvutc0 r-poiln3" style="text-overflow: unset;">Following</span><div class="css-175oi2r r-xoduu5 r-1kihuf0 r-sdzlij r-1p0dtai r-hdaws3 r-s8bhmr r-u8s1d r-13qz1uu" style="background-color: rgb(29, 155, 240);"></div></div></div></a>
        following_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Following')]")))
        following_button.click()
        sleep(1)

        # wait for data to load
        marker = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@data-testid='cellInnerDiv']")))
        sleep(10)  # you don't need it if proxy is fast

        data = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@aria-label='Timeline: Your Home Timeline']")))

        # parse loaded data with soup
        soup = BeautifulSoup(data.get_attribute('outerHTML'), "html.parser")

        # check if directory exists
        s = datetime.now()
        # !!!! hardcoded path !!!!
        path_to_file = path_to_bot + '/images/' + s.strftime("%d_%m_%Y") + '/twitter'
        if not os.path.exists(path_to_file):
            os.makedirs(path_to_file)
        # start SQL query
        query = "INSERT INTO TWITTER (SCREENSHOT, AVATAR, TWITTERUSERLINK, TWITTERUSER, TIME, AD, TEXT, IMAGES, IMAGEOVERTEXT, COMMENTS, REPOSTS, LIKES, VIEWS, STATUS, TYPE) VALUES"
        # find all tweets
        elements = soup.findAll(lambda tag: tag.name == 'article')
        counter_elem = 0
        # process each tweet
        for element in elements:
            print(element)
            print("-------------------------------------")
            # catch screenshot of tweet

            ts = datetime.now().strftime(("%f"))
            screen_path = path_to_file + '/' + ts + '.png'
            element_id = element['aria-labelledby']
            catch = driver.find_element("xpath", "//article[@aria-labelledby='" + element_id + "']")
            catch.screenshot(screen_path)

            # avatar
            avatar = element.find('div', attrs={'data-testid': 'Tweet-User-Avatar'})
            avatar_src = avatar.find('img').get("src")
            # !!!! do we really need this shit? !!!!

            # user
            user = element.find('div', attrs={'data-testid': 'User-Name'})
            user_a = user.find('a').get('href')

            user_a_t = user.find('a').text.strip()
            # tweet time + check if tweet is an ad
            try:
                time = user.find('time').attrs['datetime']
                ad = 0
            except:
                # if there is no time, tweet is an ad
                time = ''
                ad = 1
                continue
            # finally:
            #    sleep(1)
            # how to scrape ads???
            # text
            text = element.find('div', attrs={'data-testid': 'tweetText'}).contents[0]
            # are there any images?
            try:
                # image
                image_wrapper = element.find('div', attrs={'data-testid': 'card.wrapper'})
                # print(image_wrapper)
                images = image_wrapper.findAll('img')
                print('*********')
                print(images)
                print('*********')
                img_arr = []
                for image in images:
                    ts = datetime.now().strftime(("%f"))
                    path = path_to_file + '/' + ts + '.jpg'

                    # shit with image download with proxy

                    req = request.Request(image['src'], headers=hdr)
                    opener = request.build_opener(proxy)
                    request.install_opener(opener)
                    resp = request.urlopen(req, timeout=5)
                    out = open(path, 'wb')
                    out.write(resp.read())
                    out.close()

                    img_arr_tmp = [path, image['src'], image['alt']]
                    print(img_arr_tmp)
                    print('*********')
                    # image-alt
                    img_arr.append(img_arr_tmp)
                try:
                    image_over = image_wrapper.find('div', attrs={'dir': 'ltr'}).text.strip()
                except Exception as e:
                    raise
                    image_over = "none"
                # finally:
                #    print("*************")
            except:
                img_arr = []
                image_over = "error"
            finally:
                img_arr = json.dumps({'image': img_arr})

            # comments
            comments_count = element.find('div', attrs={'data-testid': 'reply'}).text.strip()
            # reposts
            reposts_count = element.find('div', attrs={'data-testid': 'retweet'}).text.strip()
            # likes
            likes_count = element.find('div', attrs={'data-testid': 'like'}).text.strip()

            # views
            views_count = element.find('a', attrs={'aria-label': re.compile(r'View post analytics$')}).text.strip()
            status = 0
            type = 2

            if counter_elem > 0:
                query = query + ","
            counter_elem = counter_elem + 1

            query = query + "('" + screen_path + "', '" + avatar_src + "', '" + user_a + "', '" + user_a_t + "', '" + str(
                time) + "', " + str(ad) + ", '" + str(text) + "', '" + str(
                img_arr) + "', '" + image_over + "', '" + str(comments_count) + "', '" + str(
                reposts_count) + "', '" + str(likes_count) + "', '" + str(views_count) + "', " + str(
                status) + ", " + str(type) + ")"
        # query=query+



    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
        try:
            connection = psycopg2.connect(dbname=db_name, user=db_user,
                                          password=db_password, host=db_host)
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as ex:
            print(ex)
    print("getTwitterMessages done")

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

def clearHTML(text):
    text=re.sub(r'\<[^>]*\>', '', text)
    return (text)

def translate(text):
    text = GoogleTranslator(source='en', target='ru').translate(text)
    return (text)
#db tg
async def DBprocessing():
    connection = psycopg2.connect(dbname=db_name, user=db_user,
                                  password=db_password, host=db_host)
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
    connection = psycopg2.connect(dbname=db_name, user=db_user,
                                  password=db_password, host=db_host)
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

# сейчас оптимизирую это
#db tw
async def DBprocessing_tw():
    connection = psycopg2.connect(dbname=db_name, user=db_user,
                                  password=db_password, host=db_host)
    cursor = connection.cursor()
    SQLquery = "SELECT ID, TEXT, IMAGEOVERTEXT FROM TWITTER WHERE (STATUS=0 AND (TYPE=2))"

    cursor.execute(SQLquery)
    selectedrecords = cursor.fetchall()

    for row in selectedrecords:
        id = row[0]
        text = translate(clearHTML(row[1]))
        over = row[2]
        if over != '':
            over=translate(over)


        status = 1
        cursor.execute(f"UPDATE TWITTER SET TEXT = '{text}', IMAGEOVERTEXT = '{over}',STATUS = {status} WHERE id = {id}")

    connection.commit()
    cursor.close()
    connection.close()

async def DBposting_tw():
    connection = psycopg2.connect(dbname=db_name, user=db_user,
                                  password=db_password, host=db_host)
    cursor = connection.cursor()
    SQLquery = "SELECT ID, SCREENSHOT, TEXT, TWITTERUSER, IMAGEOVERTEXT FROM TWITTER WHERE (STATUS=1 AND (TYPE=2))"

    cursor.execute(SQLquery)
    selectedrecords = cursor.fetchall()

    for row in selectedrecords:
        id = row[0]
        image = str(row[1])
        text = row[2]
        over = row[4]
        user = row[3]

        # change this shit!!!!
        text = user+':<br>' + text + '<br>' + over
        if image == '' or len(text)>= 1000:
            await client.send_message(-1002009872429, text)
        else:
            await client.send_message(-1002009872429, text, file=image)
        status = 8
        cursor.execute(f"UPDATE TWITTER SET STATUS = {status} WHERE id = {id}")
        await asyncio.sleep(20)

    connection.commit()
    cursor.close()
    connection.close()


async def CheckDB(type):
    connection = psycopg2.connect(dbname=db_name, user=db_user,
                                  password=db_password, host=db_host)
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

async def CheckDB_tw(type):
    connection = psycopg2.connect(dbname=db_name, user=db_user,
                                  password=db_password, host=db_host)
    cursor = connection.cursor()
    if type == 0:
        SQLquery = "SELECT COUNT (ID) FROM TWITTER WHERE (STATUS=0)"
    elif type == 1:
        SQLquery = "SELECT COUNT (ID) FROM TWITTER WHERE (STATUS=1)"

    cursor.execute(SQLquery)
    quantity = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return(quantity)

# запись в базу данных сообщения телеграмм
# todo бъединить в одну функцию  запись в таблцы TG, TW, VK
async def WritetoDB(senderid, sendertitle, text, status=0, type=0, image=''):
    SQLquery = f"INSERT INTO MESSAGES (SENDERID,SENDERNAME,TEXT,STATUS,TYPE,IMAGE,TIMER) VALUES ('{senderid}', '{sendertitle}', '{text}', {status}, {type}, '{image}', CURRENT_TIMESTAMP)"

    connection = psycopg2.connect(dbname=db_name, user=db_user,
                                  password=db_password, host=db_host)
    cursor = connection.cursor()
    cursor.execute(SQLquery)

    connection.commit()
    cursor.close()
    connection.close()

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#запись в базу данных сообщения twitter
async def WritetoDB_tw(screen_path, avatar_src, user_a, user_a_t, time, ad, text, img_arr, image_over, comments_count, reposts_count, likes_count, views_count, status, type):
    SQLquery = f"INSERT INTO TWITTER (SCREENSHOT, AVATAR, TWITTERUSERLINK, TWITTERUSER, TIME, AD, TEXT, IMAGES, IMAGEOVERTEXT, COMMENTS, REPOSTS, LIKES, VIEWS, STATUS, TYPE) VALUES ({screen_path}, {avatar_src}, {user_a}, {user_a_t}, {time}, {ad}, {text}, {img_arr}, {image_over}, {comments_count}, {reposts_count}, {likes_count}, {views_count}, {status}, {type})"

    connection = psycopg2.connect(dbname=db_name, user=db_user,
                                  password=db_password, host=db_host)
    cursor = connection.cursor()
    cursor.execute(SQLquery)

    connection.commit()
    cursor.close()
    connection.close()

# hardcode
# включение бота на прослушивание каналов
@client.on(events.NewMessage(chats=chats_to_read))

# hardcode
# условия для сохранения сообщения
async def handler(event):
    # todo вынести в отдельный конфигурационный файл
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

# условия для асинхронного запуска функций бота
async def main():
    async with client:
        lastHour=0
        cicle=0
        while True:
            cicle = cicle+1
            #старт итерации цикла, сброс переменных
            unProcessedQuantity = 0
            unPostedQuantity = 0

            #проверка количества необработанных сообщений
            # unProcessedQuantity - количество сообщений ТГ
            # unProcessedQuantity_tw - количество сообщений twitter
            # unProcessedQuantity_vk - количество сообщений VK





            # todo перенести из JNB бота VK
            # VK

            # todo убрать ожидание
            await asyncio.sleep(10)


            # TG
            unProcessedQuantity = await CheckDB(0)
            if unProcessedQuantity > 0:
                await DBprocessing()
                print('processed')
            unPostedQuantity = await CheckDB(1)
            if unPostedQuantity >0:
                #await DBposting()
                print('post')
                print('ready for send tg messages ', unPostedQuantity)
            print(unProcessedQuantity,"-",unPostedQuantity)

            # TW
            unProcessedQuantity_tw = await CheckDB_tw(0)
            if unProcessedQuantity_tw > 0:
                await DBprocessing_tw()
                print('processed_tw')
            unPostedQuantity_tw = await CheckDB_tw(1)
            if unPostedQuantity_tw > 0:
                #await DBposting_tw()
                print('post_tw')
                print('ready for send tw messages', unPostedQuantity_tw)
            print(unProcessedQuantity_tw, "-", unPostedQuantity_tw)
            await getTwitterMessages()


            # todo вывести в стенозависимые
            #текущее время и проверка на возможность отправкии (бот работает с 9 до 18)
            currentHour = int(datetime.now().strftime("%H"))
            print(currentHour)
            print(lastHour)
            #tmp hardcode to test
            currentHour=10
            if currentHour > 9 and currentHour > lastHour and currentHour <19 :
                print('heatmap start')
                #lastHour = await getHeatmap()
                print('Twitter start')


            print('-------------')
            print(cicle)
            print('-------------')



# todo вывести в стенозависимые
# Повторяется цикл раз в n секунд, например 300
            await asyncio.sleep(300)

if __name__ == '__main__':
    workflow =
    asyncio.run(main())


# todo
# twitter does't work via proxy
# variables to ENV
# proxy for download img to ENV
# VK
# instagram
# triggers to switch functions
# each variable to ENV file
