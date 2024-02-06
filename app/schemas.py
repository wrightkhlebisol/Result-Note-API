from app import ma
from app.models import Users, Tasks, Schools, Classes, Subjects, Scores
from enum import Enum

from marshmallow import Schema, fields

class UsersEnum(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    STUDENT = "student"
    TEACHER = "teacher"
    PARENT = "parent"
    OTHERS = "others"

    
class UsersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users

class UsersDeserializingSchema(Schema):
    username = fields.String()
    password = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    birthday = fields.Date()
    role = fields.Enum(UsersEnum)


class SchoolsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Schools


class SchoolsDeserializingSchema(Schema):
    name = fields.String()
    location = fields.String()
    color = fields.String()


class ClassesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Classes


class ClassesDeserializingSchema(Schema):
    name = fields.String()
    

class SubjectsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Subjects


class SubjectsDeserializingSchema(Schema):
    name = fields.String()


class ScoresSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Scores
        
class ScoresDeserializingSchema(Schema):
    score = fields.Integer()

class TasksSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tasks
