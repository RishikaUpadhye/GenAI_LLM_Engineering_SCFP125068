import sqlite3
import hashlib
import hmac
import secrets
from pathlib import Path
from datetime import date, timedelta, datetime

DB_PATH = Path(__file__).resolve().parents[1] / "lab_book.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tests (
        test_id TEXT PRIMARY KEY,
        test_name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS slots (
        slot_id TEXT PRIMARY KEY,
        test_id TEXT NOT NULL,
        slot_date TEXT NOT NULL,
        slot_time TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Available',
        FOREIGN KEY (test_id) REFERENCES tests(test_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        test_id TEXT NOT NULL,
        slot_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Confirmed',
        booking_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (test_id) REFERENCES tests(test_id),
        FOREIGN KEY (slot_id) REFERENCES slots(slot_id)
    )
    """)

    tests_data = [
        ("T001", "CBC", "Blood", "Complete Blood Count test", 500.0),
        ("T002", "Lipid Profile", "Blood", "Measures cholesterol levels", 800.0),
        ("T003", "Thyroid Profile", "Blood", "Measures thyroid hormones", 900.0),
        ("T004", "Urine Routine", "Urine", "Routine urine examination", 300.0),
        ("T005", "Urine Culture", "Urine", "Checks for bacterial growth in urine", 600.0),
        ("T006", "Chest X-Ray", "Imaging", "Chest radiography examination", 700.0),
        ("T007", "Ultrasound", "Imaging", "Ultrasound examination", 1200.0),
        ("T008", "ECG", "Imaging", "Electrocardiogram examination", 400.0),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO tests
    (test_id, test_name, category, description, price)
    VALUES (?, ?, ?, ?, ?)
    """, tests_data)

    tomorrow = date.today() + timedelta(days=1)
    slot_date = tomorrow.isoformat()

    slots_data = []
    for test_number in range(1, 9):
        test_id = f"T{test_number:03d}"
        for slot_number, slot_time in enumerate(["09:00", "10:00", "11:00"], start=1):
            slot_id = f"S{test_number:03d}{slot_number}"
            status = "Booked" if test_id == "T008" else "Available"
            slots_data.append((slot_id, test_id, slot_date, slot_time, status))

    cursor.executemany("""
    INSERT OR IGNORE INTO slots
    (slot_id, test_id, slot_date, slot_time, status)
    VALUES (?, ?, ?, ?, ?)
    """, slots_data)

    conn.commit()
    conn.close()


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 200000
    )
    return salt.hex() + ":" + password_hash.hex()


def verify_password(password, stored_hash):
    try:
        salt_hex, password_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 200000
        ).hex()
        return hmac.compare_digest(new_hash, password_hex)
    except (ValueError, TypeError):
        return False


def create_user(name, email, password):
    conn = get_connection()
    user_id = "U" + secrets.token_hex(6).upper()
    try:
        conn.execute("""
            INSERT INTO users (user_id, name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            name.strip(),
            email.strip().lower(),
            hash_password(password),
            datetime.now().isoformat(timespec="seconds")
        ))
        conn.commit()
        return True, user_id, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, None, "This email is already registered."
    finally:
        conn.close()


def authenticate_user(email, password):
    conn = get_connection()
    row = conn.execute("""
        SELECT user_id, name, email, password_hash
        FROM users WHERE email = ?
    """, (email.strip().lower(),)).fetchone()
    conn.close()

    if row and verify_password(password, row["password_hash"]):
        return dict(row)
    return None


def get_user_name(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT name FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row["name"] if row else "Patient"


def get_tests():
    conn = get_connection()
    rows = conn.execute("""
        SELECT test_id, test_name, category, description, price
        FROM tests ORDER BY test_id
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_available_slots(test_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT slot_id, slot_date, slot_time
        FROM slots
        WHERE test_id = ? AND status = 'Available'
        ORDER BY slot_date, slot_time
    """, (test_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_bookings(user_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.booking_id, t.test_id, t.test_name, s.slot_id,
               s.slot_date, s.slot_time, b.status, t.price
        FROM bookings b
        JOIN tests t ON b.test_id = t.test_id
        JOIN slots s ON b.slot_id = s.slot_id
        WHERE b.user_id = ?
        ORDER BY b.booking_date DESC, s.slot_date, s.slot_time
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_booking_for_user(user_id, booking_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT b.booking_id, b.user_id, b.test_id, b.slot_id, b.status,
               t.test_name, t.price, s.slot_date, s.slot_time
        FROM bookings b
        JOIN tests t ON b.test_id = t.test_id
        JOIN slots s ON b.slot_id = s.slot_id
        WHERE b.booking_id = ? AND b.user_id = ?
    """, (booking_id, user_id)).fetchone()
    conn.close()
    return dict(row) if row else None


def book_test(user_id, test_id, slot_id):
    conn = get_connection()
    cursor = conn.cursor()

    test = cursor.execute(
        "SELECT test_name, price FROM tests WHERE test_id = ?", (test_id,)
    ).fetchone()

    slot = cursor.execute("""
        SELECT slot_date, slot_time, status
        FROM slots WHERE slot_id = ? AND test_id = ?
    """, (slot_id, test_id)).fetchone()

    if test is None:
        conn.close()
        return False, "Test not found."

    if slot is None:
        conn.close()
        return False, "Slot not found for this test."

    if slot["status"] != "Available":
        conn.close()
        return False, "This slot is no longer available."

    duplicate = cursor.execute("""
        SELECT booking_id FROM bookings
        WHERE user_id = ? AND test_id = ? AND status = 'Confirmed'
    """, (user_id, test_id)).fetchone()

    if duplicate:
        conn.close()
        return False, "You already have a confirmed booking for this test."

    booking_id = "B" + datetime.now().strftime("%Y%m%d%H%M%S%f")

    cursor.execute("""
        UPDATE slots SET status = 'Booked'
        WHERE slot_id = ? AND status = 'Available'
    """, (slot_id,))

    if cursor.rowcount != 1:
        conn.rollback()
        conn.close()
        return False, "This slot was just booked. Please choose another slot."

    cursor.execute("""
        INSERT INTO bookings
        (booking_id, user_id, test_id, slot_id, status, booking_date)
        VALUES (?, ?, ?, ?, 'Confirmed', ?)
    """, (booking_id, user_id, test_id, slot_id, date.today().isoformat()))

    conn.commit()
    receipt = cursor.execute("""
        SELECT booking_id, user_id, test_id, slot_id, status
        FROM bookings WHERE booking_id = ?
    """, (booking_id,)).fetchone()
    conn.close()
    return True, dict(receipt)


def cancel_test_booking(user_id, booking_id):
    conn = get_connection()
    cursor = conn.cursor()

    booking = cursor.execute("""
        SELECT booking_id, slot_id, status
        FROM bookings
        WHERE booking_id = ? AND user_id = ?
    """, (booking_id, user_id)).fetchone()

    if booking is None:
        conn.close()
        return False, "Booking not found in your account."

    if booking["status"] != "Confirmed":
        conn.close()
        return False, "This booking is already cancelled."

    cursor.execute("""
        UPDATE bookings SET status = 'Cancelled'
        WHERE booking_id = ? AND user_id = ? AND status = 'Confirmed'
    """, (booking_id, user_id))

    if cursor.rowcount != 1:
        conn.rollback()
        conn.close()
        return False, "The booking could not be cancelled. Please try again."

    cursor.execute("""
        UPDATE slots SET status = 'Available'
        WHERE slot_id = ?
    """, (booking["slot_id"],))

    conn.commit()
    conn.close()
    return True, "Booking cancelled successfully."
