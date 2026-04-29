import os, json
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), ".dev")
os.makedirs(LOG_DIR, exist_ok=True)
MAIL_LOG = os.path.join(LOG_DIR, "mail.log")

def send_email(to: str, subject: str, body: str):
    """Send an email. For now, logs to .dev/mail.log. Supports SendGrid if SENDGRID_API_KEY is set."""
    api_key = os.getenv("SENDGRID_API_KEY")
    if api_key:
        try:
            import httpx
            resp = httpx.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "personalizations": [{"to": [{"email": to}]}],
                    "from": {"email": os.getenv("FROM_EMAIL", "noreply@contentforge.local")},
                    "subject": subject,
                    "content": [{"type": "text/plain", "value": body}],
                },
            )
            resp.raise_for_status()
            return {"sent": True, "provider": "sendgrid"}
        except Exception as e:
            print("SendGrid failed:", e)
    # Fallback: log to file
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "to": to,
        "subject": subject,
        "body": body,
    }
    with open(MAIL_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return {"sent": True, "provider": "log", "log": MAIL_LOG}

def send_welcome_email(to: str, name: str):
    subject = "Welcome to ContentForge!"
    body = f"Hi {name or 'there'},\n\nWelcome to ContentForge. Start by creating your first brand and generating content.\n\nIf you have questions, hit reply.\n\n— The ContentForge Team"
    return send_email(to, subject, body)

def send_content_tip_email(to: str, name: str, tip: str):
    subject = "Your weekly Content Tip"
    body = f"Hi {name or 'there'},\n\nHere is your content tip for the week:\n\n{tip}\n\nKeep creating!\n— The ContentForge Team"
    return send_email(to, subject, body)
