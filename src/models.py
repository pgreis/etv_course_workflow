import random
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

from playwright.sync_api import Page
from pydantic import BaseModel, ConfigDict, Field, SecretStr


#  generall
class PlaywrightPipelineContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ctx: Dict[str, Any] = {}
    page: Optional[Page] = None
    error: Optional[str] = None

class PlaywrightPipelineStep(ABC):
    name : str
    add_wait_time: Optional[float] = random.randint(2, 3)

    @abstractmethod
    def execute(self, ctx: PlaywrightPipelineContext) -> PlaywrightPipelineContext:
        pass

class MainContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ctx: Dict[str, Any] = {}



# login
class LoginLocators(BaseModel):
    username: str = Field('input[formcontrolname="username"]')
    password: str = Field('input[type="password"]')
    checkbox: str = Field('input[type="checkbox"]')
    submit_button: str = Field('button[type="submit"]')

class LoginCredentials(BaseModel):
    username: SecretStr
    password: SecretStr


