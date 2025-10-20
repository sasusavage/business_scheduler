from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from config import get_db_connection, mail_settings
import smtplib
from datetime import datetime
import random
import string

app = Flask(__name__)
app.secret_key = "your_secret_key"
bcrypt = Bcrypt(app)

# Configure Flask-Mail
app.config.update(mail_settings)
app.config['MAIL_DEBUG'] = True  # Enable debug logging for email
mail = Mail(app)

# Replace this with a valid email address
admin_email = "sasuisaak332@gmail.com"

# Add a global variable for max appointments per time slot (default 3)
MAX_APPOINTMENTS_PER_SLOT = 3

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Add Appointment
@app.route('/add', methods=['POST'])
def add_appointment():
    customer_name = request.form['customer_name']
    email = request.form['email']
    contact_number = request.form['contact_number']
    service = request.form['service']
    date_time = request.form['date'] + " " + request.form['time']

    # Check if the selected date is a Sunday
    selected_date = datetime.strptime(request.form['date'], "%Y-%m-%d")
    if selected_date.weekday() == 6:  # Sunday
        flash("Bookings are not allowed on Sundays.")
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the selected date is a holiday
    query = "SELECT * FROM holidays WHERE holiday_date = DATE(%s)"
    cursor.execute(query, (date_time,))
    holiday = cursor.fetchone()
    if holiday:
        flash("Bookings are not allowed on holidays. Please choose another date.")
        return redirect(url_for('index'))

    # Check if the time slot is full
    query = "SELECT COUNT(*) FROM appointments WHERE date_time = %s"
    cursor.execute(query, (date_time,))
    count = cursor.fetchone()[0]
    if count >= 3:
        flash("The selected time slot is full. Please choose another time.")
        return redirect(url_for('index'))

    # Insert the appointment
    query = "INSERT INTO appointments (customer_name, email, contact_number, service, date_time) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (customer_name, email, contact_number, service, date_time))
    conn.commit()
    conn.close()

    send_email(email, "Appointment Confirmation", f"Dear {customer_name}, your appointment for {service} on {date_time} has been confirmed.")
    send_email(admin_email, "New Appointment", f"New appointment booked by {customer_name} for {service} on {date_time}.")

    flash("Appointment booked successfully.")
    return redirect(url_for('index'))

