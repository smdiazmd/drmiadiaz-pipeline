# shared/email_utils.py
"""
Shared email sending utilities for the content pipeline.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from shared.config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD


def send_email(
    to: str | list,
    subject: str,
    html_body: str,
    plain_body: str = "",
    attachments: list = None,
    cc: str = None
):
    """
    Send an HTML email with optional attachments.
    
    to: single email or list of emails
    attachments: list of dicts with keys: filename, data (bytes), mimetype
    """
    if isinstance(to, str):
        to = [to]

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = ", ".join(to)
    if cc:
        msg["Cc"] = cc

    alt = MIMEMultipart("alternative")
    if plain_body:
        alt.attach(MIMEText(plain_body, "plain"))
    alt.attach(MIMEText(html_body, "html"))
    msg.attach(alt)

    if attachments:
        for att in attachments:
            part = MIMEBase(*att["mimetype"].split("/"))
            part.set_payload(att["data"])
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=att["filename"])
            msg.attach(part)

    all_recipients = to + ([cc] if cc else [])

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, all_recipients, msg.as_string())

    print(f"✓ Email sent: {subject} → {', '.join(to)}")


def email_header(title: str, subtitle: str, badge_text: str, badge_color: str = "#1a1a1a") -> str:
    """Reusable HTML email header."""
    return f"""
    <div style="border-bottom:2px solid #1a1a1a;padding-bottom:14px;margin-bottom:28px;">
        <div style="display:inline-block;font-size:10px;letter-spacing:0.14em;
                    text-transform:uppercase;background:{badge_color};color:white;
                    padding:3px 10px;border-radius:2px;font-family:sans-serif;margin-bottom:8px;">
            {badge_text}
        </div>
        <div style="font-size:20px;font-weight:bold;margin:4px 0 2px;font-family:Georgia,serif;">{title}</div>
        <div style="font-size:13px;color:#888;font-family:sans-serif;">{subtitle}</div>
    </div>
    """


def email_section(title: str, body: str, border_color: str = "#1a1a1a", bg: str = "#f8f8f8") -> str:
    """Reusable HTML email content section."""
    return f"""
    <div style="margin-bottom:28px;">
        <div style="font-size:10px;letter-spacing:0.14em;text-transform:uppercase;
                    color:{border_color};font-family:sans-serif;margin-bottom:8px;font-weight:600;">
            {title}
        </div>
        <div style="background:{bg};border-left:3px solid {border_color};padding:18px 22px;
                    white-space:pre-wrap;font-size:15px;line-height:1.85;font-family:Georgia,serif;">
{body}
        </div>
    </div>
    """


def email_table(headers: list, rows: list) -> str:
    """Reusable HTML table for schedules."""
    header_html = "".join(f'<th style="text-align:left;padding:8px 12px;background:#1a1a1a;color:white;font-family:sans-serif;font-size:12px;">{h}</th>' for h in headers)
    rows_html = ""
    for i, row in enumerate(rows):
        bg = "#f8f8f8" if i % 2 == 0 else "#ffffff"
        cells = "".join(f'<td style="padding:8px 12px;font-family:sans-serif;font-size:13px;border-bottom:1px solid #eee;">{c}</td>' for c in row)
        rows_html += f'<tr style="background:{bg};">{cells}</tr>'
    return f"""
    <table style="width:100%;border-collapse:collapse;margin-bottom:28px;">
        <thead><tr>{header_html}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """


def email_wrapper(content: str) -> str:
    """Wraps content in consistent email shell."""
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Georgia,serif;max-width:680px;margin:40px auto;
             color:#1a1a1a;line-height:1.7;padding:0 24px;background:#ffffff;">
    {content}
    <div style="font-size:11px;color:#aaa;margin-top:40px;border-top:1px solid #eee;
                padding-top:16px;font-family:sans-serif;">
        Dr. Mia Diaz Content Pipeline · @drmiadiaz · Welmivia Medical
    </div>
</body>
</html>"""
