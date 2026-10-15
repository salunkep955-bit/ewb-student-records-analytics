from datetime import date
from sqlalchemy import String, Date, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Student(Base):
    __tablename__ = "students"
    student_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    course: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    enrollment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
