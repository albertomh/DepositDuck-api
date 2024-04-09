"""
(c) 2024 Alberto Morón Hernández
"""

import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import (
    SMTP,
    SMTP_SSL,
    SMTPDataError,
    SMTPHeloError,
    SMTPNotSupportedError,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
)

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel

from depositduck import BASE_DIR
from depositduck.dependables import get_logger, get_settings

LOG = get_logger()
settings = get_settings()


class HtmlEmail(BaseModel):
    title: str
    preheader: str


async def render_html_email(template_name: str, context: HtmlEmail) -> str:
    templates_dir_path = BASE_DIR / "email" / "templates"

    env = Environment(
        loader=FileSystemLoader(templates_dir_path),
        autoescape=select_autoescape(["html", "jinja2"]),
    )

    template = env.get_template(template_name)
    rendered_html = template.render(context.model_dump())

    return rendered_html


async def send_email(
    recipient: str, subject: str, html_body: str, plain_body: str | None = None
) -> None:
    sender_email = settings.smtp_sender_address
    smtp_password = settings.smtp_password
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    html_part = MIMEText(html_body, "html")
    # email clients render last part first, so html must be last
    if plain_body:
        text_part = MIMEText(plain_body, "plain")
        message.attach(text_part)
    message.attach(html_part)

    if settings.debug:
        smtp_cm = SMTP(
            settings.smtp_server,
            settings.smtp_port,
        )
    else:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        smtp_cm = SMTP_SSL(settings.smtp_server, settings.smtp_port, context=ssl_context)
    with smtp_cm as server:
        try:
            if not settings.debug:
                server.starttls()
                server.login(sender_email, smtp_password)
            server.sendmail(sender_email, recipient, message.as_string())
        except (
            SMTPHeloError,
            SMTPRecipientsRefused,
            SMTPSenderRefused,
            SMTPDataError,
            SMTPNotSupportedError,
        ) as e:
            LOG.error(f"TODO: {e}")
        finally:
            server.quit()
