from typing import Any
from flask import request, jsonify, Response

from app import db
from app.classes import bp
from app.models import Classes, Subjects
from app.schemas import ClassesSchema, ClassesDeserializingSchema
from app.errors.handlers import bad_request

from flask_jwt_extended import jwt_required, current_user

from marshmallow import ValidationError

import asyncio
from aiohttp import ClientSession

class_schema = ClassesSchema()
classes_schema = ClassesSchema(many=True)
class_deserializing_schema = ClassesDeserializingSchema()

@bp.post("/")
@jwt_required()
def create_class() -> tuple[Response, int] | Response:
    """
    Lets users create a class

    Returns
    -------
    str
        A JSON object containing a success message
    """
    try:
        result = class_schema.load(request.get_json())
    except ValidationError as e:
        return bad_request(e.messages)

    classes = Classes(
        name=result["name"],
        description = result["description"],
    )

    db.session.add(classes)
    db.session.commit()

    return jsonify({"msg": "Class created successfully"}), 201


@bp.get("/")
@jwt_required()
def get_all_classes() -> Response:
    """
    Endpoint for retrieving all classes

    Returns
    -------
    str
        A JSON object containing the classes
    """
    try:
        classes = Classes.query.all()
    except Exception as e:
        return bad_request(e.messages), 400
    
    if not classes:
        return bad_request("No classes found")
    
    return classes_schema.jsonify(classes)


@bp.get("/<int:id>")
@jwt_required()
def get_class_by_id(id: int) -> Response:
    """
    Endpoint for retrieving a class by ID

    Parameters
    ----------
    id : int
        ID of the class which needs
        to be retrieved 
    """
    try:
        result = Classes.query.filter_by(id=id).first()
    except Exception as e:
        return bad_request(e.messages), 400
    
    if not result:
        return bad_request("Class not found"), 404
    
    return class_schema.jsonify(result)


@bp.put("/<int:id>")
@jwt_required()
def update_class(id: int) -> tuple[Response, int] | Response:
    """
    Lets users update a class

    Parameters
    ----------
    id : int
        ID of the class which needs to be updated

    Returns
    -------
    str
        A JSON object containing a success message
    """
    try:
        result = class_schema.load(request.get_json())
    except ValidationError as e:
        return bad_request(e.messages), 400

    classes = Classes.query.get(id)

    if not classes:
        return bad_request("Class not found"), 404

    classes.name = result["name"]
    classes.description = result["description"]

    db.session.commit()

    return jsonify({"msg": "Class updated successfully"}), 201


@bp.delete("/<int:id>")
@jwt_required()
def delete_class(id: int) -> tuple[Response, int] | Response:
    """Delete a class by its id

    Parameters
    ----------
    id (int): 
        ID of the class to be deleted

    Returns:
    --------
    str
        Response: A JSON object containing a success message
    """
    try:
        result = Classes.query.get(id)
    except Exception as e:
        return bad_request(e.messages), 400
    
    if not result:
        return bad_request("Class not found"), 404
    
    db.session.delete(result)
    db.session.commit()
    
    return jsonify({"msg": "Class deleted successfully"}), 201


# @bp.get("/get/user/classes/post/<int:id>")
# @jwt_required()
# def get_classes_by_post_id(id: int) -> Response:
#     """
#     Endpoint for retrieving the user classes associated with a particular post

#     Parameters
#     ----------
#     id : int
#         ID of the post which class's need to be retrieved

#     Returns
#     -------
#     str
#         A JSON object containing the classes
#     """
#     classes = Classes.query.filter_by(post_id=id).all()
#     return classes_schema.jsonify(classes)


# @bp.post("/post/user/submit/class")
# @jwt_required()
# def submit_class() -> tuple[Response, int] | Response:
#     """
#     Lets users submit a class regarding a post

#     Returns
#     -------
#     str
#         A JSON object containing a success message
#     """
#     try:
#         result = class_deserializing_schema.load(request.get_json())
#     except ValidationError as e:
#         return bad_request(e.messages)

#     post = Posts.query.get(result["post_id"])

#     if not post:
#         return bad_request("Post not found")

#     if post.user_id != current_user.id:
#         return bad_request("Unauthorized")

#     classes = Classes(body=result["body"], post=post, user=current_user)

#     db.session.add(classes)
#     db.session.commit()

#     return jsonify({"msg": "Comment succesfully submitted"}), 201


# @bp.delete("/delete/user/class/<int:id>")
# @jwt_required()
# def delete_class(id: int) -> tuple[Response, int] | Response:
#     """
#     Lets users delete one of their own classes

#     Parameters
#     ----------
#     id : int
#         ID of the post which class's need to be retrieved

#     Returns
#     -------
#     str
#         A JSON object containing a success message
#     """
#     classes = Classes.query.get(id)

#     if not classes:
#         return bad_request("Comment not found")

#     if classes.user_id != current_user.id:
#         return bad_request("Unauthorized")

#     db.session.delete(classes)
#     db.session.commit()

#     return jsonify({"msg": "Comment succesfully deleted"}), 201


# @bp.get("/get/user/classes/async")
# @jwt_required()
# async def async_classes_api_call() -> dict[str, list[Any]]:
#     """
#     Calls two endpoints from an external API as async demo

#     Returns
#     -------
#     str
#         A JSON object containing the class
#     """
#     urls = [
#         "https://jsonplaceholder.typicode.com/classes",
#         "https://jsonplaceholder.typicode.com/classes",
#         "https://jsonplaceholder.typicode.com/classes",
#         "https://jsonplaceholder.typicode.com/classes",
#         "https://jsonplaceholder.typicode.com/classes",
#     ]

#     async with ClientSession() as session:
#         tasks = (session.get(url) for url in urls)
#         user_posts_res = await asyncio.gather(*tasks)
#         json_res = [await r.json() for r in user_posts_res]

#     response_data = {"classes": json_res}

#     return response_data
