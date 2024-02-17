from app import db, jwt
from flask import current_app
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import redis
import rq

@jwt.user_lookup_loader
def user_loader_callback(jwt_header: dict, jwt_data: dict) -> object:
    """
    HUser loader function which uses the JWT identity to retrieve a user object.
    Method is called on protected routes

    Parameters
    ----------
    jwt_header : dictionary
        header data of the JWT
    jwt_data : dictionary
        payload data of the JWT

    Returns
    -------
    object
        Returns a users object containing the user information
    """
    return Users.query.filter_by(id=jwt_data["sub"]).first()


student_reports = db.Table(
    "student_reports",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("report_id", db.Integer, db.ForeignKey("reports.id")),
)

users_subjects = db.Table(
    "users_subjects",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("subject_id", db.Integer, db.ForeignKey("subjects.id"), primary_key=True),
)

school_students = db.Table(
    "school_students",
    db.Column("student_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("school_id", db.Integer, db.ForeignKey("schools.id"), primary_key=True),
)

school_teachers = db.Table(
    "school_teachers",
    db.Column("teacher_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("school_id", db.Integer, db.ForeignKey("schools.id"), primary_key=True)
)

schools_subjects = db.Table(
    "schools_subjects",
    db.Column("school_id", db.Integer, db.ForeignKey("schools.id"), primary_key=True),
    db.Column("subject_id", db.Integer, db.ForeignKey("subjects.id"), primary_key=True)
)

school_classes = db.Table(
    "school_classes",
    db.Column("school_id", db.Integer, db.ForeignKey("schools.id"), primary_key=True),
    db.Column("class_id", db.Integer, db.ForeignKey("classes.id"), primary_key=True)
)

class_subjects = db.Table(
    "class_subjects",
    db.Column("subject_id", db.Integer, db.ForeignKey("subjects.id"), primary_key=True),
    db.Column("class_id", db.Integer, db.ForeignKey("classes.id"), primary_key=True)
)

students_classes = db.Table(
    "students_classes",
    db.Column("student_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("class_id", db.Integer, db.ForeignKey("classes.id"), primary_key=True)
)


# defines the Users database table
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=False, nullable=False)
    role = db.Column(db.Enum('super_admin', 'admin', 'student', 'teacher', 'parent', 'others'), nullable=False, default="others")
    birthday = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    schools = relationship("Schools", back_populates="owner", lazy=True, cascade="all, delete")
    reports = relationship("Reports", back_populates="students", secondary=student_reports, cascade="all, delete")
    subjects = relationship("Subjects", back_populates="students", secondary=users_subjects, cascade="all, delete")
    scores = relationship("Scores", back_populates="students", lazy=True)
    school = relationship("Schools", back_populates="students", secondary=school_students, lazy=True, cascade="all, delete")
    school_teachers = relationship("Schools", back_populates="teachers", secondary=school_teachers, lazy=True, cascade="all, delete")
    classes = relationship("Classes", back_populates="students", secondary=students_classes, lazy=True, cascade="all, delete")


    def set_password(self, password: str):
        """
        Helper function to generate the password hash of a user

        Parameters
        ----------
        password : str
            The password provided by the user when registering
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Helper function to verify the password hash agains the password provided
        by the user when logging in

        Parameters
        ----------
        password : str
            The password provided by the user when logging in

        Returns
        -------
        bool
            Returns True if the password is a match. If not False is returned
        """
        return check_password_hash(self.password_hash, password)
    
    def launch_task(self, name: str, description: str, **kwargs) -> object:
        """
        Helper function to launch a background task

        Parameters
        ----------
        name : str
            Name of the task to launch
        description : str
            Description of the task to launch

        Returns
        -------
        object
            A Tasks object containing the task information
        """
        rq_job = current_app.task_queue.enqueue(
            "app.tasks.long_running_jobs" + name, **kwargs
        )
        task = Tasks(
            task_id=rq_job.get_id(), 
            name=name, 
            description=description, 
            user=self
        )
        db.session.add(task)

        return task

    def get_tasks_in_progress(self) -> list:
        """
        Helper function which retrieves the background tasks that are still in progress

        Returns
        -------
        list
            A list of Tasks objects
        """
        return Tasks.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name: str) -> object:
        """
        Helper function to retrieve a task in progress based on name

        Parameters
        ----------
        name : str
            name of the task to be retrieved

        Returns
        -------
        object
            A task object
        """
        return Tasks.query.filter_by(name=name, user=self, complete=False).first()

    def get_completed_tasks(self) -> dict:
        """
        Helper function to retrieve all completed tasks

        Returns
        -------
        dict
            A dictionary of Tasks objects
        """
        return Tasks.query.filter_by(user=self, complete=True).all()


# defines the Schools database table
class Schools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    color = db.Column(db.String(100), default="blue")
    logo = db.Column(db.String(100), nullable=True, default="default.png")
    motto = db.Column(db.String(100), nullable=True, default="Education for all")
    city = db.Column(db.String(100), nullable=False, default="Lagos")
    state = db.Column(db.String(100), nullable=False, default="Lagos")
    country = db.Column(db.String(100), default="Nigeria")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = relationship("Users", back_populates="schools", lazy=True, cascade="all, delete")

    students = relationship("Users", back_populates="school", secondary=school_students, lazy=True, cascade="all, delete")
    teachers = relationship("Users", back_populates="school_teachers", secondary=school_teachers, lazy=True, cascade="all, delete")
    subjects = relationship("Subjects", back_populates="schools", secondary=schools_subjects, lazy=True, cascade="all, delete")
    classes = relationship("Classes", back_populates="schools", secondary=school_classes, lazy=True, cascade="all, delete")

    
# defines the Students database table
class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    subjects = relationship("Subjects", back_populates="classes", secondary=class_subjects, lazy=True, cascade="all, delete")
    scores = relationship("Scores", back_populates="classes", lazy=True)
    schools = relationship("Schools", back_populates="classes", lazy=True, secondary=school_classes, cascade="all, delete")
    students = relationship("Users", back_populates="classes", secondary=students_classes, lazy=True, cascade="all, delete")
    

# defines the Subjects database table
class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
    classes = relationship("Classes", back_populates="subjects", secondary=class_subjects, lazy=True, cascade="all, delete")
    students = relationship("Users", back_populates="subjects", lazy=True, cascade="all, delete", secondary=users_subjects)
    scores = relationship("Scores", back_populates="subjects", lazy=True)
    schools = relationship("Schools", back_populates="subjects", lazy=True, secondary=schools_subjects, cascade="all, delete")
    

# defines the Scores database table
class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    term = db.Column(db.Enum('first', 'second', 'third'), nullable=False)
    session = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum('CA', 'exam', 'test', 'assignment', 'project', 'others'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    
    classes = relationship("Classes", back_populates="scores", lazy=True)
    subjects = relationship("Subjects", back_populates="scores", lazy=True)
    students = relationship("Users", back_populates="scores", lazy=True)
    
    
class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(150), nullable=False)
    term = db.Column(db.Enum('first', 'second', 'third'), nullable=False)
    session = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    generator_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    students = relationship("Users", back_populates="reports", lazy=True, secondary=student_reports, cascade="all, delete")
    # generator = relationship("Users", lazy=True, cascade="all, delete")
    

class RevokedTokenModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))
    date_revoked = db.Column(db.DateTime, default=datetime.utcnow)

    def add(self):
        """
        Helper function to add a JWT to the table
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti: str) -> bool:
        """
        Helper function to check if a JWT is in the Revoked Token table

        Parameters
        ----------
        jti : str
            The JWT unique identifier

        Returns
        -------
        bool
            Return True if the JWT is in the Revoked Token table
        """
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), index=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.task_id, connection=current_app.redis)

        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None

        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100
