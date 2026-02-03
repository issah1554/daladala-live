from fastapi_mail import MessageSchema
from volta_api.core.mail import fastmail


async def send_welcome_email(to: str):
    message = MessageSchema(
        subject="Welcome",
        recipients=[to],
        body="Welcome to Daladala Live",
        subtype="plain",
    )
    await fastmail.send_message(message)

async def send_password_reset_email(to: str, reset_link: str):
    message = MessageSchema(
        subject="Password Reset",
        recipients=[to],
        body=f"Click the link to reset your password: {reset_link}",
        subtype="plain",
    )
    await fastmail.send_message(message)

# example usage:
# import asyncio
# asyncio.run(send_welcome_email("nzikustephen826@gmail.com"))
# asyncio.run(send_password_reset_email("nzikustephen826@gmail.com", "http://localhost:8000/reset-password"))