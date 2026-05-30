import time
import logging
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException
)
from src.pipeline_core import SeleniumStep #, SaveHtml, SavePng

logger = logging.getLogger(__name__)


# delete
from pathlib import Path
from datetime import datetime

DEBUG_DIR = Path("/app/debug")

def dump_page(driver, prefix="debug"):
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    (DEBUG_DIR / f"{prefix}_{ts}.html").write_text(
        driver.page_source,
        encoding="utf-8"
    )

    driver.save_screenshot(
        str(DEBUG_DIR / f"{prefix}_{ts}.png")
    )

    (DEBUG_DIR / f"{prefix}_{ts}.url").write_text(
        driver.current_url,
        encoding="utf-8"
    )

class DumpPageStep(SeleniumStep):

    def __init__(self, driver: Optional[WebDriver] = None, name:str="Dump Page", add_wait_time: Optional[float] = 0.1, debug_dir:Path=Path("/app/debug"), prefix:str="debug"):
        self.driver = driver
        self.name = name
        self.add_wait_time = add_wait_time
        self.debug_dir = debug_dir
        self.prefix = prefix

    def execute(self, ctx: dict=None) -> None:
        self.debug_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        (DEBUG_DIR / f"{self.prefix}_{ts}.html").write_text(
            self.driver.page_source,
            encoding="utf-8"
        )

        self.driver.save_screenshot(
            str(DEBUG_DIR / f"{self.prefix}_{ts}.png")
        )

        (DEBUG_DIR / f"{self.prefix}_{ts}.url").write_text(
            self.driver.current_url,
            encoding="utf-8"
        )




class ClickSectionIsBlockingStep(SeleniumStep):

    def __init__(self, driver: Optional[WebDriver] = None, name:str="Click Section Is Blocking", add_wait_time: Optional[float] = 5.0):
        self.driver = driver
        self.name = name
        self.add_wait_time = add_wait_time
    
    def execute(self, ctx: dict=None, xpath: str = '//button[contains(normalize-space(), "Nein")]') -> None:
        try:      
            time.sleep(self.add_wait_time or 0)     
            element = WebDriverWait(driver=self.driver, timeout=20).until(EC.presence_of_element_located(locator = (By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].click();", element)        
            
        except (TimeoutException,
                NoSuchElementException,
                StaleElementReferenceException,
            ) as e:
            logger.exception(f"NOT RAISED in {self.name}: {e}  | xpath : {xpath} ")
            
            dump_page(self.driver, "blocking")

            # self.driver.save_screenshot(png_path_button)
            # with open(html_path_button, "w", encoding="utf-8") as f:
            #     f.write(self.driver.page_source)

            # SaveHtml(driver=self.driver, name=self.name)
            # SavePng(driver=self.driver, name=self.name)

            return None

class StopLoopIfStep(SeleniumStep):
    def __init__(self, name:str, condition: callable, driver: Optional[WebDriver] = None):
        self.name = name
        self.condition = condition
        self.driver = driver

    def execute(self, ctx):
        ctx["stop_loop"] = self.condition(ctx)
        return ctx["stop_loop"]

class GoToUrlStep(SeleniumStep):
    def __init__(self, name:str, url:str, driver: Optional[WebDriver] = None, add_wait_time: Optional[float] = 3.0, add_wait_time_after: Optional[float] = 8.0):
        self.name = name
        self.url = url
        self.driver = driver
        self.add_wait_time = add_wait_time
        self.add_wait_time_after = add_wait_time_after

    def execute(self, ctx: dict=None) -> str:
        try:    
            logger.info(f"Go to: {self.url}")
            time.sleep(self.add_wait_time or 0)  
            resolved_url = self.url(ctx) if ctx else self.url
            self.driver.get(resolved_url)
            time.sleep(self.add_wait_time_after or 0) 
            logger.info(f"Current Url: {self.driver.current_url}")
            return resolved_url
        
        except (TimeoutException,
                NoSuchElementException,
                StaleElementReferenceException ) as e:
            logger.exception(f"Exception RAISED {self.name}: {e}  | url : {self.url}")
            raise
            
class ClickElementStep(SeleniumStep):
    def __init__(self, name:str, xpath:str,  add_wait_time: Optional[float] = 3.5, driver: Optional[WebDriver] = None):
        self.name = name
        self.xpath = xpath
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> None:
        try:
            time.sleep(self.add_wait_time or 0)
            element = WebDriverWait(driver=self.driver, timeout=20).until(EC.element_to_be_clickable(mark = (By.XPATH, self.xpath)))
            element.click()
        except (TimeoutException,
                NoSuchElementException,
                StaleElementReferenceException,
                ElementClickInterceptedException,
                WebDriverException) as e:
            logger.exception(f"Exception RAISED {self.name}: {e}  | xpath : {self.xpath}")


            dump_page(self.driver, "click")
            # SaveHtml(driver=self.driver, name=self.name)
            # SavePng(driver=self.driver, name=self.name)
            # self.driver.save_screenshot(png_path_button)
            # with open(html_path_button, "w", encoding="utf-8") as f:
            #     f.write(self.driver.page_source)
                
            raise

class FillInputStep(SeleniumStep):
    def __init__(self, name:str, xpath:str, value:str, add_wait_time: Optional[float] = 3.5, driver: Optional[WebDriver] = None):
        self.name = name
        self.xpath = xpath
        self.value = value
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> None:
        try:
            time.sleep(self.add_wait_time or 0)
            element = WebDriverWait(driver=self.driver, timeout=20).until(EC.presence_of_element_located(locator = (By.XPATH, self.xpath)))
            element.send_keys(self.value)
        except (TimeoutException,
                NoSuchElementException,
                StaleElementReferenceException) as e:
            logger.exception(f"Exception RAISED {self.name}: {e}  | xpath : {self.xpath}")
            raise

class GetElementAttributeStep(SeleniumStep):
    def __init__(self, name: str, xpath: str, attribute: str, add_wait_time: Optional[float] = 3.5, driver: Optional[WebDriver] = None):
        self.name = name
        self.xpath = xpath
        self.attribute = attribute
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> Optional[str]:
        try:
            time.sleep(self.add_wait_time or 0)
            element = WebDriverWait(driver=self.driver, timeout=20).until(
                EC.presence_of_element_located((By.XPATH, self.xpath))
            )

            getters = {
                "text": lambda el: el.text,
                "href": lambda el: el.get_attribute("href"),
            }

            getter = getters.get(self.attribute, lambda el: el.get_attribute(self.attribute))
            return getter(element)
        except (TimeoutException,
                NoSuchElementException,
                StaleElementReferenceException) as e:
                        logger.exception(f"Exception NOT RAISED {self.name}: {e} | attibute : {self.attribute} | xpath : {self.xpath}")

            


class CheckIfAnyElementExistsStep(SeleniumStep):
    def __init__(self, name: str, xpath: str, add_wait_time: Optional[float] = 3.5, driver: Optional[WebDriver] = None):
        self.name = name
        self.xpath = xpath
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> bool:
        time.sleep(self.add_wait_time or 0)
        elements = self.driver.find_elements(By.XPATH, self.xpath)
        return len(elements) > 0
    
class CheckIfConditionMetStep(SeleniumStep):
    def __init__(self, name: str, condition: callable, add_wait_time: Optional[float] = 3.5, driver: Optional[WebDriver] = None):
        self.name = name
        self.condition = condition
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> bool:
        time.sleep(self.add_wait_time or 0)
        return self.condition(ctx)
