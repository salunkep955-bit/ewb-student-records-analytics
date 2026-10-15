from collections import Counter
from datetime import date
from io import StringIO
import csv

def age_on(dob: date, today: date | None = None) -> int:
    today = today or date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def build_analytics_summary(students):
    ages = [age_on(s.date_of_birth) for s in students]
    enrollments = [s.enrollment_date for s in students if s.enrollment_date]
    courses = {s.course.strip().casefold() for s in students if s.course and s.course.strip()}
    return {
        "total_students": len(students),
        "students_with_email": sum(bool(s.email) for s in students),
        "students_with_phone": sum(bool(s.phone) for s in students),
        "courses_count": len(courses),
        "average_age": round(sum(ages) / len(ages), 1) if ages else None,
        "earliest_enrollment": min(enrollments) if enrollments else None,
        "latest_enrollment": max(enrollments) if enrollments else None,
    }

def course_counts(students):
    counts = Counter((s.course.strip() if s.course and s.course.strip() else "Not specified") for s in students)
    return [{"course": name, "student_count": count} for name, count in sorted(counts.items(), key=lambda x: (-x[1], x[0].lower()))]

def age_buckets(students):
    buckets = {"Under 18": 0, "18–20": 0, "21–24": 0, "25+": 0}
    for student in students:
        age = age_on(student.date_of_birth)
        if age < 18: buckets["Under 18"] += 1
        elif age <= 20: buckets["18–20"] += 1
        elif age <= 24: buckets["21–24"] += 1
        else: buckets["25+"] += 1
    return [{"age_group": group, "student_count": count} for group, count in buckets.items()]

def students_to_csv(students):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["student_id", "name", "date_of_birth", "email", "phone", "course", "address", "enrollment_date"])
    for s in students:
        writer.writerow([s.student_id, s.name, s.date_of_birth.isoformat(), s.email or "",
                         s.phone or "", s.course or "", s.address or "",
                         s.enrollment_date.isoformat() if s.enrollment_date else ""])
    return output.getvalue()
