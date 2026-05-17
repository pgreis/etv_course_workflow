from datetime import datetime, timedelta
import time
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_tomorrow_weekday_abbr(add_n_hours: int=0) -> str:
    next_day = datetime.now() + timedelta(days=1, hours=add_n_hours)
    return ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][next_day.weekday()]

def get_active_courses_by_weekday(course_table:pd.DataFrame, weekday_ger_abb:str) -> list[dict]:
    return course_table[
      (course_table['is_registration_active']) &
      (course_table['weekday'] == weekday_ger_abb)
      ].to_dict(orient="records")

def fill_locator(template: str, *values) -> str:
    result = template
    for value in values:
        result = result.replace("{PLACEHOLDER}", str(value), 1)
    return result

def run_filter_until_correct(filter_pipeline, max_iterations: int = 3, delay_seconds: int = 15, ctx_condition_key: str = "Get Applied Filter Number", correct_filter_number: int = 3) -> dict:
    ctx = {}
    for i in range(max_iterations):
        logger.info(f"--- filter attempt {i+1}/{max_iterations} ---")
        ctx = filter_pipeline.run()
        if int(ctx.get(ctx_condition_key, "0")) == correct_filter_number:
            logger.info("Correct filter number found!")
            return ctx
        time.sleep(delay_seconds)

    logger.info("Maximum iterations reached.")
    return ctx