@app.route('/reschedule1/<int:id>', methods=['POST', 'GET'])
def reschedule_appointment1(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_date = request.form['date']
        new_time = request.form['time']
        new_date_time = f"{new_date} {new_time}"

        # Check if the time slot is already booked
        query = "SELECT * FROM appointments WHERE date_time = %s AND id != %s"
        cursor.execute(query, (new_date_time, id))
        existing_appointment = cursor.fetchone()

        if existing_appointment:
            flash("The selected time slot is already booked. Please choose a different time.")
            return redirect(url_for('reschedule_appointment1', id=id))

        # Update the appointment
        query = "UPDATE appointments SET date_time = %s WHERE id = %s"
        cursor.execute(query, (new_date_time, id))
        conn.commit()

        # Fetch updated appointment details
        query = "SELECT customer_name, email, service FROM appointments WHERE id = %s"
        cursor.execute(query, (id,))
        appointment = cursor.fetchone()
        conn.close()

        # Send email notifications
        customer_name, email, service = appointment
        send_email(email, "Appointment Rescheduled", f"Dear {customer_name}, your appointment for {service} has been rescheduled to {new_date} at {new_time}.")
        send_email(admin_email, "Appointment Rescheduled", f"The appointment for {customer_name} has been rescheduled to {new_date} at {new_time}.")

        flash("Appointment rescheduled successfully.")
        return redirect(url_for('admin_dashboard'))

    # Fetch current appointment details for the form
    query = "SELECT DATE(date_time), TIME(date_time) FROM appointments WHERE id = %s"
    cursor.execute(query, (id,))
    appointment = cursor.fetchone()
    conn.close()

    # Pass the appointment details to the template
    return render_template('reschedule.html', id=id, appointment=appointment)

@app.route('/reschedule/<int:id>', methods=['POST', 'GET'])
def reschedule_appointment(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_date = request.form['date']
        new_time = request.form['time']

        # Check if the time slot is already booked
        query = "SELECT * FROM appointments WHERE date_time = %s AND id != %s"
        cursor.execute(query, (f"{new_date} {new_time}", id))
        existing_appointment = cursor.fetchone()

        if existing_appointment:
            flash("The selected time slot is already booked. Please choose a different time.")
            return redirect(url_for('reschedule_appointment', id=id))

        # Update the appointment
        query = "UPDATE appointments SET date_time = %s WHERE id = %s"
        cursor.execute(query, (f"{new_date} {new_time}", id))
        conn.commit()

        # Fetch updated appointment details
        query = "SELECT customer_name, email, service FROM appointments WHERE id = %s"
        cursor.execute(query, (id,))
        appointment = cursor.fetchone()
        conn.close()

        # Send email notifications
        customer_name, email, service = appointment
        send_email(email, "Appointment Rescheduled", f"Dear {customer_name}, your appointment for {service} has been rescheduled to {new_date} at {new_time}.")
        send_email(admin_email, "Appointment Rescheduled", f"The appointment for {customer_name} has been rescheduled to {new_date} at {new_time}.")

        flash("Appointment rescheduled successfully.")
        return redirect(url_for('user_dashboard'))

    # Fetch current appointment details for the form
    query = "SELECT DATE(date_time), TIME(date_time) FROM appointments WHERE id = %s"
    cursor.execute(query, (id,))
    appointment = cursor.fetchone()
    conn.close()

    return render_template('reschedule.html', id=id, appointment=appointment)

@app.route('/cancel/<int:id>')
def cancel_appointment(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch appointment details before deleting
    query = "SELECT customer_name, email, service, date_time FROM appointments WHERE id = %s"
    cursor.execute(query, (id,))
    appointment = cursor.fetchone()

    if not appointment:
        flash("Appointment not found.")
        return redirect(url_for('user_dashboard'))

    customer_name, email, service, date_time = appointment

    # Delete the appointment
    query = "DELETE FROM appointments WHERE id = %s"
    cursor.execute(query, (id,))
    conn.commit()
    conn.close()

    # Send email notifications
    send_email(email, "Appointment Canceled", f"Dear {customer_name}, your appointment for {service} on {date_time} has been canceled.")
    send_email(admin_email, "Appointment Canceled", f"The appointment for {customer_name} on {date_time} has been canceled.")

    flash("Appointment canceled successfully.")
    return redirect(url_for('user_dashboard'))

@app.route('/add_appointment_admin', methods=['POST'])
def add_appointment_admin():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    customer_name = request.form['customer_name']
    email = request.form['email']
    contact_number = request.form['contact_number']
    service = request.form['service']
    date = request.form['date']
    time = request.form['time']
    date_time = f"{date} {time}"  # Combine date and time into a single datetime value

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO appointments (customer_name, email, contact_number, service, date_time) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (customer_name, email, contact_number, service, date_time))
    conn.commit()
    conn.close()

    # Send email notifications
    send_email(email, "Appointment Confirmation", f"Dear {customer_name}, your appointment for {service} on {date_time} has been confirmed.")
    send_email(admin_email, "New Appointment Added", f"New appointment added by admin for {customer_name} for {service} on {date_time}.")

    flash("Appointment added successfully.")
    return redirect(url_for('admin_dashboard'))

@app.route('/mark_completed/<int:id>', methods=['POST'])
def mark_completed(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the appointment details
    query = "SELECT customer_name, email, contact_number, service, date_time FROM appointments WHERE id = %s"
    cursor.execute(query, (id,))
    appointment = cursor.fetchone()

    if not appointment:
        flash("Appointment not found.")
        return redirect(url_for('admin_dashboard'))

    customer_name, email, contact_number, service, date_time = appointment

    # Move the appointment to the completed_appointments table
    query = """
        INSERT INTO completed_appointments (customer_name, email, contact_number, service, date_time)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (customer_name, email, contact_number, service, date_time))

    # Delete the appointment from the appointments table
    query = "DELETE FROM appointments WHERE id = %s"
    cursor.execute(query, (id,))
    conn.commit()
    conn.close()

    # Send email notifications
    send_email(email, "Appointment Completed", f"Dear {customer_name}, your appointment for {service} on {date_time} has been marked as completed.")
    send_email(admin_email, "Appointment Completed", f"The appointment for {customer_name} on {date_time} has been marked as completed.")

    flash("Appointment marked as completed.")
    return redirect(url_for('admin_dashboard'))

@app.route('/set_holiday', methods=['POST'])
def set_holiday():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    holiday_date = request.form['holiday_date']

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT IGNORE INTO holidays (holiday_date) VALUES (%s)"
    cursor.execute(query, (holiday_date,))
    conn.commit()
    conn.close()

    flash("Holiday set successfully.")
    return redirect(url_for('admin_dashboard'))

# Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        identifier = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admin_users WHERE username = %s OR email = %s",
            (identifier, identifier)
        )
        admin = cursor.fetchone()
        conn.close()

        if admin:
            # admin_users table columns: id, username, email, password_hash
            # admin[0] = id, admin[1] = username, admin[2] = email, admin[3] = password_hash
            password_hash = admin[3]
            
            if check_password_hash(password_hash, password):
                session['admin'] = admin[1]
                return redirect(url_for('admin_dashboard'))
        
        flash("Invalid credentials. Please try again.")
    return render_template('admin_login.html')

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch pending appointments
    query = "SELECT id, customer_name, email, service, date_time, FALSE AS completed FROM appointments ORDER BY date_time"
    cursor.execute(query)
    appointments = cursor.fetchall()

    # Fetch completed appointments
    query = "SELECT id, customer_name, email, service, date_time, completed_at FROM completed_appointments ORDER BY completed_at DESC"
    cursor.execute(query)
    completed_appointments = cursor.fetchall()

    # Fetch max appointments per slot (from DB or config table)
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (setting_key VARCHAR(50) PRIMARY KEY, setting_value VARCHAR(50))")
    cursor.execute("SELECT setting_value FROM settings WHERE setting_key = 'max_appointments_per_slot'")
    max_slot = cursor.fetchone()
    max_appointments = int(max_slot[0]) if max_slot else MAX_APPOINTMENTS_PER_SLOT

    # Calculate analytics for available slots (today and next 7 days)
    from datetime import timedelta, date as dt_date
    today = dt_date.today()
    slot_analytics = []
    summary_cards = []
    alerts = []
    for i in range(8):
        day = today + timedelta(days=i)
        # Check if holiday
        cursor.execute("SELECT * FROM holidays WHERE holiday_date = %s", (day,))
        is_holiday = bool(cursor.fetchone())
        slots = []
        booked = 0
        for slot in ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]:
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE date_time = %s", (f"{day} {slot}",))
            count = cursor.fetchone()[0]
            slots.append({'time': slot, 'count': count, 'available': count < max_appointments})
            booked += count
        total_slots = 8 * max_appointments
        available = total_slots - booked if not is_holiday else 0
        slot_analytics.append({'date': day.strftime('%Y-%m-%d'), 'is_holiday': is_holiday, 'slots': slots})
        summary_cards.append({
            'date': day.strftime('%Y-%m-%d'),
            'is_holiday': is_holiday,
            'total_slots': total_slots,
            'booked': booked,
            'available': available
        })
        if is_holiday:
            alerts.append(f"{day.strftime('%Y-%m-%d')}: Holiday")
        elif booked == total_slots:
            alerts.append(f"{day.strftime('%Y-%m-%d')}: Fully booked")
        elif booked <= max_appointments:
            alerts.append(f"{day.strftime('%Y-%m-%d')}: Low bookings")

    # Booking trends (last 14 days)
    trends_labels = []
    trends_data = []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE DATE(date_time) = %s", (day,))
        count = cursor.fetchone()[0]
        trends_labels.append(day.strftime('%Y-%m-%d'))
        trends_data.append(count)

    # Service popularity (last 30 days)
    cursor.execute("SELECT service, COUNT(*) as cnt FROM appointments WHERE date_time >= %s GROUP BY service ORDER BY cnt DESC", (today - timedelta(days=30),))
    service_popularity = cursor.fetchall()
    service_labels = [row[0] for row in service_popularity]
    service_counts = [row[1] for row in service_popularity]

    # User activity (last 30 days, top 5 users)
    cursor.execute("SELECT customer_name, COUNT(*) as cnt FROM appointments WHERE date_time >= %s GROUP BY customer_name ORDER BY cnt DESC LIMIT 5", (today - timedelta(days=30),))
    user_activity_rows = cursor.fetchall()
    user_activity_labels = [row[0] for row in user_activity_rows]
    user_activity_counts = [row[1] for row in user_activity_rows]

    # Total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Bookings today, this week, this month
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE DATE(date_time) = %s", (today,))
    today_bookings = cursor.fetchone()[0]
    week_start = today - timedelta(days=today.weekday())
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE DATE(date_time) >= %s AND DATE(date_time) <= %s", (week_start, today))
    week_bookings = cursor.fetchone()[0]
    month_start = today.replace(day=1)
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE DATE(date_time) >= %s AND DATE(date_time) <= %s", (month_start, today))
    month_bookings = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    # Format appointments for the template
    formatted_appointments = []
    for appt in appointments:
        formatted_appointments.append({
            'id': appt[0],
            'user_name': appt[1],
            'email': appt[2],
            'service': appt[3],
            'date': appt[4].strftime('%Y-%m-%d') if hasattr(appt[4], 'strftime') else str(appt[4]).split(' ')[0],
            'time': appt[4].strftime('%H:%M') if hasattr(appt[4], 'strftime') else str(appt[4]).split(' ')[1][:5],
            'status': 'Completed' if appt[5] else 'Pending'
        })

    # Prepare summary dict for dashboard cards
    summary = {
        'today_bookings': today_bookings,
        'week_bookings': week_bookings,
        'month_bookings': month_bookings,
        'total_users': total_users
    }

    # Prepare chart data as dicts for Jinja tojson
    booking_trends = {'labels': trends_labels, 'data': trends_data}
    service_popularity = {'labels': service_labels, 'data': service_counts}
    user_activity = {'labels': user_activity_labels, 'data': user_activity_counts}

    return render_template(
        'admin_dashboard.html',
        appointments=formatted_appointments,
        completed_appointments=completed_appointments,
        max_appointments=max_appointments,
        slot_analytics=slot_analytics,
        summary_cards=summary_cards,
        summary=summary,
        alerts=alerts,
        booking_trends=booking_trends,
        service_popularity=service_popularity,
        user_activity=user_activity
    )

# Set Max Appointments Per Slot
@app.route('/set_max_appointments', methods=['POST'])
def set_max_appointments():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    max_appointments = request.form.get('max_appointments', type=int)
    if max_appointments and max_appointments > 0:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS settings (setting_key VARCHAR(50) PRIMARY KEY, setting_value VARCHAR(50))")
        cursor.execute("REPLACE INTO settings (setting_key, setting_value) VALUES ('max_appointments_per_slot', %s)", (str(max_appointments),))
        conn.commit()
        conn.close()
        flash('Max appointments per time slot updated.')
    else:
        flash('Please enter a valid number greater than 0.')
    return redirect(url_for('admin_dashboard'))

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, hashed_password))
            conn.commit()  # Commit the transaction
        except Exception as e:
            conn.rollback()  # Rollback the transaction in case of an error
            raise e
        finally:
            cursor.close()
            conn.close()  # Ensure the connection is closed

        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        # Try user login by email
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email_or_username,))
        user = cursor.fetchone()
        # Try admin login by username
        cursor.execute(
            "SELECT * FROM admin_users WHERE username = %s OR email = %s",
            (email_or_username, email_or_username)
        )
        admin = cursor.fetchone()
        conn.close()

        # User login
        if user is not None and len(user) >= 4 and check_password_hash(user[3], password):
            session['user'] = user[1]  # username
            session['user_email'] = user[2]  # email
            # If password is exactly 10 chars and alphanumeric, assume it's a temp password
            if len(password) == 10 and password.isalnum():
                session['force_password_change'] = True
                return redirect(url_for('change_password'))
            return redirect(url_for('user_dashboard'))
        # Admin login
        elif admin is not None:
            # admin_users table columns: id, username, email, password_hash
            # admin[0] = id, admin[1] = username, admin[2] = email, admin[3] = password_hash
            password_hash = admin[3]
            username = admin[1]
            
            if check_password_hash(password_hash, password):
                session['admin'] = username
                return redirect(url_for('admin_dashboard'))
        flash("Invalid credentials. Please try again.")
    return render_template('login.html')

# User Dashboard
@app.route('/user_dashboard')
def user_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch pending appointments
    query = "SELECT id, service, date_time, FALSE AS completed FROM appointments WHERE email = %s ORDER BY date_time"
    cursor.execute(query, (session['user_email'],))
    pending_appointments = cursor.fetchall()

    # Fetch completed appointments
    query = "SELECT id, service, date_time, TRUE AS completed FROM completed_appointments WHERE email = %s ORDER BY date_time"
    cursor.execute(query, (session['user_email'],))
    completed_appointments = cursor.fetchall()

    appointments = pending_appointments + completed_appointments
    conn.close()

    # Prepare appointments for modern dashboard template
    formatted_appointments = []
    for appt in appointments:
        formatted_appointments.append({
            'id': appt[0],
            'service': appt[1],
            'date': appt[2].strftime('%Y-%m-%d') if hasattr(appt[2], 'strftime') else str(appt[2]).split(' ')[0],
            'time': appt[2].strftime('%H:%M') if hasattr(appt[2], 'strftime') else str(appt[2]).split(' ')[1][:5],
            'status': 'Completed' if appt[3] else 'Pending'
        })

    return render_template('user_dashboard.html', user_name=session['user'], appointments=formatted_appointments)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Fetch available time slots
    conn = get_db_connection()
    cursor = conn.cursor()
    time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
    def time_available(time):
        query = "SELECT COUNT(*) FROM appointments WHERE date_time = %s"
        cursor.execute(query, (f"{request.form['date']} {time}",))
        count = cursor.fetchone()[0]
        return count < 3

    conn.close()
    return render_template('booking.html', time_slots=time_slots, time_available=time_available)

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch max appointments per slot
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (setting_key VARCHAR(50) PRIMARY KEY, setting_value VARCHAR(50))")
    cursor.execute("SELECT setting_value FROM settings WHERE setting_key = 'max_appointments_per_slot'")
    max_slot = cursor.fetchone()
    max_appointments = int(max_slot[0]) if max_slot else MAX_APPOINTMENTS_PER_SLOT

    # Define available time slots
    time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
    time_availability = {}

    if request.method == 'POST':
        # Get form data
        date = request.form['date']
        contact_number = request.form['contact_number']
        service = request.form['service']
        time = request.form['time']

        # Check if the selected date is a holiday
        query = "SELECT * FROM holidays WHERE holiday_date = %s"
        cursor.execute(query, (date,))
        holiday = cursor.fetchone()
        if holiday:
            flash("Appointments cannot be booked on this day. Please choose another date.", 'danger')
            conn.close()
            return redirect(url_for('book_appointment'))

        # Check if the time slot is full
        date_time = f"{date} {time}"
        query = "SELECT COUNT(*) FROM appointments WHERE date_time = %s"
        cursor.execute(query, (date_time,))
        count = cursor.fetchone()[0]
        if count >= max_appointments:
            flash("The selected time slot is fully booked. Please choose another time or date.", 'danger')
            conn.close()
            return redirect(url_for('book_appointment'))

        # Insert the appointment
        query = "INSERT INTO appointments (customer_name, email, contact_number, service, date_time) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (session['user'], session['user_email'], contact_number, service, date_time))
        conn.commit()

        # Send email notifications
        send_email(session['user_email'], "Appointment Confirmation", f"Dear {session['user']}, your appointment for {service} on {date_time} has been confirmed.")
        send_email(admin_email, "New Appointment", f"New appointment booked by {session['user']} for {service} on {date_time}.")

        flash("Appointment booked successfully.")
        conn.close()
        return redirect(url_for('user_dashboard'))

    # Calculate time slot availability for GET requests
    if request.method == 'GET':
        date = request.args.get('date', None)
        if date:
            for time in time_slots:
                date_time = f"{date} {time}"
                query = "SELECT COUNT(*) FROM appointments WHERE date_time = %s"
                cursor.execute(query, (date_time,))
                count = cursor.fetchone()[0]
                time_availability[time] = count < max_appointments

    conn.close()
    return render_template('booking.html', time_slots=time_slots, time_availability=time_availability)

# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    session.pop('user', None)
    session.pop('user_email', None)
    return redirect(url_for('index'))

# Utility function to send emails
def send_email(to, subject, body):
    try:
        sender_email = app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME') or admin_email
        msg = Message(subject, sender=sender_email, recipients=[to])
        msg.body = body
        mail.send(msg)
        print(f"Email sent successfully to {to}: {subject}")
        return True
    except Exception as e:
        print(f"Error sending email to {to}: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/admin_cancel/<int:id>')
def admin_cancel_appointment(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch appointment details before deleting
    query = "SELECT customer_name, email, service, date_time FROM appointments WHERE id = %s"
    cursor.execute(query, (id,))
    appointment = cursor.fetchone()

    if not appointment:
        flash("Appointment not found.")
        return redirect(url_for('admin_dashboard'))

    customer_name, email, service, date_time = appointment

    # Delete the appointment
    query = "DELETE FROM appointments WHERE id = %s"
    cursor.execute(query, (id,))
    conn.commit()
    conn.close()

    # Send email notifications
    send_email(email, "Appointment Canceled", f"Dear {customer_name}, your appointment for {service} on {date_time} has been canceled.")
    send_email(admin_email, "Appointment Canceled", f"The appointment for {customer_name} on {date_time} has been canceled.")

    flash("Appointment canceled successfully.")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_reschedule/<int:id>', methods=['POST', 'GET'])
def admin_reschedule_appointment(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_date = request.form['date']
        new_time = request.form['time']
        date_time = f"{new_date} {new_time}"

        # Check if the time slot is already booked
        query = "SELECT * FROM appointments WHERE date_time = %s AND id != %s"
        cursor.execute(query, (date_time, id))
        existing_appointment = cursor.fetchone()

        if existing_appointment:
            flash("The selected time slot is already booked. Please choose a different time.")
            return redirect(url_for('admin_reschedule_appointment', id=id))

        # Update the appointment
        query = "UPDATE appointments SET date_time = %s WHERE id = %s"
        cursor.execute(query, (date_time, id))
        conn.commit()

        # Fetch updated appointment details
        query = "SELECT customer_name, email, service FROM appointments WHERE id = %s"
        cursor.execute(query, (id,))
        appointment = cursor.fetchone()
        conn.close()

        # Send email notifications
        customer_name, email, service = appointment
        send_email(email, "Appointment Rescheduled", f"Dear {customer_name}, your appointment for {service} has been rescheduled to {new_date} at {new_time}.")
        send_email(admin_email, "Appointment Rescheduled", f"The appointment for {customer_name} has been rescheduled to {new_date} at {new_time}.")

        flash("Appointment rescheduled successfully.")
        return redirect(url_for('admin_dashboard'))

    # Fetch current appointment details for the form
    query = "SELECT DATE(date_time), TIME(date_time) FROM appointments WHERE id = %s"
    cursor.execute(query, (id,))
    appointment = cursor.fetchone()
    conn.close()

    return render_template('reschedule1.html', id=id, appointment=appointment)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            hashed_temp = generate_password_hash(temp_password, method='pbkdf2:sha256')
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_temp, email))
            conn.commit()
            send_email(email, "Password Reset", f"Your temporary password is: {temp_password}\nPlease log in and change your password immediately.")
            flash("A temporary password has been sent to your email.")
        else:
            flash("No user found with that email address.")
        cursor.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_password = request.form['new_password']
        hashed_new = generate_password_hash(new_password, method='pbkdf2:sha256')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_new, session['user_email']))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Password changed successfully.")
        session.pop('force_password_change', None)
        return redirect(url_for('user_dashboard'))
    return render_template('change_password.html')


if __name__ == '__main__':
    app.run(debug=True)
