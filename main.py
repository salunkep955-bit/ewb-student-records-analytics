import json
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

import httpx
from fastapi import FastAPI, Depends, HTTPException, Query, Response
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from database import Base, DATABASE_URL, get_db
from models import Student
from schemas import StudentCreate, StudentUpdate, StudentOut, AnalyticsSummary, CourseCount
from analytics import build_analytics_summary, course_counts, age_buckets, students_to_csv

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="EWB Student Records & Analytics API",
    description="Student CRUD, data quality validation, analytics, CSV export, and optional local Ollama Q&A.",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/", tags=["Health"])
def root():
    return {"message": "EWB Student Records & Analytics API is running", "docs": "/docs", "analytics": "/analytics/summary"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

@app.post("/students", response_model=StudentOut, status_code=201, tags=["Students"])
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    if db.get(Student, payload.student_id):
        raise HTTPException(status_code=409, detail="A student with this student_id already exists.")
    if payload.email and db.scalar(select(Student).where(func.lower(Student.email) == payload.email.lower())):
        raise HTTPException(status_code=409, detail="A student with this email already exists.")
    student = Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@app.get("/students", response_model=list[StudentOut], tags=["Students"])
def list_students(
    q: Optional[str] = Query(None, description="Search name, ID, email, or course"),
    course: Optional[str] = None,
    enrolled_after: Optional[date] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Student)
    if q:
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            Student.name.ilike(term) | Student.student_id.ilike(term) |
            Student.email.ilike(term) | Student.course.ilike(term)
        )
    if course:
        stmt = stmt.where(func.lower(Student.course) == course.lower())
    if enrolled_after:
        stmt = stmt.where(Student.enrollment_date >= enrolled_after)
    if born_after:
        stmt = stmt.where(Student.date_of_birth > born_after)
    if born_before:
        stmt = stmt.where(Student.date_of_birth < born_before)
    return list(db.scalars(stmt.order_by(Student.name.asc()).offset(offset).limit(limit)).all())

@app.get("/students/{student_id}", response_model=StudentOut, tags=["Students"])
def get_student(student_id: str, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student

@app.put("/students/{student_id}", response_model=StudentOut, tags=["Students"])
def replace_student(student_id: str, payload: StudentCreate, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    if payload.student_id != student_id:
        raise HTTPException(status_code=400, detail="student_id in the body must match the URL.")
    if payload.email:
        duplicate = db.scalar(select(Student).where(
            (func.lower(Student.email) == payload.email.lower()) & (Student.student_id != student_id)
        ))
        if duplicate:
            raise HTTPException(status_code=409, detail="A student with this email already exists.")
    for key, value in payload.model_dump().items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student

@app.patch("/students/{student_id}", response_model=StudentOut, tags=["Students"])
def update_student(student_id: str, payload: StudentUpdate, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("student_id") not in (None, student_id):
        raise HTTPException(status_code=400, detail="student_id cannot be changed.")
    if changes.get("email"):
        duplicate = db.scalar(select(Student).where(
            (func.lower(Student.email) == changes["email"].lower()) & (Student.student_id != student_id)
        ))
        if duplicate:
            raise HTTPException(status_code=409, detail="A student with this email already exists.")
    changes.pop("student_id", None)
    for key, value in changes.items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student

@app.delete("/students/{student_id}", status_code=204, tags=["Students"])
def delete_student(student_id: str, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    db.delete(student)
    db.commit()
    return Response(status_code=204)

@app.get("/analytics/summary", response_model=AnalyticsSummary, tags=["Analytics"])
def analytics_summary(db: Session = Depends(get_db)):
    return build_analytics_summary(list(db.scalars(select(Student)).all()))

@app.get("/analytics/courses", response_model=list[CourseCount], tags=["Analytics"])
def analytics_courses(db: Session = Depends(get_db)):
    return course_counts(list(db.scalars(select(Student)).all()))

@app.get("/analytics/age-distribution", tags=["Analytics"])
def analytics_age_distribution(db: Session = Depends(get_db)):
    return age_buckets(list(db.scalars(select(Student)).all()))

@app.get("/students/export.csv", tags=["Analytics"])
def export_students_csv(db: Session = Depends(get_db)):
    csv_text = students_to_csv(list(db.scalars(select(Student).order_by(Student.name.asc())).all()))
    return Response(content=csv_text, media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="students_export.csv"'})

@app.post("/ai/ask", tags=["Optional AI"])
async def ask_local_ai(question: str = Query(..., min_length=3, max_length=500), db: Session = Depends(get_db)):
    """Optional Ollama Q&A. The model receives aggregates, not database access or SQL execution ability."""
    students = list(db.scalars(select(Student)).all())
    context = build_analytics_summary(students)
    context["courses"] = course_counts(students)
    context["age_distribution"] = age_buckets(students)
    prompt = (
        "Answer only using the JSON facts. If insufficient, say so. Do not invent values. "
        f"FACTS: {json.dumps(context, default=str)}\nQUESTION: {question}\nANSWER:"
    )
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post("http://localhost:11434/api/generate",
                json={"model": "llama3.2:1b", "prompt": prompt, "stream": False})
            response.raise_for_status()
        return {"model": "llama3.2:1b", "answer": response.json().get("response", "").strip()}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama is not running. Install Ollama and run: ollama pull llama3.2:1b")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Ollama returned HTTP {exc.response.status_code}.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama request timed out.")
