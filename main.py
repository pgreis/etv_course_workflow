# base python
import os
import logging
import sys
import time

# third party
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# internal moduls
from db_handler import DatabaseHandler
from src.help_fns import (get_tomorrow_weekday_abbr,
                          get_active_courses_by_weekday,
                          fill_locator,
                          run_filter_until_correct)
from src.pipeline_core import SeleniumPipelineEngine
from src.pipeline_steps import (ClickSectionIsBlockingStep,
                                CheckIfConditionMetStep,
                                CheckIfAnyElementExistsStep,
                                StopLoopIfStep,
                                GoToUrlStep,
                                ClickElementStep,
                                FillInputStep,
                                GetElementAttributeStep)

# models
from src.models import (
    DatabaseConfig,
    LoginLocators,
    LoginCredentials,
    FilterLocators,
    VisitCoursePageLocators,
    BookingPersona,
    BookingLocators
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


def main():
    
    # db
    db_conf = DatabaseConfig(db_url=os.getenv("DB_URL"), # TODO: centralize location for set env vars
                             table_name=os.getenv("TABLE_NAME")) # TODO: centralize location for set env varsc


    db = DatabaseHandler(db_url=db_conf.db_url) # TODO: centralize location for set env vars
    db.load_table(table_name=db_conf.table_name) # TODO: centralize location for set env vars

    weekday_abbr=get_tomorrow_weekday_abbr(add_n_hours=24) # TODO: hard coded
    active_courses = get_active_courses_by_weekday(course_table=db.loaded_table,
                                                   weekday_ger_abb=weekday_abbr)

    if not active_courses:
        logger.info("No active courses for %s", weekday_abbr)
        sys.exit()


    # driver
    IS_HEADLESS = True

    options = Options()
    if IS_HEADLESS:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    time.sleep(10) 
    driver.maximize_window()

    # login
    login_locators = LoginLocators()
    login_credentials = LoginCredentials(username=os.getenv("LOGIN_NAME"), # TODO: centralize location for set env vars
                                        password=os.getenv("LOGIN_PW")) # TODO: centralize location for set env vars
    login_url = os.getenv("LOGIN_URL") # TODO: centralize location for set env vars

    login_pipeline = SeleniumPipelineEngine(
        steps=[
            GoToUrlStep(name="Go to Login Page", url=login_url, driver=driver),
            FillInputStep(name="Fill Username", xpath=login_locators.username, value=login_credentials.username.get_secret_value(), driver=driver),
            FillInputStep(name="Fill Password", xpath=login_locators.password, value=login_credentials.password.get_secret_value(), driver=driver),
            # ClickElementStep(name="Click Checkbox", xpath=login_locators.checkbox, driver=driver),
            ClickElementStep(name="Click Submit", xpath=login_locators.submit_button, driver=driver)
        ]
    )

    login_pipeline.run()

    ### loop start

    for active_course in active_courses:
        logger.info("\n------------------------------")
        logger.info(f"Processing course: {active_course['orig_course_name']} on {active_course['weekday']} for person {active_course['person']}")
        logger.info("------------------------------\n")

        # prepare bookin process
        booking_persona = BookingPersona(person=active_course['person'],
                                         course_name=active_course['orig_course_name'],
                                         weekday=active_course['weekday'],
                                         invoice_person=os.getenv("INVOICE_PERSON")) # TODO: centralize location for set env vars


        # filter
        filter_locators = FilterLocators()
        filter_locators.location_filled = fill_locator(filter_locators.location, "Sportzentrum Hoheluft")
        filter_locators.weekday_filled = fill_locator(filter_locators.weekday, active_course['weekday']) 
        filter_locators.apply_filter_filled = fill_locator(filter_locators.apply_filter, "Angebote anzeigen")


        CORRECT_FILTER_NUMBER = 3 # TODO: hard coded

        filter_pipeline = SeleniumPipelineEngine(
            steps=[
                GoToUrlStep(name="Go to Course Overview", url=os.getenv("COURSE_OVERVIEW_URL"), driver=driver),
                ClickSectionIsBlockingStep(driver=driver, add_wait_time=10.0),
                ClickElementStep(name="Click Filter Button", xpath=filter_locators.filter, add_wait_time=12.0, driver=driver),
                ClickElementStep(name="Click Location Dropdown", xpath=filter_locators.location_filled, driver=driver),
                ClickElementStep(name="Click Weekday Option", xpath=filter_locators.weekday_filled,  driver=driver),
                ClickElementStep(name="Click Apply Filter Button", xpath=filter_locators.apply_filter_filled, driver=driver),
                GetElementAttributeStep(name="Get Applied Filter Number", xpath=filter_locators.filter_number, attribute="text", driver=driver),
                CheckIfConditionMetStep(name="Check if correct filter number is applied", condition=lambda ctx: int(ctx.get("Get Applied Filter Number", "0")) == CORRECT_FILTER_NUMBER)
            ]
        )

        last_filter_run_ctx = run_filter_until_correct(filter_pipeline=filter_pipeline)

        # visit
        visit_course_locators = VisitCoursePageLocators()
        visit_course_locators.course_filled = fill_locator(visit_course_locators.course, active_course['orig_course_name'])


        visit_course_pipeline = SeleniumPipelineEngine(
            steps=[
                GetElementAttributeStep(name="Get course link", xpath=visit_course_locators.course_filled, attribute="href", driver=driver),
                GoToUrlStep(name="Go to Course Page", url=lambda ctx: ctx["Get course link"], driver=driver),
                ])

        visit_course_pipeline.run()

        # booking
        booking_locators = BookingLocators()
        booking_locators.cancelled_filled = fill_locator(booking_locators.cancelled, "Der Verein hat diesen Termin abgesagt")
        booking_locators.bookable_filled = fill_locator(booking_locators.bookable, "Buchen für")
        booking_locators.book_person_filled = fill_locator(booking_locators.book_person, "Buchen für", booking_persona.person)
        booking_locators.invoice_person_filled = fill_locator(booking_locators.invoice_person, "Rechnungsempfänger", booking_persona.invoice_person)
        booking_locators.aggree_terms_filled = fill_locator(booking_locators.aggree_terms, "Teilnahme- und Stornierungsbedingungen")
        booking_locators.confirm_booking_filled = fill_locator(booking_locators.confirm_booking, "Verbindlich buchen")
        booking_locators.is_booked_filled = fill_locator(booking_locators.is_booked, booking_persona.person)


        booking_pipeline = SeleniumPipelineEngine(
            steps=[
                ClickSectionIsBlockingStep(driver=driver),
                CheckIfAnyElementExistsStep(name="Check if course is bookable", xpath=booking_locators.book_person_filled, driver=driver),
                StopLoopIfStep(name="Stop if not bookable", condition=lambda ctx: not ctx.get("Check if course is bookable", False)),
                ClickElementStep(name="Click Book Person Dropdown", xpath=booking_locators.book_person_filled, driver=driver),
                ClickElementStep(name="Click Invoice Person Dropdown", xpath=booking_locators.invoice_person_filled, driver=driver),
                ClickElementStep(name="Click Agree Terms Checkbox", xpath=booking_locators.aggree_terms_filled, driver=driver),
                ClickElementStep(name="Click Confirm Booking Button", xpath=booking_locators.confirm_booking_filled, driver=driver),
                CheckIfAnyElementExistsStep(name="Check if booking is successful", xpath=booking_locators.is_booked_filled, driver=driver)
            ]
        )
            
        booking_pipeline_ctx = booking_pipeline.run()

        logger.info("Booking pipeline completed.")
        logger.info(f"Booking ctx: {active_course['orig_course_name']} on {active_course['weekday']} for {active_course['person']}: {booking_pipeline_ctx}")
    
if __name__ == "__main__":
    main()