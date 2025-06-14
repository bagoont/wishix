import emails

from app.core.config import settings


def send_email(
    email_to: str,
    subject: str,
    html_content: str,
) -> None:
    if not settings.email:
        msg = "No provided configuration for email variables."
        raise ValueError(msg)

    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.email.name, settings.email.email),
    )
    smtp_options = {"host": settings.email.host, "port": settings.email.port}
    if settings.email.tls:
        smtp_options["tls"] = True
    elif settings.email.ssl:
        smtp_options["ssl"] = True
    if settings.email.user:
        smtp_options["user"] = settings.email.user
    if settings.email.password:
        smtp_options["password"] = settings.email.password
    message.send(to=email_to, smtp=smtp_options)
