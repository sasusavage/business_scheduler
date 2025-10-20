import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="nbaSavage123",
        password="nbaSavage123",
        database="business_scheduler",
        charset='utf8mb4'  # Use utf8mb4 for full Unicode support
    )

mail_settings = {
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 465,
    "MAIL_USE_SSL": True,
    "MAIL_USE_TLS": False,
    "MAIL_USERNAME": "sasuisaak332@gmail.com",
    "MAIL_PASSWORD": "mqvcuorzcfnuwevc",
    "MAIL_DEFAULT_SENDER": "sasuisaak332@gmail.com"
}
