import random
import json
import re
import time


from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType

from .utils import clamp
from .logger import Logger
import yandexClicker.config as CONFIG
import yandexClicker.agents as agents


class VirtualBrowser:
    driver: webdriver.Chrome
    mobile_config: dict = {"userAgent": "<host>"}

    xpath_dict = {
        "search-input": '//*[@id="text"]',
        "search-result": '//*[@id="search-result"]',
        "search-cards": './/*[@class="serp-item"]',
        "text-element": ".//div/div[3]/div[1]/span/span[1]",
        "ad-link-element": ".//div/div[1]/a",
    }

    logger: Logger

    def __init__(self, type: str = "", ip: str = ""):
        self.type, self.ip = type, ip
        options = webdriver.ChromeOptions()

        if not CONFIG.DEBUG:
            options.add_argument("--headless")

        # --- Settings specific for mobile devices --- #
        if CONFIG.mobile:
            viewport_width = random.randint(300, 500)
            viewport_height = random.randint(600, 900)

            self.mobile_config = {
                "deviceMetrics": {
                    "width": viewport_width,
                    "height": viewport_height,
                    "pixelRatio": 3.0,
                },
                "userAgent": agents.get_random_user_agent(),
            }
            options.add_experimental_option("mobileEmulation", self.mobile_config)

            self.xpath_dict.update(
                {
                    "search-input": '//input[@type="search"]',
                    "text-element": ".//div/div[2]/div[1]/span/span[1]",
                }
            )
        # --- End of mobile settings --- #

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # options.add_argument(f"--proxy-server={self.type}://{self.ip}")
        # options.add_argument(f'--host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE {self.ip[:self.ip.index(":")]}"')

        self.driver = webdriver.Chrome(
            options=options,
            executable_path="./Drivers/chromedriver",
        )

        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Linux",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        self.logger = Logger()

    def find_advert(self, search_term: str):
        self.driver.get("https://ya.ru/")
        self.__resolve_captcha()

        if hasattr(CONFIG, "region"):
            self.__set_region(CONFIG.region)

        try:
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, self.xpath_dict.get("search-input"))
                )
            )

        except:
            self.logger.log(
                "https://ya.ru/",
                str(self.mobile_config),
                self.ip,
                action="Captcha not solved",
            )
            return

        search_input.send_keys(search_term)
        search_input.submit()

        self.__resolve_captcha()

        try:
            search_cards = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, self.xpath_dict.get("search-result"))
                )
            )
            search_cards = search_cards.find_elements(By.CLASS_NAME, "serp-item")

        except:
            self.logger.log(
                "https://ya.ru/search",
                str(self.mobile_config),
                self.ip,
                action="Captcha not solved",
            )
            return

        ad_links: list[WebElement] = []

        for search_card in search_cards:
            try:
                text_element = search_card.find_element(
                    By.XPATH, self.xpath_dict.get("text-element")
                )

                if text_element.text.find("Реклама") != -1:
                    ad_link_element = search_card.find_element(
                        By.XPATH, self.xpath_dict.get("ad-link-element")
                    )

                    link = self.__get_url(ad_link_element)

                    if self.__check_link(link):
                        ad_links.append(ad_link_element)

            except:
                continue

        if hasattr(CONFIG, "index") and len(ad_links) > 0:
            ad_link = ad_links[clamp(0, CONFIG.index - 1, len(ad_links) - 1)]

        elif len(ad_links) > 0:
            ad_link = ad_links[0]

        else:
            self.logger.log(
                "<None>", str(self.mobile_config), self.ip, action="No ads found"
            )
            return

        link = self.__get_url(ad_link)
        ad_link.click()

        time.sleep(2)

        self.logger.log(link, str(self.mobile_config), self.ip, action="clicked")

        try:
            elem = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "div"))
            )

            time.sleep(random.randint(*CONFIG.delay_interval))

        except:
            pass

    def __get_url(self, element: WebElement):
        json_data = element.get_attribute("data-bem")
        json_data = json.loads(json_data)
        link = json_data.get("click").get("arguments").get("url")

        return link

    def __check_link(self, link: str):
        for link_mask in CONFIG.link_masks:
            if re.match(link_mask, link) is not None:
                return True

        return False

    def __set_region(self, region):
        self.driver.get("https://yandex.ru/tune/geo?retpath=https://ya.ru/&nosync=1")
        try:
            city_input = self.driver.find_element(
                By.CSS_SELECTOR, "input[placeholder='Город']"
            )
            city_input.clear()
            city_input.send_keys(region)
            city_input.submit()
            
            self.logger.log(
                "https://ya.ru/",
                str(self.mobile_config),
                self.ip,
                action="Region changed",
            )
        
        except:
            self.logger.log(
                "https://ya.ru/",
                str(self.mobile_config),
                self.ip,
                action="Can't change region",
            )

    def __resolve_captcha(self):
        try:
            elem: WebElement = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "js-button"))
            )
            elem.click()

        except:
            self.logger.log(
                "https://ya.ru/",
                str(self.mobile_config),
                self.ip,
                action="Captcha not found",
            )


def main(type: str = "", ip: str = ""):
    browser = VirtualBrowser(type, ip)
    browser.find_advert(CONFIG.search_term)
