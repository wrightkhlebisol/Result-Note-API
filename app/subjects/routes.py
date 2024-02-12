from flask import request, jsonify, Response

from app import db
from app.subjects import bp
from app.models import Subjects
from app.schemas import SubjectsSchema
from app.errors.handlers import bad_request

from flask_jwt_extended import jwt_required, current_user

from marshmallow import ValidationError

import asyncio
from aiohttp import ClientSession

# Declare database schemas so they can be returned as JSON objects
subject_schema = SubjectsSchema()
subjects_schema = SubjectsSchema(many=True)

@bp.post("/")
@jwt_required()
def submit_subject() -> tuple[Response, int] | Response:
    """
    Lets users submit a subject

    Returns
    -------
    str
        A JSON object containing a success message
    """
    
    try:
        result = subject_schema.load(request.json)
    except ValidationError as e:
        return bad_request(e.messages[0])
    
    subject = Subjects(
        name=result["name"],
        description=result["description"]
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify({'msg': 'Subject created successfully'}), 201


@bp.get("/")
@jwt_required()
def get_subjects() -> tuple[Response, int]:
    """
    Returns all subjects submitted by the user making the request

    Returns
    -------
    JSON
        A JSON object containing all subject data
    """
    subjects = Subjects.query.all()

    return subjects_schema.jsonify(subjects), 200


@bp.get("/<int:id>")
@jwt_required()
def get_subject_by_id(id: int) -> tuple[Response, int] | Response:
    """
    Returns a specific subject based on the ID in the URL

    Parameters
    ----------
    id : int
        The ID of the subject

    Returns
    -------
    JSON
        A JSON object containing all subject data
    """
    subject = Subjects.query.filter_by(id=id).first()

    if not subject:
        return bad_request("No subject found")

    return subject_schema.jsonify(subject), 200


@bp.put("/<int:id>")
@jwt_required()
def update_subject(id: int) -> tuple[Response, int] | Response:
    """
    Lets users retrieve a user profile when logged in

    Parameters
    ----------
    id : int
        The ID of the subject to be updated

    Returns
    -------
    str
        A JSON object containing the success message
    """
    subject = Subjects.query.get(id)

    if not subject:
        return bad_request("Subject not found")

    try:
        result = subject_schema.load(request.json)
    except ValidationError as e:
        return bad_request(e.messages[0])

    for k, v in result.items():
        setattr(subject, k, v)
    
    db.session.commit()

    return jsonify({"msg": "Subject succesfully updated"}), 201


@bp.delete("/<int:id>")
@jwt_required()
def delete_subject(id: int) -> tuple[Response, int] | Response:
    """
    Lets users retrieve a user profile when logged in

    Parameters
    ----------
    id : int
        The ID of the subject to be deleted

    Returns
    -------
    str
        A JSON object containing the success message
    """
    subject = Subjects.query.get(id)

    if not subject:
        return bad_request("Subject not found")

    db.session.delete(subject)
    db.session.commit()

    return jsonify({"msg": "Subject succesfully deleted"}), 201

