import os
from datetime import datetime

from abc import ABC, abstractmethod
from typing import List, Optional
import logging

from selenium.webdriver.remote.webdriver import WebDriver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # TODO: inject logger or centralize configuration


class SeleniumStep(ABC):
    name : str
    driver : Optional[WebDriver] = None
    
    @abstractmethod
    def execute(self, ctx: dict) -> None:
        pass

class SeleniumPipelineEngine:
    def __init__(self, steps: List[SeleniumStep]):
        self.steps = steps

    def run(self, ctx: dict = None) -> dict:
        ctx = ctx or {}
        for step in self.steps:
            logger.info(f"[STEP] {step.name}")
            result = step.execute(ctx)
            ctx[step.name] = result

            if ctx.get("stop_loop"):
                logger.info(f"Stopping pipeline after step '{step.name}' because stop_loop=True")
                break

        return ctx


class SaveArtifact(ABC):

    def __init__(self, driver: Optional[WebDriver] = None, name:str=None, base_dir:str="/app/debug"):
        self.driver = driver
        self.name = name
        self.base_dir = base_dir

    @abstractmethod
    def save(self):
        pass

class SaveHtml(SaveArtifact):

    def save(self):
        now = datetime.now()
        file_name = self.name + now.strftime("%Y-%m-%d-%H-%M-%S") + ".html"
        save_path = os.path.join(self.base_dir, file_name)

        os.makedirs(self.base_dir, exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)

class SavePng(SaveArtifact):

    def save(self):
        now = datetime.now()
        file_name = self.name + now.strftime("%Y-%m-%d-%H-%M-%S") + ".png"
        save_path = os.path.join(self.base_dir, file_name)

        os.makedirs(self.base_dir, exist_ok=True)
        
        self.driver.save_screenshot(save_path)

