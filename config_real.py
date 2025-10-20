import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Replace with your MySQL host
        user="your_username",  # Replace with your MySQL username
        password="your_password",  # Replace with your MySQL password
        database="business_scheduler",  # Replace with your database name
        charset='utf8mb4'  # Use utf8mb4 for full Unicode support
    )

mail_settings = {
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USERNAME": "your_email@gmail.com",  # Replace with your Gmail address
    "MAIL_PASSWORD": "your_app_password",  # Replace with your Gmail app password
    "MAIL_DEFAULT_SENDER": "your_email@gmail.com"  # Replace with your Gmail address
}