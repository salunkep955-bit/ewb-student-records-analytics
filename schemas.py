from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

class StudentFields(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    date_of_birth: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=1000)
    enrollment_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_dates_and_contact(self):
        if self.date_of_birth > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        if self.enrollment_date and self.enrollment_date > date.today():
            raise ValueError("enrollment_date cannot be in the future")
        if not self.email and not self.phone:
            raise ValueError("Provide at least an email or phone number")
        return self

class StudentCreate(StudentFields):
    student_id: str = Field(min_length=1, max_length=30, pattern=r"^[A-Za-z0-9_-]+$")

class StudentUpdate(BaseModel):
    student_id: Optional[str] = Field(default=None, min_length=1, max_length=30, pattern=r"^[A-Za-z0-9_-]+$")
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=1000)
    enrollment_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        if self.enrollment_date and self.enrollment_date > date.today():
            raise ValueError("enrollment_date cannot be in the future")
        return self

class StudentOut(StudentFields):
    model_config = ConfigDict(from_attributes=True)
    student_id: str

class AnalyticsSummary(BaseModel):
    total_students: int
    students_with_email: int
    students_with_phone: int
    courses_count: int
    average_age: Optional[float]
    earliest_enrollment: Optional[date]
    latest_enrollment: Optional[date]

class CourseCount(BaseModel):
    course: str
    student_count: int
