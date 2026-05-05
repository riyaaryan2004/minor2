import os

from backend.heart_alert_vars import (
    EMAIL_FROM_NAME,
    EMAIL_PROVIDER,
    EMERGENCY_EMAIL,
    ESCALATION_MINUTES,
    HIGH_BPM,
    LOW_BPM,
    FROM_EMAIL,
    SENDGRID_API_KEY,
    SENDGRID_API_URL,
    SELF_EMAIL,
)


def _load_local_env():
    env_paths = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
    ]

    for env_path in env_paths:
        if not os.path.exists(env_path):
            continue

        with open(env_path, "r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_local_env()

HEART_ALERT_LOW_BPM = int(os.getenv("HEART_ALERT_LOW_BPM", str(LOW_BPM)))
HEART_ALERT_HIGH_BPM = int(os.getenv("HEART_ALERT_HIGH_BPM", str(HIGH_BPM)))
HEART_ALERT_ESCALATION_MINUTES = int(os.getenv("HEART_ALERT_ESCALATION_MINUTES", str(ESCALATION_MINUTES)))

SMTP_HOST = os.getenv("HEART_ALERT_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("HEART_ALERT_SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("HEART_ALERT_SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("HEART_ALERT_SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("HEART_ALERT_FROM_EMAIL", FROM_EMAIL or SMTP_USERNAME)

DEFAULT_SELF_EMAIL = os.getenv("HEART_ALERT_SELF_EMAIL", SELF_EMAIL)
DEFAULT_EMERGENCY_EMAIL = os.getenv("HEART_ALERT_EMERGENCY_EMAIL", EMERGENCY_EMAIL)

EMAIL_PROVIDER = os.getenv("HEART_ALERT_EMAIL_PROVIDER", EMAIL_PROVIDER).lower()
EMAIL_FROM_NAME = os.getenv("HEART_ALERT_FROM_NAME", EMAIL_FROM_NAME)
SENDGRID_API_URL = os.getenv("HEART_ALERT_SENDGRID_API_URL", SENDGRID_API_URL)
SENDGRID_API_KEY = os.getenv("HEART_ALERT_SENDGRID_API_KEY", SENDGRID_API_KEY)
