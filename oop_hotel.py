import streamlit as st
import pandas as pd
from datetime import date

# ----------------- Data Classes -------------------

class Guest:
    id_counter = 1
    def __init__(self, first_name, last_name, contact, email, address, dob):
        self.guest_id = Guest.id_counter
        Guest.id_counter += 1
        self.first_name = first_name
        self.last_name = last_name
        self.contact = contact
        self.email = email
        self.address = address
        self.dob = dob

class Room:
    def __init__(self, room_id, number, rtype, price):
        self.room_id = room_id
        self.number = number
        self.rtype = rtype
        self.price = price
        self.status = "Available"

class Booking:
    id_counter = 1
    def __init__(self, guest, room, check_in, check_out):
        self.booking_id = Booking.id_counter
        Booking.id_counter += 1
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.status = "Booked"

class Payment:
    id_counter = 1
    def __init__(self, booking, method):
        self.payment_id = Payment.id_counter
        Payment.id_counter += 1
        self.booking = booking
        self.method = method
        self.amount = (booking.check_out - booking.check_in).days * booking.room.price
        self.date = date.today()

# ----------------- Hotel Management System -------------------

class HotelManagementSystem:
    def __init__(self):
        self.guests = []
        self.rooms = [
            Room(1, "101", "Single", 5000),
            Room(2, "102", "Double", 7000),
            Room(3, "201", "Suite", 10000)
        ]
        self.bookings = []
        self.payments = []

    def register_guest(self, guest):
        self.guests.append(guest)

    def book_room(self, booking):
        booking.room.status = "Booked"
        self.bookings.append(booking)

    def check_out(self, booking_id, method):
        for booking in self.bookings:
            if booking.booking_id == booking_id and booking.status == "Booked":
                booking.status = "Checked-Out"
                booking.room.status = "Available"
                payment = Payment(booking, method)
                self.payments.append(payment)
                return payment
        return None

# ----------------- Initialize with session_state -------------------

if 'hotel' not in st.session_state:
    st.session_state.hotel = HotelManagementSystem()

hotel = st.session_state.hotel

# ----------------- Streamlit UI -------------------

st.set_page_config(page_title="Hotel Management", layout="centered")
st.title("🏨 Hotel Management System")

menu = st.sidebar.selectbox("Select Option", ["Register Guest", "Book Room", "View Bookings", "Check-Out", "Payments"])

# ----------------- Register Guest -------------------

if menu == "Register Guest":
    st.header("🧍 Register New Guest")
    f = st.text_input("First Name")
    l = st.text_input("Last Name")
    c = st.text_input("Contact Number")
    e = st.text_input("Email")
    a = st.text_area("Address")
    d = st.date_input("Date of Birth")

    if st.button("Register Guest"):
        g = Guest(f, l, c, e, a, d)
        hotel.register_guest(g)
        st.success("Guest registered successfully!")

# ----------------- Book Room -------------------

elif menu == "Book Room":
    st.header("📅 Book Room")
    if hotel.guests:
        guest_options = {f"{g.first_name} {g.last_name} (ID: {g.guest_id})": g for g in hotel.guests}
        selected_guest = st.selectbox("Select Guest", list(guest_options.keys()))

        available_rooms = [r for r in hotel.rooms if r.status == "Available"]
        if available_rooms:
            room_options = {f"{r.number} - {r.rtype} (ID: {r.room_id})": r for r in available_rooms}
            selected_room = st.selectbox("Select Room", list(room_options.keys()))

            check_in = st.date_input("Check-in Date", date.today())
            check_out = st.date_input("Check-out Date")

            if st.button("Confirm Booking"):
                g = guest_options[selected_guest]
                r = room_options[selected_room]
                b = Booking(g, r, check_in, check_out)
                hotel.book_room(b)
                st.success("Room booked successfully!")
        else:
            st.warning("No available rooms.")
    else:
        st.warning("Please register a guest first.")

# ----------------- View Bookings -------------------

elif menu == "View Bookings":
    st.header("📋 All Bookings")
    data = []
    for b in hotel.bookings:
        data.append([b.booking_id, f"{b.guest.first_name} {b.guest.last_name}", b.room.number,
                     b.check_in, b.check_out, b.status])
    df = pd.DataFrame(data, columns=["Booking ID", "Guest", "Room", "Check-in", "Check-out", "Status"])
    st.dataframe(df)

# ----------------- Check-Out -------------------

elif menu == "Check-Out":
    st.header("🚪 Check-Out Guest")
    active = [b for b in hotel.bookings if b.status == "Booked"]
    if active:
        options = {f"{b.guest.first_name} {b.guest.last_name} (Booking ID: {b.booking_id})": b.booking_id for b in active}
        selected = st.selectbox("Select Booking to Check-Out", list(options.keys()))
        method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Online"])
        if st.button("Confirm Check-Out"):
            payment = hotel.check_out(options[selected], method)
            if payment:
                st.success(f"Checked out. Payment Rs. {payment.amount} via {payment.method}")
            else:
                st.error("Check-out failed.")
    else:
        st.info("No active bookings found.")

# ----------------- Payment Records -------------------

elif menu == "Payments":
    st.header("💵 Payment Records")
    data = []
    for p in hotel.payments:
        data.append([p.payment_id, p.booking.booking_id, p.amount, p.date, p.method])
    df = pd.DataFrame(data, columns=["Payment ID", "Booking ID", "Amount (PKR)", "Date", "Method"])
    st.dataframe(df)
 