from selenium.webdriver import Edge, EdgeOptions, Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from time import sleep
from re import sub


class GoogleMapsScraper:
    def __init__(self):
        self.options = EdgeOptions()
        self.options.use_chromium = True
        self.options.add_argument("--gust")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--mute-audio")
        self.options.add_argument("--headless")

    def get_webpage(self, keyword: str) -> list:
        with Edge(service=Service('driver\\edge.exe'), options=self.options) as driver:
            driver.get(f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}")
            location = driver.find_element(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
            links = lambda location_data: [link.get_attribute('href') for link in location_data.find_elements(by=By.CSS_SELECTOR, value='a[class="hfpxzc"]')]
            last_links_scraped = 0
            while len(links(location)) > last_links_scraped:
                last_links_scraped = len(links(location))
                for _ in range(10):
                    location.send_keys(Keys.PAGE_DOWN)
                    sleep(0.1)
                sleep(1)

            return list(set(links(location)))

    def get_data(self, links: list[str]) -> list[dict]:
        locations, phones, addresses, names, urls = [], [], [], [], []
        print('places:', len(links), f'EST: {((len(links) * 1.5) // 60)} - {((len(links) * 2.1) // 60)} minutes')

        with Edge(service=Service('driver\\edge.exe'), options=self.options) as driver:
            for link in links:
                driver.get(link)
                sleep(0.1)
                phone = self.__get_phone_number(driver, 0)

                if phone and phone not in phones:
                    name = driver.find_element(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div').get_attribute('aria-label').strip()
                    try: address = sub(r"[A-Z0-9]+\+[A-Z0-9]+", '', driver.find_element(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[9]/div[3]/button').get_attribute('aria-label').replace('لعنوان: ', '').strip())
                    except NoSuchElementException: address = 'None'
                    phones.append(phone), addresses.append(address), names.append(name), urls.append(link)
                    print(name, address, phone, phones.index(phone), sep=' - ')

                if links.index(link) > 0 and links.index(link) % 100 == 0:
                    driver.quit()
                    driver = Edge(service=Service('driver\\edge.exe'), options=self.options)

        for phone, location, name, url in zip(phones, addresses, names, urls):
            dictionary = dict()
            dictionary['id'] = phones.index(phone)
            dictionary['Phone'] = phone
            dictionary['Name'] = name
            dictionary['Address'] = location
            dictionary['Link'] = url

            locations.append(dictionary)

        return locations

    def __get_phone_number(self, driver, try_number: int):
        if try_number > 4: return

        try: scroll = driver.find_element(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]')
        except (StaleElementReferenceException, NoSuchElementException):
            self.__get_phone_number(driver, try_number + 1)
        else:
            scroll.send_keys(Keys.PAGE_DOWN)
            sleep(0.1)
            try: phone_number = driver.find_element(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[9]/div[5]/button/div/div[2]/div[1]').text.replace(' ', '')
            except NoSuchElementException: return
            if phone_number.isdigit(): return phone_number
            scroll.send_keys(Keys.PAGE_UP)
            sleep(0.5)
            self.__get_phone_number(driver, try_number + 1)

    @staticmethod
    def export(data: list[dict], filename: str):
        with open(f"{filename}.csv", 'a+', encoding='utf-8', errors='ignore') as export_file:
            export_file.write("ID - Phone - Name - address - URL\n")
            for place in data:
                for value in place.values():
                    export_file.write(f"{value} - ")
                export_file.write("\n")
