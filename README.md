# Trekking Management System

A web-based Trekking Management System developed as a student project using Flask, SQLite, HTML, CSS, and Jinja2.

The application is designed to manage trekking routes, trekker registrations, staff, bookings, and administrative operations through a role-based web interface.

## Live Demo

## Live Demo

🌐 **Live Website:**  
https://trekkking-management-system.onrender.com
The application is deployed on Render for demonstration purposes.

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@gmail.com` | `admin123` |
| Trekker | `trekker@test.com` | `trekker123` |
| Staff | `staff@test.com` | `staff123` |

> **Note:** These credentials are created specifically for demonstrating the application. Please do not enter personal information while testing the demo.

# Trekking Management System

A web-based Trekking Management System developed as a student project using Flask, SQLite, HTML, CSS, and Jinja2.

The application is designed to manage trekking routes, trekker registrations, staff, bookings, and administrative operations through a role-based web interface.

## Live Demo

**Live Website:**  
https://trekking-management-system.onrender.com

> The application is deployed on Render for demonstration purposes.

## Project Overview

The Trekking Management System provides a centralized platform for managing trekking activities and related operations.

The system supports different user roles and provides separate functionality for administrators, staff, and trekkers.

### Main Roles

- **Admin**
  - Manage trekking routes
  - Manage users and staff
  - Review staff registrations
  - Assign staff to treks
  - Manage bookings
  - Search and manage records
  - Blacklist users when required

- **Staff**
  - Access assigned trekking activities
  - View relevant trek and booking information
  - Manage assigned operations

- **Trekker**
  - Register and log in
  - Browse available treks
  - View trek details
  - Make and manage bookings

## Technologies Used

### Backend
- Python
- Flask
- SQLite

### Frontend
- HTML
- CSS
- Jinja2 Templates

### Deployment
- Render
## Project Overview

The Trekking Management System provides a centralized platform for managing trekking activities and related operations.

The system supports different user roles and provides separate functionality for administrators, staff, and trekkers.

### Main Roles

- **Admin**
  - Manage trekking routes
  - Manage users and staff
  - Review staff registrations
  - Assign staff to treks
  - Manage bookings
  - Search and manage records
  - Blacklist users when required

- **Staff**
  - Access assigned trekking activities
  - View relevant trek and booking information
  - Manage assigned operations

- **Trekker**
  - Register and log in
  - Browse available treks
  - View trek details
  - Make and manage bookings

## Technologies Used

### Backend
- Python
- Flask
- SQLite

### Frontend
- HTML
- CSS
- Jinja2 Templates

### Deployment
- Render
- Gunicorn

## Project Structure

```text
Trekking_Management_System/
│
├── app.py
├── database.py
├── g1_adventures.db
├── requirements.txt
├── render.yaml
│
├── templates/
│   ├── login.html
│   ├── register.html
│   └── ...
│
└── static/
    ├── css/
    ├── js/
    └── ...
