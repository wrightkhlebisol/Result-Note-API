from app import db, ma
from app.dashboard import bp
from app.errors.handlers import bad_request
from app.models import Users, Classes, Subjects, Scores, Schools, Reports
from app.schemas import UsersSchema, ClassesSchema, SubjectsSchema, ScoresSchema, SchoolsSchema, ReportsSchema
from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy.orm import joinedload


school_schema = SchoolsSchema()
user_schema = UsersSchema(exclude=["password_hash", "created_at", "updated_at"])    
users_schema = UsersSchema(many=True, exclude=["password_hash", "created_at", "updated_at"])
subjects_schema = SubjectsSchema(many=True)

@bp.get("")
@jwt_required()
def dashboard() -> Response:
    """
    Returns all the data for the dashboard

    Returns
    -------
    JSON
        A JSON object containing all the data for the dashboard
    """

    school_details = Schools.query.options(joinedload(Schools.owner)).filter_by(owner=current_user).outerjoin(Schools.students).first()
    
    try:
        school_detail = school_schema.dump(school_details)
        school_detail["students"] = user_schema.dump(school_details.students, many=True)
        school_detail["teachers"] = users_schema.dump(school_details.teachers)
        school_detail["owner"] = user_schema.dump(school_details.owner)
        school_detail["subjects"] = subjects_schema.dump(school_details.subjects)
        school_detail["classes"] = subjects_schema.dump(school_details.classes)
    except Exception as e:
        return bad_request(e.messages), 400
    
    reports_count = 0
    for student in school_details.students:
        if student.reports:
            reports_count += 1
        
    student_count = len(school_details.students)
    teacher_count = len(school_details.teachers)
    subject_count = len(school_details.subjects)
    class_count = len(school_details.classes)
    
    school_detail["school_summary"] = {
        "student_count": student_count,
        "teacher_count": teacher_count,
        "class_count": class_count,
        "subject_count": subject_count,
        "reports_count": reports_count
    }
    
    return jsonify(school_detail), 200