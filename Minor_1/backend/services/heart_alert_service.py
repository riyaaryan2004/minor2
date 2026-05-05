from datetime import datetime
from email.message import EmailMessage
import requests
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


def _sendgrid_ready():
    return all(
        [
            alert_settings.SENDGRID_API_URL,
            alert_settings.SENDGRID_API_KEY,
            alert_settings.SMTP_FROM_EMAIL,
        ]
    )


def _email_ready():
    if alert_settings.EMAIL_PROVIDER == "sendgrid":
        return _sendgrid_ready()

    return _smtp_ready()


def _send_sendgrid_email(to_email, subject, body):
    if not _sendgrid_ready():
        return {
            "sent": False,
            "reason": "SendGrid is not configured. Set HEART_ALERT_SENDGRID_API_KEY and HEART_ALERT_FROM_EMAIL.",
        }

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {
            "email": alert_settings.SMTP_FROM_EMAIL,
            "name": alert_settings.EMAIL_FROM_NAME,
        },
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }

    try:
        response = requests.post(
            alert_settings.SENDGRID_API_URL,
            headers={
                "Authorization": f"Bearer {alert_settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
    except requests.RequestException as exc:
        return {
            "sent": False,
            "reason": f"SendGrid API request failed: {exc}",
        }

    if response.status_code not in {200, 202}:
        return {
            "sent": False,
            "reason": f"SendGrid API failed with status {response.status_code}",
        }

    return {"sent": True, "provider": "sendgrid"}


def send_email(to_email, subject, body):
    if not to_email:
        return {"sent": False, "reason": "Recipient email is missing"}

    if alert_settings.EMAIL_PROVIDER == "sendgrid":
        return _send_sendgrid_email(to_email, subject, body)

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

    return {"sent": True, "provider": "smtp"}


def get_default_config():
    return {
        "lowBpm": alert_settings.HEART_ALERT_LOW_BPM,
        "highBpm": alert_settings.HEART_ALERT_HIGH_BPM,
        "escalationMinutes": alert_settings.HEART_ALERT_ESCALATION_MINUTES,
        "selfEmail": alert_settings.DEFAULT_SELF_EMAIL,
        "emergencyEmail": alert_settings.DEFAULT_EMERGENCY_EMAIL,
        "emailProvider": alert_settings.EMAIL_PROVIDER,
        "emailConfigured": _email_ready(),
        "smtpConfigured": _smtp_ready(),
    }


def classify_heart_rate(heart_rate, low_bpm, high_bpm):
    if heart_rate < low_bpm:
        return "low"
    if heart_rate > high_bpm:
        return "high"
    return "normal"


def _format_alert_time(timestamp):
    try:
        return datetime.fromisoformat(timestamp).strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return timestamp


def _alert_subject(alert):
    return f"Urgent: {alert['patientName']} may need help ({alert['heartRate']} BPM)"


def _alert_body(alert):
    direction = "below" if alert["kind"] == "low" else "above"
    detected_at = _format_alert_time(alert["createdAt"])
    escalated_at = _format_alert_time(alert.get("escalatedAt", ""))
    delay = alert["escalationMinutes"]

    return (
        f"FitIntel heart-rate safety alert\n\n"
        f"{alert['patientName']} had an abnormal heart-rate reading and did not confirm they were okay "
        f"within {delay} minute(s).\n\n"
        f"Current reading: {alert['heartRate']} BPM\n"
        f"Expected range: {alert['lowBpm']}-{alert['highBpm']} BPM\n"
        f"Alert type: {alert['kind'].upper()} heart rate ({direction} expected range)\n"
        f"Detected at: {detected_at}\n"
        f"Escalated at: {escalated_at}\n\n"
        "Suggested action:\n"
        "1. Try calling or messaging them now.\n"
        "2. If they do not respond and you believe there is immediate danger, contact local emergency services.\n\n"
        "This alert is generated automatically from heart-rate data and is not a medical diagnosis."
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
        _alert_subject(alert),
        _alert_body(alert),
    )

    with _lock:
        if alert_id in _alerts:
            _alerts[alert_id]["emergencyEmailResult"] = result


def create_heart_alert(payload):
    heart_rate = int(payload.get("heartRate"))
    low_bpm = alert_settings.HEART_ALERT_LOW_BPM
    high_bpm = alert_settings.HEART_ALERT_HIGH_BPM
    escalation_minutes = alert_settings.HEART_ALERT_ESCALATION_MINUTES
    escalation_minutes = max(escalation_minutes, 1)
    patient_name = PATIENT_NAME
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
        "emergencyEmail": emergency_email,
        "escalationMinutes": escalation_minutes,
        "createdAt": datetime.now().isoformat(timespec="seconds"),
    }

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
