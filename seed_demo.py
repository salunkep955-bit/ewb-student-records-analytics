"""Insert fictional demo records. Never use real student information."""
from datetime import date
from sqlalchemy import select
from database import Base, engine, SessionLocal
from models import Student

SAMPLE = [
    {"student_id":"EWB-1001","name":"Aarav Patil","date_of_birth":date(2005,4,12),"email":"aarav.demo@example.com","phone":"9000001001","course":"Mechanical Engineering","address":"Demo Address A","enrollment_date":date(2024,8,1)},
    {"student_id":"EWB-1002","name":"Meera Shah","date_of_birth":date(2004,11,3),"email":"meera.demo@example.com","phone":"9000001002","course":"Data Analytics","address":"Demo Address B","enrollment_date":date(2023,8,1)},
    {"student_id":"EWB-1003","name":"Kabir Deshmukh","date_of_birth":date(2006,2,21),"email":"kabir.demo@example.com","phone":"9000001003","course":"Mechanical Engineering","address":"Demo Address C","enrollment_date":date(2025,8,1)},
    {"student_id":"EWB-1004","name":"Anaya Joshi","date_of_birth":date(2003,7,15),"email":"anaya.demo@example.com","phone":None,"course":"Python Development","address":"Demo Address D","enrollment_date":date(2022,8,1)},
    {"student_id":"EWB-1005","name":"Ishaan Kulkarni","date_of_birth":date(2005,9,8),"email":"ishaan.demo@example.com","phone":"9000001005","course":"Data Analytics","address":"Demo Address E","enrollment_date":date(2024,8,1)},
]
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    inserted = 0
    for row in SAMPLE:
        if not db.scalar(select(Student).where(Student.student_id == row["student_id"])):
            db.add(Student(**row))
            inserted += 1
    db.commit()
print(f"Demo data ready. Added {inserted} fictional student records.")
