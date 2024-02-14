from app import db
from app.reports import bp
from app.errors.handlers import bad_request
from app.models import Reports
from app.schemas  import ReportsSchema
from flask import Response, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

report_schema = ReportsSchema()
reports_schema = ReportsSchema(many=True)

@bp.post('/')
@jwt_required()
def create_report() -> tuple[Response, int] :
    """
    Lets users submit a report
    
    Returns
    -------
    JSON
        A JSON object containing a success message
    """
    
    try:
        result = report_schema.load(request.json)
    except ValidationError as e:
        return bad_request(e.messages)
    
    report = Reports(
        url=result['url'],
        term=result['term'],
        session=result['session'],
        comment=result['comment']
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({'msg': 'Report created successfully'}), 201


@bp.get("/")
@jwt_required()
def get_reports() -> tuple[Response, int]:
    """
    Returns all reports submitted by the user making the request

    Returns
    -------
    JSON
        A JSON object containing all report data
    """
    reports = Reports.query.all()

    return reports_schema.jsonify(reports), 200


@bp.get("/<int:id>")
@jwt_required()
def get_report_by_id(id) -> tuple[Response, int]:
    """Returns report corresponding to a given id

    Args:
        id (int): The ID of the report

    Returns:
    -------
        JSON: The JSON formatted report if found or error object otherwise
    """
    report = Reports.query.filter_by(id=id).first()
    
    if not report:
        return bad_request("No report found"), 404
    
    return report_schema.jsonify(report)


@bp.put("/<int:id>")
@jwt_required()
def update_report(id):
    """
    Updates a report based on the ID in the URL
    
    Args:
        id (int): The ID of the report
        
    Returns:
    -------
        JSON: The JSON formatted report if found or error object otherwise
    """

    report = Reports.query.filter_by(id=id).first()
    
    if not report:
        return bad_request("Report not found"), 404
    
    try:
        result = report_schema.load(request.json, partial=True)
    except ValidationError as e:
        return bad_request(e.messages)
    
    for k, v in result.items():
        setattr(report, k, v)
        
    db.session.commit()
        
    return jsonify({"msg": "Report successfully updated"})


@bp.delete("/<int:id>")
@jwt_required()
def delete_report(id):
    """
    Deletes a report based on the ID in the URL
    
    Args:
        id (int): The ID of the report
        
    Returns:
    -------
        JSON: A JSON object containing the success message
    """
    report = Reports.query.filter_by(id=id).first()
    
    if not report:
        return bad_request("Report not found"), 404
        
    db.session.delete(report)
    db.session.commit()
    
    return jsonify({"msg": "Report deleted successfully"}), 200