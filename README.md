# Sasu's Barbering Saloon Appointment Scheduler

A modern, web-based appointment scheduling and management system for the Barbering Saloon, built with Flask, MySQL, and Bootstrap. The platform supports robust user and admin authentication, appointment booking, management, analytics, and notifications.

## Features

### User Features
- **Registration & Login:** Secure user registration and login with password hashing.
- **Password Reset:** Users can reset their password via email (temporary password, forced change on next login).
- **Book Appointments:** Book available time slots for services, with real-time slot availability.
- **Reschedule & Cancel:** Users can reschedule or cancel their appointments.
- **Dashboard:** Modern, responsive dashboard showing upcoming and past appointments.
- **Email Notifications:** Receive confirmation, reschedule, and cancellation emails.

### Admin Features
- **Admin Login:** Secure admin authentication.
- **View & Manage Appointments:** View all appointments, mark as completed, reschedule, or cancel.
- **Set Holidays:** Mark specific dates as holidays (no bookings allowed).
- **Set Max Appointments per Slot:** Configure the maximum number of bookings per time slot.
- **Add Appointments:** Book appointments on behalf of customers.
- **Advanced Analytics Dashboard:**
  - Summary cards (today/week/month bookings, total users)
  - Booking trends (line chart)
  - Service popularity (bar chart)
  - User activity (top users)
  - Slot analytics (availability for next 7 days)
  - Alerts for holidays, fully booked, or low booking days
- **Modern UI:** Glassmorphism, background images, and responsive Bootstrap design.

## Technology Stack
- **Backend:** Python, Flask, Flask-Bcrypt, Flask-Mail
- **Frontend:** Bootstrap 5, Chart.js, modern HTML/CSS
- **Database:** MySQL (utf8mb4 charset)

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd business_scheduler
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure Database:**
   - Create a MySQL database and user.
   - Update `config.py` with your DB credentials and mail settings.
   - Ensure all tables (`users`, `admin_users`, `appointments`, `completed_appointments`, `holidays`, `settings`) exist. See code for schema.
4. **Create an Admin User:**
   - Run `insert_admin.py` to add an admin account.
5. **Run the App:**
   ```sh
   python app.py
   ```
6. **Access the App:**
   - Open [http://localhost:5000](http://localhost:5000) in your browser.

## Folder Structure
- `app.py` - Main Flask application
- `config.py` - Database and mail configuration
- `insert_admin.py` - Script to create admin user
- `templates/` - HTML templates (Bootstrap, glassmorphism)
- `static/images/` - Background images
- `requirements.txt` - Python dependencies

## Customization
- Update background images in `static/images/` for your brand.
- Adjust available time slots or services in `app.py` as needed.
- Modify email templates/messages in `app.py` for your business.

## Security Notes
- Passwords are securely hashed.
- All user/admin actions require authentication.
- Email notifications are sent for all critical actions.

## License
This project is for SASU. Please contact the owner for reuse or redistribution.

---

**Modern, powerful, and easy-to-use appointment management for your BUSiness!**
