import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from assets import Fetch

def send_absence_email(email, roll):
    # Email content
    subject = "Attendance Notification"
    body = (
        f"Dear Student ({roll}),\n\n"
        f"This is to inform you that you have been marked absent for the course 'CS1' on {date.today()}.\n\n"
        "If you believe this is an error, please contact your instructor immediately.\n\n"
        "Best regards,\n"
        "Attendance Management System"
    )

    # Email configuration
    sender_email = "akis.pwdchecker@gmail.com"
    sender_password = "tjjqhaifdobuluhg"

    # Setting up the MIME
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connecting to the server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


f = Fetch()
x = f.fetch_daily_absentees_with_mail(str(date.today()), "cs1")
print(x)
for i,j in x.items():
    send_absence_email(j,i)


