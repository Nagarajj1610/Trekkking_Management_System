import sqlite3
from flask import Flask, g, request, redirect, render_template, session


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'g1_adventures.db')

app=Flask(__name__)



app.secret_key = 'g1-adventures-secret-key'


def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row

    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)

    if db is not None:
        db.close()

def is_logged_in():
    return 'user_id' in session


def is_admin():
    return session.get('role') == 'Admin'


def is_staff():
    return session.get('role') == 'Trek Staff'


def is_trekker():
    return session.get('role') == 'Trekker'

def admin_required():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return False
    return True


def staff_required():
    if 'user_id' not in session or session.get('role') != 'Trek Staff':
        return False
    return True

@app.route('/')
def home():
    return redirect('/login')
    


@app.route('/register', methods=['GET', 'POST'])
def register_user():

    if request.method == 'GET':
        return render_template('signup.html')

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    db = get_db()

    existing_user = db.execute(
        'SELECT user_id FROM User WHERE email = ?',
        (email,)
    ).fetchone()

    if existing_user:
     return render_template(
        'signup.html',
        error="Email already registered"
    )


    cursor = db.execute(
        'INSERT INTO User (name, email, password, role) VALUES (?, ?, ?, ?)',
        (name, email, password, role)
    )

    user_id = cursor.lastrowid

    if role == 'Trek Staff':
        db.execute(
            'INSERT INTO StaffProfile (user_id, approval_status) VALUES (?, ?)',
            (user_id, 'Pending')
        )

    db.commit()

    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login_user():

    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()

        user = db.execute(
            'SELECT * FROM User WHERE email = ?',
            (email,)
        ).fetchone()

        if user is None:
            return "Invalid email or password"

        if user['password'] != password:
            return "Invalid email or password"

        if user['account_status'] != 'Active':
            return "Account is inactive"

        if user['role'] == 'Trek Staff':
            staff = db.execute(
                'SELECT approval_status FROM StaffProfile WHERE user_id = ?',
                (user['user_id'],)
            ).fetchone()

            if staff['approval_status'] != 'Approved':
                return "Staff account is awaiting admin approval"
        session['user_id'] = user['user_id']
        session['role'] = user['role']

        if user['role'] == 'Admin':
         return redirect('/admin/dashboard')

        elif user['role'] == 'Trek Staff':
         return redirect('/staff/dashboard')

        elif user['role'] == 'Trekker':
         return redirect('/user/dashboard')



    


@app.route('/admin/dashboard')
def admin_dashboard():

    if not admin_required():
        return redirect('/login')

    db = get_db()

    total_treks = db.execute(
        'SELECT COUNT(*) FROM Trek'
    ).fetchone()[0]

    total_users = db.execute(
        "SELECT COUNT(*) FROM User WHERE role = 'Trekker'"
    ).fetchone()[0]

    total_staff = db.execute(
        "SELECT COUNT(*) FROM User WHERE role = 'Trek Staff'"
    ).fetchone()[0]

    total_bookings = db.execute(
        'SELECT COUNT(*) FROM Booking'
    ).fetchone()[0]

    return render_template(
        'admin_dashboard.html',
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings
    )

@app.route('/admin/search')
def admin_search():

    if not admin_required():
        return redirect('/login')

    query = request.args.get('query', '')

    db = get_db()

    users = db.execute("""
        SELECT user_id,
               name,
               email,
               role,
               account_status
        FROM User
        WHERE name LIKE ? OR email LIKE ?
    """, ('%' + query + '%', '%' + query + '%')).fetchall()

    

    staff = db.execute("""
        SELECT StaffProfile.staff_id, User.user_id, User.name, User.email,
               StaffProfile.approval_status
        FROM StaffProfile
        JOIN User ON StaffProfile.user_id = User.user_id
        WHERE User.name LIKE ? OR User.email LIKE ?
    """, ('%' + query + '%', '%' + query + '%')).fetchall()

    treks = db.execute("""
        SELECT trek_id, trek_name, location, difficulty, status
        FROM Trek
        WHERE trek_name LIKE ? OR location LIKE ?
    """, ('%' + query + '%', '%' + query + '%')).fetchall()

    return render_template(
        'admin_search.html',
        users=users,
        staff=staff,
        treks=treks,
        query=query
    )

@app.route('/trek/<int:trek_id>/delete', methods=['POST'])
def delete_trek(trek_id):

    if not admin_required():
        return redirect('/login')

    db = get_db()

    db.execute(
        'DELETE FROM Trek WHERE trek_id = ?',
        (trek_id,)
    )

    db.commit()

    return redirect('/treks')



