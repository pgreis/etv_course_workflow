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
