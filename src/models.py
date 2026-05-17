from pydantic import BaseModel, Field, SecretStr, ConfigDict
import os

# database
class DatabaseConfig(BaseModel):
    db_url: str
    table_name: str

# login
class LoginLocators(BaseModel):
    username: str = Field(default='//input[@formcontrolname="username"]')
    password: str = Field(default='//input[@type="password"]')
    checkbox: str = Field(default='//input[@type="checkbox"]')
    submit_button: str = Field(default='//button[@type="submit"]')

class LoginCredentials(BaseModel):
    username: SecretStr
    password: SecretStr


# filter
class FilterLocators(BaseModel):

    model_config = ConfigDict(extra="allow")

    filter: str = Field(default='//button[contains(text(), "Filter")]')
    location: str = Field(default='//option[contains(normalize-space(.), "{PLACEHOLDER}")]')
    weekday: str = Field(default='//span[contains(normalize-space(.), "{PLACEHOLDER}")]/preceding-sibling::input')
    apply_filter: str = Field(default='//button[contains(normalize-space(.), "{PLACEHOLDER}")]')
    filter_number: str = Field(default='//button[contains(normalize-space(.), "Filter")]/following-sibling::div')



# visit
class VisitCoursePageLocators(BaseModel):

    model_config = ConfigDict(extra="allow")

    course : str = Field(default='//a[contains(normalize-space(.), "{PLACEHOLDER}")]')


# booking
class BookingPersona(BaseModel):
    person: str 
    course_name: str 
    invoice_person: str
    weekday: str
    location: str = Field(default="Sportzentrum Hoheluft")
   

class BookingLocators(BaseModel):

    model_config = ConfigDict(extra="allow")

    cancelled : str = Field(default='//div[contains(normalize-space(.), "{PLACEHOLDER}")]')
    bookable : str = Field(default='//span[contains(normalize-space(.), "{PLACEHOLDER}")]/following-sibling::kgr-select-control')
    book_person : str = Field(default='//kgr-form-field[@label="{PLACEHOLDER}"]/descendant::option[contains(normalize-space(.), "{PLACEHOLDER}")]') # 1) Buchen für 2) person
    invoice_person : str = Field(default='//kgr-form-field[@label="{PLACEHOLDER}"]/descendant::option[contains(normalize-space(.), "{PLACEHOLDER}")]') # 1) Rechnungsempfänger 2) person
    aggree_terms : str = Field(default='//kgr-form-field[@label="{PLACEHOLDER}"]/descendant::input[@type="checkbox"]')
    confirm_booking : str = Field(default='//button[contains(normalize-space(.), "{PLACEHOLDER}")]')
    is_booked : str = Field(default='//*[contains(normalize-space(.), "Gebucht für {PLACEHOLDER}")]')