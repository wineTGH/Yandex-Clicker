import random

from selenium import webdriver
from selenium_stealth import stealth
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import (
    OperatingSystem,
    HardwareType,
)

DEBUG = True

class VirtualBrowser:
    driver: webdriver.Chrome

    def __init__(self):
        operating_systems = [OperatingSystem.ANDROID.value]
        hardware_types = [HardwareType.MOBILE.value]
        user_agent_rotator = UserAgent(
            operating_systems=operating_systems, hardware_types=hardware_types, limit=10
        )
        
        viewport_width = random.randint(300, 500)
        viewport_height = random.randint(600, 900)
        
        mobile_emulation = {
            "deviceMetrics": {
                "width": viewport_width,
                "height": viewport_height,
                "pixelRatio": 3.0,
            },
            "userAgent": user_agent_rotator.get_random_user_agent(),
        }

        options = webdriver.ChromeOptions()

        if not DEBUG:
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
        search_box = self.driver.find_element(value='text')
        search_box.send_keys(search_term)
        search_box.submit()

        input()
        cards_selector = "li.serp-item"
        ad_cards_selector = "div.Organic>div.Organic-ContentWrapper>div.TextContainer>span[role=text]>span"


def main():
    browser = VirtualBrowser()
    browser.find_advert("Купить ноутбук")

if __name__ == "__main__":
    main()
