from app import db
from app.errors.handlers import bad_request, error_response
from app.models import Schools, Users
from app.schemas import SchoolsDeserializingSchema, SchoolsSchema
from app.schools import bp
from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required, current_user

school_schema = SchoolsSchema()
schools_schema = SchoolsSchema(many=True)
school_deserializing_schema = SchoolsDeserializingSchema()

@bp.post("/")
@jwt_required()
def create_school() -> tuple[Response, int] | Response:
    """
    Lets users create a school

    Returns
    -------
    str
        A JSON object containing a success message
    """
    try:
        result = school_deserializing_schema.load(request.get_json())
    except Exception as e:
        return bad_request(e.messages)
    
    school = Schools(
        name=result["name"], 
        address=result["address"], 
        color=result["color"],
        phone=result["phone"],
        email=result["email"],
        logo = result["logo"],
        motto = result["motto"],
        city = result["city"],
        state = result["state"],
        country = result["country"]
    )
    
    db.session.add(school)
    db.session.commit()
    return jsonify({"msg": "School created successfully"}), 201


@bp.get("/")
@jwt_required()
def get_all_schools() -> Response:
    """
    Endpoint for retrieving all schools

    Returns
    -------
    str
        A JSON object containing the schools
    """
    try:
        schools = Schools.query.all()
    except Exception as e:
        return bad_request(e.messages)
    
    return schools_schema.jsonify(schools)


@bp.get("/<int:id>")
@jwt_required()
def get_school_by_id(id: int) -> Response:
    """
    Endpoint for retrieving a school by ID

    Parameters
    ----------
    id : int
        ID of the school to be retrieved

    Returns
    -------
    str
        A JSON object containing the school
    """
    try:
        school = Schools.query.get(id)
    except Exception as e:
        return bad_request(e.messages)
    
    if not school:
        return bad_request("School not found"), 404
    
    return school_schema.jsonify(school)


@bp.put("/<int:id>")
@jwt_required()
def update_school(id: int) -> tuple[Response, int] | Response:
    """
    Lets users update a school

    Parameters
    ----------
    id : int
        ID of the school to be updated

    Returns
    -------
    str
        A JSON object containing a success message
    """
    school = Schools.query.filter_by(id=id).first()
    
    if not school:
        return bad_request("School not found"), 404

    try:
        data = school_deserializing_schema.dumps(school)
    except Exception as e:
        return bad_request(e.messages)
    
    for k,v in data.items():
        setattr(school, k, v)
    
    db.session.commit()
    return jsonify({"msg": "School updated successfully"}), 200


@bp.delete("/<int:id>")
@jwt_required()
def delete_school(id: int) -> tuple[Response, int] | Response:
    """
    Lets users delete a school

    Parameters
    ----------
    id : int
        ID of the school to be deleted

    Returns
    -------
    str
        A JSON object containing a success message
    """
    school = Schools.query.get(id)
    
    if not school:
        return bad_request("School not found"), 404
    db.session.delete(school)
    db.session.commit()
    return jsonify({"msg": "School deleted successfully"}), 200