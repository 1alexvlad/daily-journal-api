import os
import smtplib
from email.message import EmailMessage
from celery_worker import celery 



def create_reset_password_message(email_to: str, token: str) -> EmailMessage:
    email = EmailMessage()
    email['Subject'] = 'Восстановние аккаунта'
    email['From'] = os.getenv("SMTP_USER")
    email['To'] = email_to 

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8000")
    reset_link = f"{frontend_url}/reset-password?token={token}"

    html_content = f"""
    <p>Здравствуйте!</p>
    <p>Вы запросили сброс пароля. Для смены пароля перейдите по ссылке ниже:</p>
    <p><a href="{reset_link}">Сбросить пароль</a></p>
    <p>Ссылка действительна в течение 15 минут. Если вы не запрашивали сброс, просто проигнорируйте это письмо.</p>
    """
    email.set_content(html_content, subtype="html")
    return email


@celery.task(name="send_reset_password_email")
def send_reset_password_email(email_to: str, token: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    msg = create_reset_password_message(email_to, token)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()         
        server.starttls()   
        server.ehlo() 
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

