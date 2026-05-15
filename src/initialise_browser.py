from playwright.sync_api import sync_playwright

def get_sync_browser(headless=True, browser_type="chromium"):

    launcher = {
        "chromium": lambda: playwright.chromium.launch(headless=headless),
        "firefox": lambda: playwright.firefox.launch(headless=headless),
        "webkit": lambda: playwright.webkit.launch(headless=headless),
    }
    playwright = sync_playwright().start()
    browser = launcher.get(browser_type, launcher["chromium"])()
    return browser

def create_page(browser):
    return browser.new_page()
