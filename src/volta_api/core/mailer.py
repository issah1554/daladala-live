# volta_api/core/mailer.py
from fastapi_mail import MessageSchema, MessageType
from volta_api.core.mail import fastmail


async def send_welcome_email(to_email: str):
    message = MessageSchema(
        subject="Welcome to Daladala Live",
        recipients=[to_email],
        body="Your account was created successfully.",
        subtype=MessageType.plain,
    )

    await fastmail.send_message(message)
