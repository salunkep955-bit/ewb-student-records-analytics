from datetime import date
from types import SimpleNamespace
from analytics import age_on, build_analytics_summary, course_counts, age_buckets, students_to_csv

def student(student_id, name, dob, email=None, phone=None, course=None, enrollment=None, address=None):
    return SimpleNamespace(student_id=student_id, name=name, date_of_birth=dob, email=email,
        phone=phone, course=course, enrollment_date=enrollment, address=address)

def test_age_on():
    assert age_on(date(2000, 10, 13), date(2026, 10, 13)) == 26
    assert age_on(date(2000, 10, 14), date(2026, 10, 13)) == 25

def test_summary_and_course_counts():
    data = [
        student("1", "A", date(2005, 1, 1), "a@example.com", "1", "Mechanical", date(2024, 8, 1)),
        student("2", "B", date(2004, 1, 1), None, "2", "Mechanical", date(2023, 8, 1)),
        student("3", "C", date(2006, 1, 1), "c@example.com", None, None, None),
    ]
    summary = build_analytics_summary(data)
    assert summary["total_students"] == 3
    assert summary["students_with_email"] == 2
    assert summary["students_with_phone"] == 2
    assert summary["courses_count"] == 1
    assert course_counts(data)[0] == {"course": "Mechanical", "student_count": 2}
    assert course_counts(data)[1] == {"course": "Not specified", "student_count": 1}

def test_age_buckets_and_csv():
    data = [student("1", "A", date(2010, 1, 1), "a@example.com", course="Data", enrollment=date(2024, 1, 1))]
    assert sum(x["student_count"] for x in age_buckets(data)) == 1
    assert "student_id,name,date_of_birth" in students_to_csv(data)
