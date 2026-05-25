from abc import ABC, abstractmethod
import time
from typing import List, Optional
import logging

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException,
)
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
            try:
                result = step.execute(ctx)
                ctx[step.name] = result

                if ctx.get("stop_loop"):
                    logger.info(f"Stopping pipeline after step '{step.name}' because stop_loop=True")
                    break
            
            except TimeoutException as e:

                logger.exception(
                    f"[TIMEOUT] Step '{step.name}' timed out",
                    extra={
                        "step": step.name,
                        "error_type": type(e).__name__,
                    }
                )

                break

            except NoSuchElementException as e:

                logger.exception(
                    f"[ELEMENT_NOT_FOUND] Step '{step.name}' failed",
                    extra={
                        "step": step.name,
                        "error_type": type(e).__name__,
                    }
                )

                break

            except StaleElementReferenceException as e:

                logger.exception(
                    f"[STALE_ELEMENT] Step '{step.name}' failed",
                    extra={
                        "step": step.name,
                        "error_type": type(e).__name__,
                    }
                )

                break

            except ElementClickInterceptedException as e:

                logger.exception(
                    f"[CLICK_INTERCEPTED] Step '{step.name}' failed",
                    extra={
                        "step": step.name,
                        "error_type": type(e).__name__,
                    }
                )

                break

            except WebDriverException as e:

                logger.exception(
                    f"[WEBDRIVER_ERROR] Step '{step.name}' failed",
                    extra={
                        "step": step.name,
                        "error_type": type(e).__name__,
                    }
                )



        return ctx