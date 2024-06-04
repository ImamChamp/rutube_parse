import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import xlsxwriter


def get_source(url):
    service = Service(executable_path=r'chromedriver-win64\chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(1)  # время на загрузку страницы
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:  # листаем страницу до последнего пикселя
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(1)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # после того как драйвер долистал до конца страницы записываем всю разметку в отдельный файл
                with open("source_page.html", "w", encoding="utf-8") as file:
                    file.write(driver.page_source)
                break
            last_height = new_height

    except Exception as _ex:
        print(_ex)
    finally:  # закрываем страницу
        driver.close()
        driver.quit()


def get_items(file_path):
    with open(file_path, encoding='utf-8') as file:
        src = file.read()  # считываем html файл

    soup = BeautifulSoup(src, 'lxml')
    items_divs = soup.find_all('article', class_='wdp-card-wrapper-module__wrapper')  # ищем все карты видео

    rut_url = 'https://rutube.ru'

    data = [['Название', 'Количество просмотров', 'Дата публикации', 'Ссылка на видео']]

    for item in items_divs:
        item_title = item.find('a', class_='wdp-link-module__link wdp-card-description-module__title '
                                           'wdp-card-description-module__url wdp-card-description-module__videoTitle')
        item_views = item.find('div', class_='wdp-card-description-meta-info-module__metaInfoViewsCountNumber')
        item_date = item.find('div', class_='wdp-card-description-meta-info-module__metaInfoPublishDate')
        item_url = item.find('a', class_='wdp-link-module__link wdp-card-poster-module__posterWrapper').get('href')
        data.append([item_title.text, item_views.text, item_date.text, rut_url+item_url])

    with xlsxwriter.Workbook('rutube_parse.xlsx') as workbook:  # создаём экселевский файл
        worksheet = workbook.add_worksheet()

        for row_num, info in enumerate(data):
            worksheet.write_row(row_num, 0, info)

    return "Экселевский файл был создан успешно"


def main():
    get_source(url='https://rutube.ru/channel/25548072/videos/')
    print(get_items(file_path=r'source_page.html'))


if __name__ == "__main__":
    main()
