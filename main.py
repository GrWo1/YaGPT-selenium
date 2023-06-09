import os
import time
import pymysql
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


load_dotenv()

HOST=os.getenv('HOST_DATABASE')
USER=os.getenv('USER_DATABASE')
PASSWORD=os.getenv('PASSWORD_DATABASE')
DATABASE=os.getenv('DATABASE')


def update_specification(all_products):
    """
    Функция принимает словарь и по id продукта меняют значение характеристик в таблице products.
    """
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
    )
    cursor = connection.cursor()
    for key, value in all_products.items():
        query = "UPDATE products SET specifications=%s WHERE id=%s"
        values = (value, key)
        cursor.execute(query, values)
        connection.commit()
    cursor.close()
    connection.close()


def get_specification(all_products):
    """
    Функция получает на вход словарь и делает на основе значений словаря запросы в YaGPT.
    Возвращает функция тот же словарь, но значения изменены с названий продуктов на характеристики.
    """
    chrome_options = Options()
    # proxy = "username:password@IP:PORT" # Ввести данные прокси-сервера
    # chrome_options.add_argument(f'--proxy-server={proxy}')
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument(
        "Accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    )
    chromedriver_path = "chromedriver"
    os.environ['PATH'] += os.pathsep + chromedriver_path
    driver = webdriver.Chrome(options=chrome_options)
    while True:
        try:
            driver.get("https://www.ya.ru")
            open_chat = driver.find_element(By.CLASS_NAME, "alice-fab__promo-shortcut-img")
        except:
            time.sleep(30)
            continue
        else:
            break
    open_chat.click()
    time.sleep(5)
    input_text = driver.find_element(By.CLASS_NAME, "input-container__text-input")
    for key, value in all_products.items():
        input_text.send_keys(
            f"Давай придумаем характеристики к товару {value} для интернет-магазина"
        )
        input_text.send_keys(Keys.RETURN)
        time.sleep(10) # Установить больше секунд, если бот не успевает ответить
        message = driver.find_elements(By.CLASS_NAME, "message")[-1]
        all_products[key] = message.text
    update_specification(all_products)


def get_products():
    """
    Функция формирует словарь на основе данных об id из файла category_id.txt.
    Ключ - это id продукта (id из таблицы products).
    Значение - это название продукта (name из таблицы products).
    """
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
    )
    cursor = connection.cursor()

    with open('category_id.txt', 'r') as file:
        for item_id in file.readlines():
            cursor.execute(
                f'''
                SELECT product_id FROM product_category
                WHERE category_id={item_id}
                ;
                '''
            )
            results = cursor.fetchall()
            all_products = {}
            for row in results:
                cursor.execute(
                    f'''
                    SELECT id, name FROM products
                    WHERE id={row[0]}
                    ;
                    '''
                )
                product = cursor.fetchone()
                all_products[product[0]] = product[1]
        get_specification(all_products)
    cursor.close()
    connection.close()




def main():
    get_products()


if __name__ == "__main__":
    main()