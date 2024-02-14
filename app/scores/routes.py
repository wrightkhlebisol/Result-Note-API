from flask import request, jsonify, Response

from app import db
from app.scores import bp
from app.models import Scores
from app.schemas import ScoresSchema, ScoresDeserializingSchema
from app.errors.handlers import bad_request

from flask_jwt_extended import jwt_required, current_user

from marshmallow import ValidationError

import asyncio
from aiohttp import ClientSession

# Declare database schemas so they can be returned as JSON objects
score_schema = ScoresSchema()
scores_schema = ScoresSchema(many=True)


@bp.post("/")
@jwt_required()
def submit_score() -> tuple[Response, int] | Response:
    """
    Lets users retrieve a user profile when logged in

    Returns
    -------
    str
        A JSON object containing a success message
    """
    try:
        result = score_schema.load(request.json)
    except ValidationError as e:
        return bad_request(e.messages)

    score = Scores(
        score=result["score"],
        term = result["term"],
        session = result["session"],
        type = result["type"]
    )

    db.session.add(score)
    db.session.commit()

    return jsonify({"msg": "Score succesfully submitted"}), 201


@bp.get("/")
@jwt_required()
def get_scores() -> tuple[Response, int]:
    """
    Returns all scores submitted by the user making the request

    Returns
    -------
    JSON
        A JSON object containing all score data
    """
    scores = Scores.query.all()

    return scores_schema.jsonify(scores), 200


@bp.get("/<int:id>")
@jwt_required()
def get_score_by_id(id: int) -> tuple[Response, int] | Response:
    """
    Returns a specific score based on the ID in the URL

    Parameters
    ----------
    id : int
        The ID of the score

    Returns
    -------
    JSON
        A JSON object containing all score data
    """
    score = Scores.query.filter_by(id=id).first()

    if not score:
        return bad_request("No score found"), 404

    return score_schema.jsonify(score), 200


@bp.put("/<int:id>")
@jwt_required()
def update_score(id: int) -> tuple[Response, int] | Response:
    """
    Lets users retrieve a user profile when logged in

    Parameters
    ----------
    id : int
        The ID of the score to be updated

    Returns
    -------
    str
        A JSON object containing the success message
    """
    score = Scores.query.get(id)

    if not score:
        return bad_request("Score not found")
    
    try:
        result = score_schema.load(request.json, partial=True)
    except ValidationError as e:
        return bad_request(e.messages)

    for k, v in result.items():
        setattr(score, k, v)

    db.session.commit()

    return jsonify({"msg": "Score succesfully updated"}), 201


@bp.delete("/<int:id>")
@jwt_required()
def delete_score(id: int) -> tuple[Response, int] | Response:
    """
    Lets users retrieve a user profile when logged in

    Parameters
    ----------
    id : int
        The ID of the score to be deleted

    Returns
    -------
    str
        A JSON object containing the success message
    """
    score = Scores.query.get(id)

    if not score:
        return bad_request("Score not found")

    db.session.delete(score)
    db.session.commit()

    return jsonify({"msg": "Score succesfully deleted"}), 201