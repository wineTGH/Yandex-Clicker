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

from utils import clamp
from logger import Logger
import config as CONFIG
import agents


class VirtualBrowser:
    driver: webdriver.Chrome
    mobile_config: dict = {
        "userAgent": "<host>"
    }

    xpath_dict = {
        "search-input": '//*[@id="text"]',
        "search-result": '//*[@id="search-result"]',
        "search-cards": './/*[@class="serp-item"]',
        "text-element": ".//div/div[3]/div[1]/span/span[1]",
        "ad-link-element": ".//div/div[1]/a",
    }

    def __init__(self):
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

            self.xpath_dict.update({
                "search-input": '//input[@type="search"]',
                "text-element": ".//div/div[2]/div[1]/span/span[1]",
            })
        # --- End of mobile settings --- #

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(
            options=options, executable_path="./Drivers/chromedriver"
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

    def find_advert(self, search_term: str):
        self.driver.get("https://ya.ru/")
        input()
        search_input = self.driver.find_element(By.XPATH, self.xpath_dict.get("search-input"))
        search_input.send_keys(search_term)
        search_input.submit()

        search_cards = self.driver.find_element(By.XPATH, self.xpath_dict.get("search-result"))\
            .find_elements(By.CLASS_NAME, "serp-item")
        
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
                        ad_links.append(link)

            except:
                continue
        
        if hasattr(CONFIG, 'index') and len(ad_links) > 0:
            ad_link = ad_links[clamp(0, CONFIG.index - 1, len(ad_links) - 1)]

        elif len(ad_links) > 0:
            ad_link = ad_links[0]
        
        else:
            return

        link = self.__get_url(ad_link)
        ad_link.click()

        time.sleep(2)

        Logger().log(link, str(self.mobile_config), action="clicked")

        try:
            elem = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, "div")
                )
            )

            time.sleep(random.randint(*CONFIG.delay_interval))

        finally:
            print("Page loaded")


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

def main():
    browser = VirtualBrowser()
    browser.find_advert(CONFIG.search_term)


if __name__ == "__main__":
    main()
