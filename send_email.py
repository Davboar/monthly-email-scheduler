import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta, timezone
import pathlib

def env(name, default=None, required=False):
    val = os.getenv(name, default)
    if required and (val is None or str(val).strip() == ""):
        raise ValueError(f"Missing required environment variable: {name}")
    return val

def parse_bool(x, default=False):
    if x is None:
        return default
    return str(x).strip().lower() in {"1","true","yes","y","on"}

def list_from_env(name):
    raw = os.getenv(name, "")
    if not raw.strip():
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]

def should_send_today(now_utc):
    # Get config
    target_day = int(env("DAY_OF_MONTH", "23"))  # 1..31
    run_hour_utc = int(env("RUN_HOUR_UTC", "8")) # 0..23
    send_on_last_if_short = parse_bool(env("SEND_ON_LAST_IF_SHORT", "true"))

    # Only proceed at the chosen hour
    run_minute_utc = int(env("RUN_MINUTE_UTC", "0"))  # new var for minutes
    if now_utc.hour != run_hour_utc or now_utc.minute != run_minute_utc:
        print(f"Not the configured time (now={now_utc.hour:02d}:{now_utc.minute:02d}, target={run_hour_utc:02d}:{run_minute_utc:02d}).")
        return False
    
    # Determine "this month" last day
    # Move to first of next month, then step back one day.
    first_next_month = (now_utc.replace(day=1) + timedelta(days=32)).replace(day=1)
    last_day = (first_next_month - timedelta(days=1)).day

    # Effective day to trigger
    effective_day = target_day
    if target_day > last_day:
        if send_on_last_if_short:
            effective_day = last_day
        else:
            print(f"Target day {target_day} exceeds last day {last_day}, and SEND_ON_LAST_IF_SHORT=false. Skipping.")
            return False

    if now_utc.day == effective_day:
        return True

    print(f"Today is day {now_utc.day}, target is {effective_day}. Not sending.")
    return False

def build_message():
    from_name = env("FROM_NAME", "")
    from_email = env("FROM_EMAIL", required=True)
    to_emails = list_from_env("TO_EMAILS") or [env("TO_EMAIL", required=True)]
    cc_emails = list_from_env("CC_EMAILS")
    bcc_emails = list_from_env("BCC_EMAILS")

    subject = env("SUBJECT", "Monthly Update")
    body_text = env("BODY_TEXT", "")
    body_html = env("BODY_HTML", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_email)) if from_name else from_email
    msg["To"] = ", ".join(to_emails)
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)

    if body_text:
        msg.attach(MIMEText(body_text, "plain"))
    if body_html:
        msg.attach(MIMEText(body_html, "html"))
    if not body_text and not body_html:
        msg.attach(MIMEText("Hello,\n\nThis is an automated monthly email.\n", "plain"))

    # Attachments (comma-separated file paths in repo)
    attachments = list_from_env("ATTACHMENTS")
    for path in attachments:
        p = pathlib.Path(path)
        if not p.exists() or not p.is_file():
            print(f"Attachment not found or not a file: {path}. Skipping.")
            continue
        with open(p, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{p.name}"',
        )
        msg.attach(part)

    recipients = to_emails + cc_emails + bcc_emails
    return msg, recipients

def send():
    smtp_host = env("SMTP_HOST", "smtp.office365.com")
    smtp_port = int(env("SMTP_PORT", "587"))
    use_tls = parse_bool(env("SMTP_USE_TLS", "true"))
    from_email = env("FROM_EMAIL", required=True)
    app_password = env("APP_PASSWORD", required=True)

    msg, recipients = build_message()

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if use_tls:
            server.starttls(context=context)
        server.login(from_email, app_password)
        server.sendmail(from_email, recipients, msg.as_string())
    print(f"Sent to: {', '.join(recipients)}")

def main():
    dry_run = parse_bool(env("DRY_RUN", "false"))
    now_utc = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    print(f"Now (UTC): {now_utc.isoformat()}")

    if should_send_today(now_utc):
        if dry_run:
            print("DRY_RUN=true → would send now, but not actually sending.")
        else:
            send()

if __name__ == "__main__":
    main()
