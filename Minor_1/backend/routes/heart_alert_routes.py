from flask import Blueprint, request

from backend.services.heart_alert_service import (
    acknowledge_alert,
    create_heart_alert,
    get_alert_status,
    get_default_config,
)


heart_alert_bp = Blueprint("heart_alert", __name__)


@heart_alert_bp.route("/heart-alert/config")
def heart_alert_config():
    return get_default_config()


@heart_alert_bp.route("/heart-alert/check", methods=["POST"])
def heart_alert_check():
    payload = request.get_json(silent=True) or {}

    try:
        if payload.get("heartRate") is None:
            return {"error": "heartRate is required"}, 400
        return create_heart_alert(payload)
    except (TypeError, ValueError):
        return {"error": "Invalid heart-rate alert payload"}, 400


@heart_alert_bp.route("/heart-alert/acknowledge", methods=["POST"])
def heart_alert_acknowledge():
    payload = request.get_json(silent=True) or {}
    alert_id = payload.get("alertId")

    if not alert_id:
        return {"error": "alertId is required"}, 400

    alert = acknowledge_alert(alert_id)
    if not alert:
        return {"error": "Alert not found"}, 404

    return alert


@heart_alert_bp.route("/heart-alert/status/<alert_id>")
def heart_alert_status(alert_id):
    alert = get_alert_status(alert_id)
    if not alert:
        return {"error": "Alert not found"}, 404

    return alert

