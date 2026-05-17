import time
import logging
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.pipeline_core import SeleniumStep


class ClickSectionIsBlockingStep(SeleniumStep):

    def __init__(self, driver: Optional[WebDriver] = None, name:str="Click Section Is Blocking", add_wait_time: Optional[float] = 5.0):
        self.driver = driver
        self.name = name
        self.add_wait_time = add_wait_time
    
    def execute(self, ctx: dict, xpath: str = '//section[contains(normalize-space(@class), "is-blocking")]//button[contains(@class, "close")]') -> None:
        try:      
            time.sleep(self.add_wait_time or 0)     
            element = WebDriverWait(driver=self.driver, timeout=20).until(EC.element_to_be_clickable(mark = (By.XPATH, xpath)))
            element.click()
        except Exception as e:
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
    def __init__(self, name:str, url:str, driver: Optional[WebDriver] = None, add_wait_time: Optional[float] = 3.0):
        self.name = name
        self.url = url
        self.driver = driver
        self.add_wait_time = add_wait_time

    def execute(self, ctx: dict) -> str:
        time.sleep(self.add_wait_time or 0)  
        resolved_url = self.url(ctx) if callable(self.url) else self.url
        self.driver.get(resolved_url)
        return resolved_url
    
class ClickElementStep(SeleniumStep):
    def __init__(self, name:str, xpath:str,  add_wait_time: Optional[float] = 2.0, driver: Optional[WebDriver] = None):
        self.name = name
        self.xpath = xpath
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> None:
        time.sleep(self.add_wait_time or 0)
        element = WebDriverWait(driver=self.driver, timeout=20).until(EC.element_to_be_clickable(mark = (By.XPATH, self.xpath)))
        element.click()

class FillInputStep(SeleniumStep):
    def __init__(self, name:str, xpath:str, value:str, add_wait_time: Optional[float] = 2.0, driver: Optional[WebDriver] = None):
        self.name = name
        self.xpath = xpath
        self.value = value
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> None:
        time.sleep(self.add_wait_time or 0)
        element = WebDriverWait(driver=self.driver, timeout=20).until(EC.presence_of_element_located(locator = (By.XPATH, self.xpath)))
        element.send_keys(self.value)

class GetElementAttributeStep(SeleniumStep):
    def __init__(self, name: str, xpath: str, attribute: str, add_wait_time: Optional[float] = 2.0, driver: Optional[WebDriver] = None):
        self.name = name
        self.xpath = xpath
        self.attribute = attribute
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> Optional[str]:
        time.sleep(self.add_wait_time or 0)
        element = WebDriverWait(driver=self.driver, timeout=20).until(
            EC.presence_of_element_located((By.XPATH, self.xpath))
        )

        getters = {
            "text": lambda el: el.text,
            "href": lambda el: el.get_attribute("href"),
        }

        getter = getters.get(self.attribute, lambda el: el.get_attribute(self.attribute))
        try:
            return getter(element)
        except Exception:
            return None
        
class CheckIfAnyElementExistsStep(SeleniumStep):
    def __init__(self, name: str, xpath: str, add_wait_time: Optional[float] = 2.0, driver: Optional[WebDriver] = None):
        self.name = name
        self.xpath = xpath
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> bool:
        time.sleep(self.add_wait_time or 0)
        elements = self.driver.find_elements(By.XPATH, self.xpath)
        return len(elements) > 0
    
class CheckIfConditionMetStep(SeleniumStep):
    def __init__(self, name: str, condition: callable, add_wait_time: Optional[float] = 2.0, driver: Optional[WebDriver] = None):
        self.name = name
        self.condition = condition
        self.add_wait_time = add_wait_time
        self.driver = driver

    def execute(self, ctx: dict) -> bool:
        time.sleep(self.add_wait_time or 0)
        return self.condition(ctx)
