import requests
import time



# URL сервиса
SERVER_URL = "server"
#"http://0.0.0.0:8000"
# host = 'http://127.0.0.1:8001'
# Заголовки запроса
headers = {
    "Content-Type": "application/json"
}

# Данные для отправки (JSON-объект)
data = {
    "name": "John Doe",
    "age": 30
}






def main():
    while True:
        try:
            # Отправляем GET-запрос
            response = requests.get(SERVER_URL, headers=headers, json=data)

            # Проверяем код состояния
            if response.status_code == 200:
                print("Запрос выполнен успешно")
                # Получаем ответ в виде JSON
                result = response.json()
                print(result)
            else:
                print(f"Ошибка: {response.status_code}")
                # Получаем текст ошибки
                error_text = response.text
                print(error_text)
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to server: {e}")
        time.sleep(5)
        try:
            # Отправляем GET-запрос
            item_response = requests.get(f"{SERVER_URL}/items/42?q=test", headers=headers, json=data)
            # Проверяем код состояния
            if item_response.status_code == 200:
                print("Запрос выполнен успешно")
                # Получаем ответ в виде JSON
                result = item_response.json()
                print(result)
            else:
                print(f"Ошибка: {item_response.status_code}")
                # Получаем текст ошибки
                error_text = item_response.text
                print(error_text)

            # Делаем запрос к эндпоинту с параметрами

            print(f"Item response: {item_response.json()}")

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to server: {e}")
        time.sleep(5)

        try:
            # Отправляем POST-запрос
            item_response = requests.post(f"{SERVER_URL}/items/", headers=headers, json=data)
            # Проверяем код состояния
            if item_response.status_code == 200:
                print("Запрос выполнен успешно")
                # Получаем ответ в виде JSON
                result = item_response.json()
                print(result)
            else:
                print(f"Ошибка: {item_response.status_code}")
                # Получаем текст ошибки
                error_text = item_response.text
                print(error_text)

            # Делаем запрос к эндпоинту с параметрами

            print(f"Item response: {item_response.json()}")

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to server: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()