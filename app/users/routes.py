from app import db

from app.errors.handlers import bad_request
from app.models import Users
from app.schemas import UsersSchema
from app.users import bp
from flask import Response, request
from flask_jwt_extended import current_user, jwt_required
from marshmallow import ValidationError

# Declare database schemas so they can be returned as JSON objects
user_schema = UsersSchema(exclude=("email", "password_hash"))
users_schema = UsersSchema(many=True, exclude=("email", "password_hash"))

@bp.route("/")
@jwt_required()
def get_all_users() -> tuple[Response, int]:
    """
    Returns all users in the database

    Returns
    -------
    JSON
        A JSON object containing all user data
    """
    users = Users.query.all()
    
    if not users:
        return bad_request("No users found"), 404

    return users_schema.jsonify(users), 200

@bp.get("/profile")
@jwt_required()
def user_page() -> tuple[Response, int] | str:
    """
    Let's users retrieve their own user information when logged in

    Returns
    -------
    str
        A JSON object containing the user profile information
    """
    return user_schema.jsonify(current_user), 200


@bp.get("/<int:id>")
@jwt_required()
def get_user(id: int) -> tuple[Response, int] | Response:
    """
    Lets users retrieve a user profile by id
    Parameters
    ----------
    id : str
        The id of the user who's information should be retrieved

    Returns
    -------
    str
        A JSON object containing the user profile information
    """
    user = Users.query.filter_by(id=id).first()

    if user is None:
        return bad_request("User not found"), 404

    return user_schema.jsonify(user), 200


@bp.get("/role/<string:role>")
@jwt_required()
def get_users_by_role(role: str) -> tuple[Response, int]:
    """
    Returns all users in the database with a specific role

    Parameters
    ----------
    role : str
        The role of the users to be retrieved

    Returns
    -------
    JSON
        A JSON object containing all user data
    """
    users = Users.query.filter_by(role=role.lower()).all()
    
    if not users:
        return bad_request("No users found with that role"), 404

    return users_schema.jsonify(users), 200


@bp.put("/<int:id>")
@jwt_required()
def update_user(id: int) -> tuple[Response, int] | Response:
    """
    Lets users update their own user information

    Parameters
    ----------
    id : int
        The id of the user to be updated

    Returns
    -------
    str
        A JSON object containing the user profile information
    """
    user = Users.query.filter_by(id=id).first()

    if user is None:
        return bad_request("User not found"), 404

    try:
        result = user_schema.load(request.json, partial=True)
    except ValidationError as e:
        return bad_request(e.messages), 400

    for k, v in result.items():
        if k == "birthday":
            setattr(user, k, v.date())
        else:
            setattr(user, k, v)

    db.session.commit()

    return user_schema.dump(user), 200


@bp.delete("/<int:id>")
@jwt_required()
def delete_user(id: int) -> tuple[Response, int]:
    """
    Lets admins delete user information

    Parameters
    ----------
    id : int
        The id of the user to be deleted

    Returns
    -------
    str
        A JSON object containing the user profile information
    """
    try:
        user = Users.query.filter_by(id=id).first()
    except Exception as e:
        return bad_request(e.messages), 400

    if user is None:
        return bad_request("User not found"), 404

    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user), 200