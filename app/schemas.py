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
    
class TermEnum(Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    
class TypeEnum(Enum):
    CA = "CA"
    EXAM = "exam"
    TEST = "test"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    OTHERS = "others"

    
class UsersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users

class UsersDeserializingSchema(Schema):
    email = fields.Email()
    phone = fields.String()
    password = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    birthday = fields.Date()
    role = fields.Enum(UsersEnum)


class SchoolsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Schools


class SchoolsDeserializingSchema(Schema):
    name = fields.String()
    address = fields.String()
    phone = fields.String()
    email = fields.Email()
    logo = fields.String()
    motto = fields.String()
    city = fields.String()
    state = fields.String()
    country = fields.String()
    color = fields.String()


class ClassesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Classes


class ClassesDeserializingSchema(Schema):
    name = fields.String()
    description = fields.String()
    

class SubjectsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Subjects


class SubjectsDeserializingSchema(Schema):
    name = fields.String()
    description = fields.String()


class ScoresSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Scores
        
class ScoresDeserializingSchema(Schema):
    score = fields.Integer()
    term = fields.Enum(TermEnum)
    session = fields.String()
    type = fields.Enum(TypeEnum)
    

class TasksSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tasks
