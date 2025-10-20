from werkzeug.security import generate_password_hash
from config_real import get_db_connection  # This will be replaced with your actual config

def insert_admin():
    # Replace these with your actual admin credentials
    username = "admin_username"  # Replace with desired admin username
    email = "admin_email@example.com"  # Replace with admin email
    password = "admin_password"  # Replace with desired admin password

    password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO admin_users (username, email, password_hash) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, email, password_hash))
    conn.commit()
    conn.close()
    print("Default admin user created.")

if __name__ == "__main__":
    insert_admin()