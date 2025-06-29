import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",          # Replace if needed
    password="Siddiqui@12789",          # Replace if needed
    database="hotel_website"
)
cursor = conn.cursor()

st.set_page_config(page_title="Hotel Management", layout="centered")
st.title("🏨 Hotel Management System")

menu = st.sidebar.selectbox("Select Option", ["Register Guest", "Book Room", "View Bookings", "Check-Out", "Payments"])

# Register Guest
def register_guest():
    st.header("🧍 Register New Guest")
    first = st.text_input("First Name")
    last = st.text_input("Last Name")
    contact = st.text_input("Contact Number")
    email = st.text_input("Email")
    address = st.text_area("Address")
    dob = st.date_input("Date of Birth")

    if st.button("Register Guest"):
        query = "INSERT INTO Guests (first_name, last_name, contact_number, email, address, dob) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (first, last, contact, email, address, dob))
        conn.commit()
        st.success("Guest registered successfully!")

# Book Room
def book_room():
    st.header("📅 Book Room")

    # Select guest
    cursor.execute("SELECT guest_id, first_name, last_name FROM Guests")
    guests = cursor.fetchall()
    guest_options = {f"{g[1]} {g[2]} (ID: {g[0]})": g[0] for g in guests}
    selected_guest = st.selectbox("Select Guest", list(guest_options.keys()))

    # Select room
    cursor.execute("SELECT room_id, room_number, room_type FROM Rooms WHERE room_status = 'Available'")
    rooms = cursor.fetchall()
    room_options = {f"{r[1]} - {r[2]} (ID: {r[0]})": r[0] for r in rooms}
    selected_room = st.selectbox("Select Room", list(room_options.keys()))

    check_in = st.date_input("Check-in Date", date.today())
    check_out = st.date_input("Check-out Date")

    if st.button("Confirm Booking"):
        guest_id = guest_options[selected_guest]
        room_id = room_options[selected_room]

        cursor.execute("""
            INSERT INTO Bookings (guest_id, room_id, check_in_date, check_out_date, booking_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (guest_id, room_id, check_in, check_out, "Booked"))

        cursor.execute("UPDATE Rooms SET room_status = 'Booked' WHERE room_id = %s", (room_id,))
        conn.commit()
        st.success("Room booked successfully!")

# View Bookings
def view_bookings():
    st.header("📋 All Bookings")
    query = """
        SELECT b.booking_id, CONCAT(g.first_name, ' ', g.last_name) AS Guest,
               r.room_number, b.check_in_date, b.check_out_date, b.booking_status
        FROM Bookings b
        JOIN Guests g ON b.guest_id = g.guest_id
        JOIN Rooms r ON b.room_id = r.room_id
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=["Booking ID", "Guest", "Room", "Check-in", "Check-out", "Status"])
    st.dataframe(df)

# Check-Out
def check_out():
    st.header("🚪 Check-Out Guest")

    cursor.execute("""
        SELECT b.booking_id, CONCAT(g.first_name, ' ', g.last_name) AS Guest
        FROM Bookings b
        JOIN Guests g ON b.guest_id = g.guest_id
        WHERE b.booking_status = 'Booked'
    """)
    bookings = cursor.fetchall()
    booking_options = {f"{b[1]} (Booking ID: {b[0]})": b[0] for b in bookings}

    if bookings:
        selected = st.selectbox("Select Booking to Check-Out", list(booking_options.keys()))
        method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Online"])
        if st.button("Confirm Check-Out"):
            booking_id = booking_options[selected]

            # Get booking cost
            cursor.execute("""
                SELECT r.price_per_night, DATEDIFF(b.check_out_date, b.check_in_date)
                FROM Bookings b
                JOIN Rooms r ON b.room_id = r.room_id
                WHERE b.booking_id = %s
            """, (booking_id,))
            price_per_night, nights = cursor.fetchone()
            total = price_per_night * nights

            cursor.execute("INSERT INTO Payments (booking_id, amount, payment_date, payment_method) VALUES (%s, %s, CURDATE(), %s)",
                           (booking_id, total, method))
            cursor.execute("UPDATE Bookings SET booking_status = 'Checked-Out' WHERE booking_id = %s", (booking_id,))
            cursor.execute("""
                UPDATE Rooms SET room_status = 'Available'
                WHERE room_id = (SELECT room_id FROM Bookings WHERE booking_id = %s)
            """, (booking_id,))
            conn.commit()
            st.success(f"Guest checked out. Payment Rs. {total} received via {method}")
    else:
        st.info("No active bookings found.")

# Payments Summary
def payments():
    st.header("💵 Payment Records")
    cursor.execute("""
        SELECT p.payment_id, b.booking_id, p.amount, p.payment_date, p.payment_method
        FROM Payments p
        JOIN Bookings b ON p.booking_id = b.booking_id
    """)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Payment ID", "Booking ID", "Amount (PKR)", "Date", "Method"])
    st.dataframe(df)

# Route Menu
if menu == "Register Guest":
    register_guest()
elif menu == "Book Room":
    book_room()
elif menu == "View Bookings":
    view_bookings()
elif menu == "Check-Out":
    check_out()
elif menu == "Payments":
    payments()
