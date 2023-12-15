import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = "MY_API_KEY"

def send_alert_email():
    message = Mail(
        from_email='yangwanlin1994@gmail.com',
        to_emails='wanliny2@outlook.com',
        subject='Alert: Monitor detects objects',
        html_content='<strong>Please check Drive folder for images</strong>',
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

if __name__ == "__main__":
    send_alert_email()

