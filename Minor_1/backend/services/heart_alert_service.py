from datetime import datetime
from email.message import EmailMessage
import smtplib
from threading import Lock, Timer
from uuid import uuid4

from backend import alert_settings
from backend.heart_alert_vars import PATIENT_NAME


_alerts = {}
_lock = Lock()


def _smtp_ready():
    return all(
        [
            alert_settings.SMTP_HOST,
            alert_settings.SMTP_PORT,
            alert_settings.SMTP_USERNAME,
            alert_settings.SMTP_PASSWORD,
            alert_settings.SMTP_FROM_EMAIL,
        ]
    )


def send_email(to_email, subject, body):
    if not to_email:
        return {"sent": False, "reason": "Recipient email is missing"}

    if not _smtp_ready():
        return {
            "sent": False,
            "reason": "SMTP is not configured. Set HEART_ALERT_SMTP_USERNAME and HEART_ALERT_SMTP_PASSWORD.",
        }

    message = EmailMessage()
    message["From"] = alert_settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(alert_settings.SMTP_HOST, alert_settings.SMTP_PORT, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(alert_settings.SMTP_USERNAME, alert_settings.SMTP_PASSWORD)
        smtp.send_message(message)

    return {"sent": True}


def get_default_config():
    return {
        "lowBpm": alert_settings.HEART_ALERT_LOW_BPM,
        "highBpm": alert_settings.HEART_ALERT_HIGH_BPM,
        "escalationMinutes": alert_settings.HEART_ALERT_ESCALATION_MINUTES,
        "selfEmail": alert_settings.DEFAULT_SELF_EMAIL,
        "emergencyEmail": alert_settings.DEFAULT_EMERGENCY_EMAIL,
        "smtpConfigured": _smtp_ready(),
    }


def classify_heart_rate(heart_rate, low_bpm, high_bpm):
    if heart_rate < low_bpm:
        return "low"
    if heart_rate > high_bpm:
        return "high"
    return "normal"


def _alert_body(alert, recipient_type):
    direction = "below" if alert["kind"] == "low" else "above"
    return (
        f"Heart-rate alert for {alert['patientName']}.\n\n"
        f"Current heart rate: {alert['heartRate']} BPM\n"
        f"Safe range: {alert['lowBpm']}-{alert['highBpm']} BPM\n"
        f"Status: {alert['kind'].upper()} heart rate, {direction} safe range\n"
        f"Detected at: {alert['createdAt']}\n\n"
        f"Recipient: {recipient_type}\n"
        "Please check on the user if this alert looks serious."
    )


def _escalate(alert_id):
    with _lock:
        alert = _alerts.get(alert_id)
        if not alert or alert["status"] != "pending":
            return
        alert["status"] = "escalated"
        alert["escalatedAt"] = datetime.now().isoformat(timespec="seconds")

    result = send_email(
        alert["emergencyEmail"],
        f"Emergency heart-rate alert: {alert['heartRate']} BPM",
        _alert_body(alert, "Emergency contact"),
    )

    with _lock:
        if alert_id in _alerts:
            _alerts[alert_id]["emergencyEmailResult"] = result


def create_heart_alert(payload):
    heart_rate = int(payload.get("heartRate"))
    low_bpm = alert_settings.HEART_ALERT_LOW_BPM
    high_bpm = alert_settings.HEART_ALERT_HIGH_BPM
    escalation_minutes = alert_settings.HEART_ALERT_ESCALATION_MINUTES
    escalation_minutes = min(max(escalation_minutes, 3), 5)
    patient_name = PATIENT_NAME
    self_email = alert_settings.DEFAULT_SELF_EMAIL.strip()
    emergency_email = alert_settings.DEFAULT_EMERGENCY_EMAIL.strip()

    kind = classify_heart_rate(heart_rate, low_bpm, high_bpm)
    if kind == "normal":
        return {
            "status": "normal",
            "message": "Heart rate is inside the selected safe range.",
            "heartRate": heart_rate,
        }

    alert_id = str(uuid4())
    alert = {
        "id": alert_id,
        "status": "pending",
        "kind": kind,
        "heartRate": heart_rate,
        "lowBpm": low_bpm,
        "highBpm": high_bpm,
        "patientName": patient_name,
        "selfEmail": self_email,
        "emergencyEmail": emergency_email,
        "escalationMinutes": escalation_minutes,
        "createdAt": datetime.now().isoformat(timespec="seconds"),
    }

    self_result = send_email(
        self_email,
        f"Heart-rate check needed: {heart_rate} BPM",
        _alert_body(alert, "User"),
    )
    alert["selfEmailResult"] = self_result

    timer = Timer(escalation_minutes * 60, _escalate, args=(alert_id,))
    timer.daemon = True
    alert["timer"] = timer

    with _lock:
        _alerts[alert_id] = alert

    timer.start()

    return _public_alert(alert)


def acknowledge_alert(alert_id):
    with _lock:
        alert = _alerts.get(alert_id)
        if not alert:
            return None

        if alert["status"] == "pending":
            alert["status"] = "acknowledged"
            alert["acknowledgedAt"] = datetime.now().isoformat(timespec="seconds")
            alert["timer"].cancel()

        return _public_alert(alert)


def get_alert_status(alert_id):
    with _lock:
        alert = _alerts.get(alert_id)
        return _public_alert(alert) if alert else None


def _public_alert(alert):
    return {
        key: value
        for key, value in alert.items()
        if key != "timer"
    }