@app.route('/admin/bookings')
def admin_bookings():

    if not admin_required():
        return redirect('/login')

    db = get_db()

    bookings = db.execute("""
        SELECT
            Booking.booking_id,
            User.name,
            User.email,
            Trek.trek_name,
            Trek.location,
            Booking.booking_date,
            Booking.booking_status,
            Booking.payment_status
        FROM Booking
        JOIN User ON Booking.user_id = User.user_id
        JOIN Trek ON Booking.trek_id = Trek.trek_id
        ORDER BY Booking.booking_id DESC
    """).fetchall()

    return render_template(
        'admin_bookings.html',
        bookings=bookings
    )

@app.route('/admin/staff')
def admin_staff():

    if not admin_required():
        return redirect('/login')

    db = get_db()

    staff = db.execute("""
    SELECT
        StaffProfile.staff_id,
        User.user_id,
        User.name,
        User.email,
        User.account_status,
        StaffProfile.phone,
        StaffProfile.specialization,
        StaffProfile.approval_status
    FROM StaffProfile
    JOIN User ON StaffProfile.user_id = User.user_id
""").fetchall()

    return render_template(
        'admin_manage_staff.html',
        staff=staff
    )

@app.route('/admin/staff/<int:staff_id>/assign')
def assign_staff_page(staff_id):

    if not admin_required():
        return redirect('/login')

    db = get_db()

    staff = db.execute("""
        SELECT
            StaffProfile.staff_id,
            User.name
        FROM StaffProfile
        JOIN User ON StaffProfile.user_id = User.user_id
        WHERE StaffProfile.staff_id = ?
    """, (staff_id,)).fetchone()

    if staff is None:
        return "Staff member not found"

    treks = db.execute("""
        SELECT trek_id, trek_name
        FROM Trek
        WHERE staff_id IS NULL
    """).fetchall()

    return render_template(
        'assign_trek.html',
        staff=staff,
        treks=treks
    )

@app.route('/admin/staff/<int:staff_id>/approve', methods=['POST'])
def approve_staff(staff_id):

    if not admin_required():
        return redirect('/login')

    db = get_db()

    db.execute(
        'UPDATE StaffProfile SET approval_status = ? WHERE staff_id = ?',
        ('Approved', staff_id)
    )

    db.commit()

    return redirect('/admin/staff')

@app.route('/admin/trek/<int:trek_id>/assign-staff', methods=['POST'])
def assign_staff(trek_id):

    if not admin_required():
     return redirect('/login')

    staff_id = request.form['staff_id']

    db = get_db()

    db.execute(
        'UPDATE Trek SET staff_id = ? WHERE trek_id = ?',
        (staff_id, trek_id)
    )

    db.commit()

    return redirect('/trek/' + str(trek_id))


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


@app.route('/treks')
def view_treks():
    if not admin_required():
     return redirect('/login')


    db = get_db()

    treks = db.execute(
        'SELECT * FROM Trek'
    ).fetchall()

    return render_template(
        'manage_treks.html',
        treks=treks
    )


