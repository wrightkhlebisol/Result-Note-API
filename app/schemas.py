from app import ma
from app.models import Users, Tasks, Schools, Classes, Subjects, Scores, Reports
from enum import Enum

from marshmallow import Schema, fields

class UsersEnum(Enum):
    super_admin = "super_admin"
    admin = "admin"
    student = "student"
    teacher = "teacher"
    parent = "parent"
    others = "others"
    
class TermEnum(Enum):
    first = "first"
    second = "second"
    third = "third"
    
class TypeEnum(Enum):
    CA = "CA"
    exam = "exam"
    test = "test"
    assignment = "assignment"
    project = "project"
    others = "others"

    
class UsersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users

class UsersDeserializingSchema(Schema):
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    phone = fields.String()
    password = fields.String()
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
    
class ReportsSchema(ma.SQLAlchemyAutoSchema):
    class Meta(Schema):
        model = Reports

class TasksSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tasks
