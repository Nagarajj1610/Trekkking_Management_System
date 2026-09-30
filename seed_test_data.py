import sqlite3

connection = sqlite3.connect('g1_adventures.db')
cursor = connection.cursor()

# -----------------------------
# Test Trekker
# -----------------------------

cursor.execute("""
INSERT OR IGNORE INTO User
(name, email, password, role, account_status)
VALUES (?, ?, ?, ?, ?)
""", (
    'Test Trekker',
    'trekker@test.com',
    'trekker123',
    'Trekker',
    'Active'
))


# -----------------------------
# Test Trek Staff
# -----------------------------

cursor.execute("""
INSERT OR IGNORE INTO User
(name, email, password, role, account_status)
VALUES (?, ?, ?, ?, ?)
""", (
    'Test Staff',
    'staff@test.com',
    'staff123',
    'Trek Staff',
    'Active'
))


# Get Staff user ID
staff_user = cursor.execute("""
SELECT user_id
FROM User
WHERE email = ?
""", ('staff@test.com',)).fetchone()

staff_user_id = staff_user[0]


# Create StaffProfile if it doesn't exist
cursor.execute("""
INSERT OR IGNORE INTO StaffProfile
(user_id, phone, specialization, approval_status)
VALUES (?, ?, ?, ?)
""", (
    staff_user_id,
    '9999999999',
    'Trekking Guide',
    'Approved'
))


# Get StaffProfile ID
staff_profile = cursor.execute("""
SELECT staff_id
FROM StaffProfile
WHERE user_id = ?
""", (staff_user_id,)).fetchone()

staff_id = staff_profile[0]


# -----------------------------
# Test Trek
# -----------------------------

cursor.execute("""
INSERT INTO Trek
(
    trek_name,
    location,
    difficulty,
    duration,
    available_slots,
    staff_id,
    status,
    start_date,
    end_date,
    description
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    'Test Mountain Trek',
    'Munnar',
    'Medium',
    2,
    10,
    staff_id,
    'Open',
    '2026-09-01',
    '2026-09-02',
    'Test trek created for application testing.'
))


connection.commit()
connection.close()

print("Test data created successfully.")
print()
print("ADMIN")
print("Email: admin@gmail.com")
print("Password: admin123")
print()
print("TREKKER")
print("Email: trekker@test.com")
print("Password: trekker123")
print()
print("STAFF")
print("Email: staff@test.com")
print("Password: staff123")
print()
print("TEST TREK")
print("Name: Test Mountain Trek")
print("Location: Munnar")

