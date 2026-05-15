from src.models import LoginLocators, LoginCredentials, PlaywrightPipelineContext
from src.initialise_browser import get_sync_browser

from src.pipeline_core import PlaywrightPipelineEngine

from src.login_steps import (
    GoToLoginPageStep,
    FillUsernameStep,
    FillPasswordStep,
    ClickCheckboxStep,
    ClickSubmitStep)

from dotenv import load_dotenv
import os
from pydantic import SecretStr
load_dotenv()


def main():
    
    
    # initialise browser
    browser = get_sync_browser(headless=False, browser_type="chromium")
    page = browser.new_page()
    
    login_locators = LoginLocators()
    login_credentials = LoginCredentials(
        username=os.getenv("LOGIN_NAME"),
        password=os.getenv("LOGIN_PW")
    )
    login_url = os.getenv("LOGIN_URL")
    login_ctx = PlaywrightPipelineContext(page=page)

    # login
    LoginPipeline = PlaywrightPipelineEngine(
        steps=[
            GoToLoginPageStep(url=login_url),
            FillUsernameStep(locator=login_locators.username, 
                             username=login_credentials.username),
            FillPasswordStep(locator=login_locators.password,
                             password=login_credentials.password),
            ClickCheckboxStep(locator=login_locators.checkbox),
            ClickSubmitStep(locator=login_locators.submit_button),
            ])

    LoginPipeline.run(login_ctx)

if __name__ == "__main__":
    main()