@app.route('/trek/add', methods=['GET', 'POST'])
def add_trek():

    if not admin_required():
        return redirect('/login')

    if request.method == 'GET':
     return render_template('add_trek.html')
    if request.method == 'POST':
     
     db = get_db()

    trek_name = request.form['trek_name']
    location = request.form['location']
    difficulty = request.form['difficulty']
    duration = request.form['duration']
    available_slots = request.form['available_slots']
    status = request.form['status']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    description = request.form['description']

    db.execute("""
        INSERT INTO Trek (
            trek_name,
            location,
            difficulty,
            duration,
            available_slots,
            status,
            start_date,
            end_date,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trek_name,
        location,
        difficulty,
        duration,
        available_slots,
        status,
        start_date,
        end_date,
        description
    ))

    db.commit()

    return redirect('/treks')

@app.route('/trek/<int:trek_id>')
def trek_details(trek_id):
    if not is_logged_in():
     return redirect('/login')

    db = get_db()

    trek = db.execute(
        'SELECT * FROM Trek WHERE trek_id = ?',
        (trek_id,)
    ).fetchone()

    if trek is None:
        return "Trek not found"

    return render_template(
        'trek_details.html',
        trek=trek
    )


@app.route('/trek/<int:trek_id>/edit')
def edit_trek(trek_id):

    if not admin_required():
        return redirect('/login')

    db = get_db()

    trek = db.execute(
        'SELECT * FROM Trek WHERE trek_id = ?',
        (trek_id,)
    ).fetchone()

    if trek is None:
        return "Trek not found"

    return render_template(
        'edit_trek.html',
        trek=trek
    )

@app.route('/trek/<int:trek_id>/update', methods=['POST'])
def update_trek(trek_id):

    if not admin_required():
        return redirect('/login')
    db = get_db()

    trek_name = request.form['trek_name']
    location = request.form['location']
    difficulty = request.form['difficulty']
    duration = request.form['duration']
    available_slots = request.form['available_slots']
    status = request.form['status']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    description = request.form['description']

    db.execute("""
        UPDATE Trek
        SET trek_name = ?,
            location = ?,
            difficulty = ?,
            duration = ?,
            available_slots = ?,
            status = ?,
            start_date = ?,
            end_date = ?,
            description = ?
        WHERE trek_id = ?
    """, (
        trek_name,
        location,
        difficulty,
        duration,
        available_slots,
        status,
        start_date,
        end_date,
        description,
        trek_id
    ))

    db.commit()

    return redirect('/trek/' + str(trek_id))


@app.route('/book', methods=['POST'])
def create_booking():

    if not is_trekker():
        return redirect('/login')

    user_id = session['user_id']
    trek_id = request.form['trek_id']
    booking_date = request.form['booking_date']

    db = get_db()

    trek = db.execute(
        'SELECT available_slots, status FROM Trek WHERE trek_id = ?',
        (trek_id,)
    ).fetchone()

    if trek is None:
        return "Trek not found"

    if trek['status'] != 'Open':
        return "This trek is not open for booking"

    if trek['available_slots'] <= 0:
        return "No slots available"

    db.execute("""
        INSERT INTO Booking (
            user_id,
            trek_id,
            booking_status,
            booking_date,
            payment_status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        trek_id,
        'Pending',
        booking_date,
        'Pending'
    ))

    db.execute("""
        UPDATE Trek
        SET available_slots = available_slots - 1
        WHERE trek_id = ?
    """, (trek_id,))

    db.commit()

    return redirect('/user/bookings')


@app.route('/admin/staff/<int:user_id>/deactivate', methods=['POST'])
def deactivate_staff(user_id):

    if not admin_required():
        return redirect('/login')

    db = get_db()

    db.execute(
        'UPDATE User SET account_status = ? WHERE user_id = ? AND role = ?',
        ('Inactive', user_id, 'Trek Staff')
    )

    db.commit()

    return redirect('/admin/staff')

@app.route('/admin/user/<int:user_id>/deactivate', methods=['POST'])
def deactivate_user(user_id):

    if not admin_required():
        return redirect('/login')

    db = get_db()

    db.execute(
        'UPDATE User SET account_status = ? WHERE user_id = ? AND role = ?',
        ('Inactive', user_id, 'Trekker')
    )

    db.commit()

    return redirect('/admin/search')


@app.route('/user/bookings')
def view_bookings():

    if  not is_trekker():
     return redirect('/login')

    user_id = session['user_id']

    db = get_db()

    bookings = db.execute("""
        SELECT
         Booking.booking_id,
         Booking.booking_status,
         Booking.booking_date,
         Booking.payment_status,
         Trek.trek_name,
         Trek.location,
         Trek.status
        FROM Booking
        JOIN Trek
        ON Booking.trek_id = Trek.trek_id
        WHERE Booking.user_id = ?
    """, (user_id,)).fetchall()

    return render_template(
        'trekker_view_bookings.html',
        bookings=bookings
    )

@app.route('/staff/dashboard')
def staff_dashboard():

    if not staff_required():
        return redirect('/login')

    db = get_db()

    staff = db.execute("""
    SELECT staff_id, approval_status
    FROM StaffProfile
    WHERE user_id = ?
""", (session['user_id'],)).fetchone()

    if staff is None:
        return "Staff profile not found"

    if staff['approval_status'] != 'Approved':
        return "Staff account is awaiting admin approval"

    treks = db.execute("""
    SELECT
        Trek.trek_id,
        Trek.trek_name,
        Trek.location,
        Trek.difficulty,
        Trek.available_slots,
        Trek.status,
        COUNT(Booking.booking_id) AS registered_users
        FROM Trek
        LEFT JOIN Booking
        ON Trek.trek_id = Booking.trek_id
        WHERE Trek.staff_id = ?
        GROUP BY Trek.trek_id
    """, (staff['staff_id'],)).fetchall()

    return render_template(
        'staff_dashboard.html',
        treks=treks
    )

