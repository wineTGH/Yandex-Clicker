import random
import json
import re

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import (
    OperatingSystem,
    HardwareType,
)

import config as CONFIG


class VirtualBrowser:
    driver: webdriver.Chrome

    def __init__(self):
        operating_systems = [OperatingSystem.ANDROID.value]
        hardware_types = [HardwareType.MOBILE.value]
        user_agent_rotator = UserAgent(
            operating_systems=operating_systems, hardware_types=hardware_types, limit=10
        )

#        viewport_width = random.randint(300, 500)
#        viewport_height = random.randint(600, 900)

        mobile_emulation = {
            # "deviceMetrics": {
            #     "width": viewport_width,
            #     "height": viewport_height,
            #     "pixelRatio": 3.0,
            # },
            "userAgent": user_agent_rotator.get_random_user_agent(),
        }

        options = webdriver.ChromeOptions()

        if not CONFIG.DEBUG:
            options.add_argument("--headless")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("mobileEmulation", mobile_emulation)

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
        search_input = self.driver.find_element(value="text")
        search_input.send_keys(search_term)
        search_input.submit()

        # Captcha xpath: /html/body/div[1]/div/div/form/div[3]
        # Sound button xpath: /html/body/div[1]/div/div/form/div/div[3]/button[2]

        search_cards = self.driver.find_element(By.ID, "search-result").find_elements(
            By.TAG_NAME, "li"
        )
        ad_links: list[WebElement] = []
        for search_card in search_cards:
            try:
                text_element = search_card.find_element(
                    By.XPATH, ".//div/div[3]/div[1]/span/span[1]"
                )
                print(text_element.text[:-2])
                if text_element.text[:-2] == "Реклама":
                    ad_link = search_card.find_element(By.XPATH, ".//div/div[1]/a")

                    json_data = ad_link.get_attribute("data-bem")
                    json_data = json.loads(json_data)
                    link = json_data.get("click").get("arguments").get("url")
                    for link_mask in CONFIG.link_masks:
                        if re.match(link_mask, link) is not None:
                            ad_links.append(ad_link)
                            break
            except:
                continue

        ad_links[
            max(-(len(ad_links) - 1), min(CONFIG.index - 1, len(ad_links) - 1))
        ].click()


def main():
    browser = VirtualBrowser()
    browser.find_advert(CONFIG.search_term)


if __name__ == "__main__":
    main()
