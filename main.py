from playwright.sync_api import sync_playwright, expect
from playwright.async_api import async_playwright, expect
import json, os
import urllib.request



def save_image(url, folder="images"):

    if not os.path.exists(folder):
        os.makedirs(folder)
    image_name = os.path.join(folder, os.path.basename(url.split("?")[0]))
    urllib.request.urlretrieve(url, image_name)
def load_cookies(context, filename="cookies.json"):
    # Загрузка куки из файла
    with open(filename, "r", encoding="utf-8") as file:
        cookies = json.load(file)
    context.add_cookies(cookies)
def sync_work():
    url = 'https://www.pinterest.com/'
    # открыть соединение
    with sync_playwright() as p:
        # инициализация браузера (без видимого открытия браузера)
        # browser = p.chromium.launch()
        # инициализация браузера (с явным открытием браузера)
        browser = p.chromium.launch( headless=True, args=[
            '--disable-blink-features=AutomationControlled'
        ])

        # инициализация страницы
        page = browser.new_context()
        # Попробовать загрузить куки, если файл существует
        try:
            load_cookies(page)
        except FileNotFoundError:
            print("Файл с куки не найден, открывается новый сеанс.")
        page = page.new_page()
        # переход по url адресу:
        page.goto(url, wait_until="networkidle")

        # Словарь для хранения уникальных URL изображений
        img_urls = set()
        # Прокрутка страницы вниз несколько раз
        scroll_attempts = 10
        for _ in range(scroll_attempts):
            # Использование JavaScript для извлечения атрибутов src всех изображений в mainContainer
            new_img_urls = page.evaluate('''() => {
                const imgs = document.querySelectorAll('.mainContainer img');
                return Array.from(imgs)
                    .map(img => img.getAttribute('src'))
                    .filter(src => src && src.includes('236x')); // Оставляем только URL с '236x'
            }''')

            # Добавление новых URL в словарь
            img_urls.update(new_img_urls)

            # Прокрутка страницы вниз
            page.evaluate('window.scrollBy(0, window.innerHeight)')

            # Небольшая задержка, чтобы контент успел загрузиться
            page.wait_for_timeout(2000)

            # Фильтрация изображений с именами более 20 символов и их сохранение

        for url in img_urls:
            if url and len(os.path.basename(url.split("?")[0])) > 20:
                url = url.replace("236x", "736x")
                save_image(url)
        print('[Succes] Image pars')

        browser.close()


sync_work()