@app.route('/staff/trek/<int:trek_id>/participants')
def participants(trek_id):

    if not staff_required():
        return redirect('/login')

    db = get_db()

    staff = db.execute(
        'SELECT staff_id FROM StaffProfile WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()

    trek = db.execute(
        'SELECT * FROM Trek WHERE trek_id = ? AND staff_id = ?',
        (trek_id, staff['staff_id'])
    ).fetchone()

    if trek is None:
        return "You are not assigned to this trek"

    participants = db.execute("""
        SELECT
            User.user_id,
            User.name,
            User.email,
            Booking.booking_id,
            Booking.booking_status,
            Booking.booking_date
        FROM Booking
        JOIN User
        ON Booking.user_id = User.user_id
        WHERE Booking.trek_id = ?
    """, (trek_id,)).fetchall()

    return render_template(
        'participants.html',
        trek=trek,
        participants=participants
    )

@app.route('/staff/trek/<int:trek_id>/manage')
def staff_manage_trek(trek_id):

    if not staff_required():
        return redirect('/login')

    db = get_db()

    staff = db.execute(
        'SELECT staff_id FROM StaffProfile WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()

    trek = db.execute(
        'SELECT * FROM Trek WHERE trek_id = ? AND staff_id = ?',
        (trek_id, staff['staff_id'])
    ).fetchone()

    if trek is None:
        return "You are not assigned to this trek"

    return render_template(
        'staff_manage_trek.html',
        trek=trek
    )

@app.route('/staff/trek/<int:trek_id>/update', methods=['POST'])
def staff_update_trek(trek_id):

    if not staff_required():
        return redirect('/login')

    available_slots = request.form['available_slots']
    status = request.form['status']

    db = get_db()

    staff = db.execute(
        'SELECT staff_id FROM StaffProfile WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()

    trek = db.execute(
        'SELECT trek_id FROM Trek WHERE trek_id = ? AND staff_id = ?',
        (trek_id, staff['staff_id'])
    ).fetchone()

    if trek is None:
        return "You are not assigned to this trek"

    db.execute("""
        UPDATE Trek
        SET available_slots = ?, status = ?
        WHERE trek_id = ?
    """, (available_slots, status, trek_id))

    db.commit()

    return redirect('/staff/dashboard')

@app.route('/user/profile', methods=['GET', 'POST'])
def edit_profile():

    if not is_trekker():
        return redirect('/login')

    db = get_db()

    if request.method == 'GET':

        user = db.execute(
            'SELECT * FROM User WHERE user_id = ?',
            (session['user_id'],)
         ).fetchone()

        return render_template(
            'edit_profile.html',
            user=user
        )

    name = request.form['name']
    email = request.form['email']

    db.execute("""
        UPDATE User
        SET name = ?, email = ?
        WHERE user_id = ?
    """, (name, email, session['user_id']))

    db.commit()

    return redirect('/user/dashboard')

@app.route('/user/dashboard')
def user_dashboard():

    if not is_trekker():
        return redirect('/login')

    db = get_db()

    query = request.args.get('query', '')

    available_treks = db.execute("""
        SELECT *
        FROM Trek
        WHERE status = 'Open'
        AND available_slots > 0
        AND (trek_name LIKE ? OR location LIKE ?)
    """, ('%' + query + '%', '%' + query + '%')).fetchall()

    booked_treks = db.execute("""
        SELECT
            Booking.booking_id,
            Booking.booking_status,
            Booking.booking_date,
            Trek.trek_name,
            Trek.location,
            Trek.status
        FROM Booking
        JOIN Trek
        ON Booking.trek_id = Trek.trek_id
        WHERE Booking.user_id = ?
        ORDER BY Booking.booking_id DESC
    """, (session['user_id'],)).fetchall()

    return render_template(
        'trekker_dashboard.html',
        available_treks=available_treks,
        booked_treks=booked_treks,
        query=query
    )


@app.route('/user/history')
def user_history():

    if not is_trekker():
        return redirect('/login')

    db = get_db()

    history = db.execute("""
        SELECT
            Booking.booking_id,
            Booking.booking_date,
            Booking.booking_status,
            Trek.trek_name,
            Trek.location,
            Trek.start_date,
            Trek.end_date,
            Trek.status
        FROM Booking
        JOIN Trek
        ON Booking.trek_id = Trek.trek_id
        WHERE Booking.user_id = ?
        AND Trek.status = 'Completed'
        ORDER BY Booking.booking_id DESC
    """, (session['user_id'],)).fetchall()

    return render_template(
        'trekking_history.html',
        history=history
    )


if __name__ == '__main__':
    app.run(debug=True)
