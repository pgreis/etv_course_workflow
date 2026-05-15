from src.models import PlaywrightPipelineContext, PlaywrightPipelineStep
import time
from pydantic import SecretStr
from typing import Union

class GoToLoginPageStep(PlaywrightPipelineStep):
    name = "Go To Login Page"
    
    def __init__(self, url:str):
        self.url = url

    def execute(self, ctx: PlaywrightPipelineContext) -> PlaywrightPipelineContext:
        page = ctx.page
        page.goto(self.url)
        time.sleep(self.add_wait_time or 0)
        return ctx

class FillUsernameStep(PlaywrightPipelineStep):
    name = "Fill Username"
    
    def __init__(self, locator:str, username:str):
        self.locator = locator
        self.username = username

    def execute(self, ctx: PlaywrightPipelineContext) -> PlaywrightPipelineContext:
        page = ctx.page
        username = self.username.get_secret_value() if isinstance(self.username, SecretStr) else self.username
        page.fill(self.locator, username)
        time.sleep(self.add_wait_time or 0)
        return ctx

class FillPasswordStep(PlaywrightPipelineStep):
    name = "Fill Password"
    
    def __init__(self, locator:str, password:str):
        self.locator = locator
        self.password = password

    def execute(self, ctx: PlaywrightPipelineContext) -> PlaywrightPipelineContext:
        page = ctx.page
        password = self.password.get_secret_value() if isinstance(self.password, SecretStr) else self.password
        page.fill(self.locator, password)
        time.sleep(self.add_wait_time or 0)
        return ctx
    
class ClickCheckboxStep(PlaywrightPipelineStep):
    name = "Click Checkbox"
    
    def __init__(self, locator:str):
        self.locator = locator

    def execute(self, ctx: PlaywrightPipelineContext) -> PlaywrightPipelineContext:
        page = ctx.page
        page.click(self.locator)
        time.sleep(self.add_wait_time or 0)
        return ctx
    
class ClickSubmitStep(PlaywrightPipelineStep):
    name = "Click Submit"
    
    def __init__(self, locator:str):
        self.locator = locator

    def execute(self, ctx: PlaywrightPipelineContext) -> PlaywrightPipelineContext:
        page = ctx.page
        page.click(self.locator)
        time.sleep(self.add_wait_time or 0)
        return ctx