PATIENT_NAME = "FitIntel user"

# Put the real self and emergency contact emails here, or override them with
# environment variables named in alert_settings.py.
SELF_EMAIL = "riya.chhavi.gaurangi@gmail.com"
EMERGENCY_EMAIL = "riyaaryan1001@gmail.com"

LOW_BPM = 50
HIGH_BPM = 120
ESCALATION_MINUTES = 1

EMAIL_PROVIDER = "sendgrid"
EMAIL_FROM_NAME = "FitIntel Heart Alerts"
FROM_EMAIL = "riya.chhavi.gaurangi@gmail.com"

# SendGrid email API settings. Keep the real key out of git by setting
# HEART_ALERT_SENDGRID_API_KEY in a local .env or your shell.
SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"
SENDGRID_API_KEY = ""
