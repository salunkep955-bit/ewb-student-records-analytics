# EWB Student Records & Analytics API

**Internship:** Python Backend Development — EWB Edu Tech Pvt. Ltd.  
**Assignment:** Students Database CRUD Application (+ Optional AI Extension)

A professional backend portfolio project built with **Python, FastAPI, SQLite, SQLAlchemy, and Pydantic**. It implements the assignment's four CRUD operations and adds analytics endpoints, data validation, search/filtering, CSV export, tests, and optional local Ollama Q&A.

> Sample records are fictional. Do not upload real student personal information.

## Features

### Required
- Create, read, update, and delete student records
- SQLite persistent storage
- Unique student IDs and duplicate-email checks
- Input validation, missing-record handling, pagination
- Swagger UI for interactive API testing

### Data analyst enhancements
- KPI summary: student count, contact coverage, number of courses, average age, enrollment date range
- Course-wise counts and age-group distribution
- Search by name, ID, email, or course
- Filters by course, date of birth, and enrollment date
- CSV export for Excel or Power BI
- Repeatable fictional demo dataset and unit tests

### Optional AI
The `/ai/ask` endpoint uses local Ollama and `llama3.2:1b`. It receives aggregate reporting facts rather than SQL access. Core CRUD features do not require Ollama.

## Architecture

```text
Swagger UI / API Client
         |
      FastAPI
         |
   Pydantic validation
         |
   SQLAlchemy ORM -------- Analytics helpers
         |
       SQLite
         |
  Optional /ai/ask -> local Ollama
```

## Requirements
- Python 3.10+ (3.11+ recommended)
- pip
- Optional AI: Ollama installed and running locally

## Setup

### Windows PowerShell
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python seed_demo.py
uvicorn main:app --reload
```

### Windows Command Prompt
```bat
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python seed_demo.py
uvicorn main:app --reload
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed_demo.py
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/docs** for interactive Swagger testing. Other useful URLs: `/`, `/health`, `/redoc`, `/analytics/summary`.

The SQLite database `students.db` is created automatically. Run `python seed_demo.py` to insert five fictional records.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/students` | Create student |
| GET | `/students` | List/search/filter students |
| GET | `/students/{student_id}` | Retrieve one student |
| PUT | `/students/{student_id}` | Replace student fields |
| PATCH | `/students/{student_id}` | Partially update fields |
| DELETE | `/students/{student_id}` | Delete student |
| GET | `/analytics/summary` | KPI summary |
| GET | `/analytics/courses` | Course distribution |
| GET | `/analytics/age-distribution` | Age-group distribution |
| GET | `/students/export.csv` | CSV export |
| POST | `/ai/ask?question=...` | Optional local AI |

### Create a student (POST /students)

```json
{
  "student_id": "EWB-2001",
  "name": "Riya Demo",
  "date_of_birth": "2005-06-17",
  "email": "riya.demo@example.com",
  "phone": "9000002001",
  "course": "Data Analytics",
  "address": "Fictional Demo Address",
  "enrollment_date": "2024-08-01"
}
```

Use Swagger's **Try it out** button or send this with curl:

```bash
curl -X POST "http://127.0.0.1:8000/students" \
  -H "Content-Type: application/json" \
  -d '{"student_id":"EWB-2001","name":"Riya Demo","date_of_birth":"2005-06-17","email":"riya.demo@example.com","phone":"9000002001","course":"Data Analytics","enrollment_date":"2024-08-01"}'
```

At least one of email or phone is required. Dates use `YYYY-MM-DD`.

### Search and filter examples
```text
GET /students?q=Riya
GET /students?course=Data%20Analytics
GET /students?born_after=2005-01-01
GET /students?born_before=2006-01-01
GET /students?enrolled_after=2023-01-01
GET /students?limit=20&offset=0
```

### Partial update (PATCH)
```json
{"course": "Python Development"}
```
Send to `/students/EWB-2001`.

### Delete
Send `DELETE /students/EWB-2001`. Successful deletion returns HTTP 204.

### Analytics and CSV
Open `/analytics/summary`, `/analytics/courses`, and `/analytics/age-distribution`. Download `/students/export.csv` and open it in Excel or import it into Power BI. Protect exported data appropriately.

## Optional Ollama setup
1. Install Ollama from its official website.
2. Run:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Keep Ollama running and start FastAPI.
4. Try:
   ```bash
   curl -X POST "http://127.0.0.1:8000/ai/ask?question=How%20many%20students%20are%20there%3F"
   ```

The AI extension is optional. It uses aggregate facts only and is intended for high-level questions. If Ollama is unavailable, core CRUD and analytics endpoints continue to work.

## Tests
```bash
pytest -q
```

## GitHub submission checklist
- [ ] Run the server and check `/docs`
- [ ] Test create, read, update, and delete with fictional data
- [ ] Review analytics endpoints and CSV export
- [ ] Run `pytest -q`
- [ ] Add screenshots of Swagger and analytics responses if desired
- [ ] Ensure `.env`, `students.db`, and real personal information are not committed
- [ ] Push the repository and submit its GitHub URL to the EWB trainer

### Suggested GitHub description
> FastAPI + SQLite student records backend featuring CRUD, validated data, course and age analytics, CSV export, and optional local Ollama Q&A.

## Production limitations
This is an internship/demo project, not a production student information system. Authentication, role-based permissions, audit logs, database migrations, rate limiting, and production CORS restrictions would be needed before real-world deployment.
