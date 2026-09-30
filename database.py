import sqlite3

connection = sqlite3.connect('g1_adventures.db')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    account_status TEXT NOT NULL DEFAULT 'Active'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS StaffProfile (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    phone TEXT,
    specialization TEXT,
    approval_status TEXT NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES User(user_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Trek (
    trek_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trek_name TEXT NOT NULL,
    location TEXT NOT NULL,
    difficulty TEXT,
    duration INTEGER,
    available_slots INTEGER NOT NULL CHECK (available_slots >= 0),
    staff_id INTEGER,
    status TEXT NOT NULL DEFAULT 'Open',
    start_date TEXT,
    end_date TEXT,
    description TEXT,
    FOREIGN KEY (staff_id) REFERENCES StaffProfile(staff_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Booking (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    trek_id INTEGER NOT NULL,
    booking_status TEXT NOT NULL DEFAULT 'Pending',
    booking_date TEXT,
    payment_status TEXT NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (trek_id) REFERENCES Trek(trek_id)
)
""")

cursor.execute("""
INSERT OR IGNORE INTO User
(name, email, password, role, account_status)
VALUES (?, ?, ?, ?, ?)
""", (
    'Admin',
    'admin@gmail.com',
    'admin123',
    'Admin',
    'Active'
))

connection.commit()
connection.close()

print("All tables created successfully")

