import streamlit as st
import sqlite3
import pandas as pd
conn=sqlite3.connect('railway.db')
current_page='login or Sign up'
c=conn.cursor()
def create_db():
    c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT,password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS employees (employee_id TEXT,password TEXT,designation TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS trains (train_number TEXT ,train_name TEXT ,start_destination TEXT,end_destination TEXT)")
    create_db()
def search_train(train_number):
    train_query=c.execute(" SELECT * FROM trains WHERE train_number=?",(train_number))
    train_data=train_query.fetchone()
    return train_data 
def train_destination(start_destination,end_destination):
    train_query=c.execute(" SELECT * FROM trains WHERE start_destination=?,end_destination=?",(start_destination,end_destination))
    train_data=train_query.fetchone()
    return train_data
def add_train(train_number, train_name, departure_date, start_destination, end_destination):
    train_query = c.execute("INSERT INTO trains (train_number, train_name, departure_date, start_destination, end_destination) VALUES (?, ?, ?, ?, ?)",
                            (train_number, train_name, departure_date, start_destination, end_destination))
    conn.commit()
def create_seat_table(train_number):
    c.execute(f'''CREATE TABLE IF NOT EXISTS seats_{train_number} (
                    seat_number INTEGER PRIMARY KEY,
                    seat_type TEXT,
                    booked INTEGER,
                    passenger_name TEXT,
                    passenger_age INTEGER,
                    passenger_gender TEXT
                )''')
    for i in range(1, 51):
        val = categorize_seat(i)  # Assuming you have a function called categorize_seat
        c.execute(f'''INSERT INTO seats_{train_number} (seat_number, seat_type, booked, passenger_name, passenger_age, passenger_gender)
                      VALUES (?, ?, ?, ?, ?, ?)''', (i, val, 0, '', 0, ''))  # Adjust the default values as needed
        conn.commit()
def allocate_next_available_seat(train_number,seat_type):
    seat_query=c.execute(f"SELECT seat_number FROM seat_{train_number} WHERE booked=0 and seat_type=?"
                        f"ORDER BY seat_number asc",(seat_type))
    result=seat_query.fetchall()
    if result:
        return[0]
            
def categorize_seat(seat_number):
    if(seat_number % 10) in [0,4,5,9]:
        return "Window"
    elif(seat_number % 10) in [2,3,6,7]:
        return "Aisle"
    else:
        return "Middle"
def view_seats(train_number):
    train_query=c.execute("SELECT * FROM trains WHERE train_number=?",(train_number))
    train_data=train_query.fetchone()

    if train_data:
        seat_query=c.execute(f'''SELECT 'Number:'||seat_number,\n Type:'||seat_type,'\n
        Name:'||passanger_name,'\n Age:'passanger_Age,'\nGender'||passanger_gender as Details,booked FROM seats_{train_number}
        ORDER BY seat_number asc ''')

    result-seat_query.fetchall()

    if result:
       st.dataframe(data=result)

def book_tickets (train_number , passenger_name, passenger_gender, passenger_age, seat_type):
    train_query=c.execute("SELECT * FROM trains WHERE train_number =?  ",(train_number,)) 
    train_data=train_query.fetchone()
    if train_data:
       seat_number=allocate_next_available_seat(train_number, seat_type)
       if seat_number:
          c.execute("UPDATE seats_{train_number} SET booked =1, seat_type=?, passenger_name=?, passenger_age=?, passenger_gender=?" f"WHERE seat_number=?" , (seat_type, passenger_name, passenger_age, passenger_gender, seat_number[0]))
          conn.commit()
          st.success("BOOKED SUCCESSFULLY!!")   
def cancel_tickets(train_number, seat_number):
    train_query = c.execute("SELECT * FROM trains WHERE train_number = ?", (train_number,))
    train_data = train_query.fetchone()
    if train_data:
        c.execute(f'''UPDATE seats_{train_number} SET booked = 0, passenger_name = '', passenger_age = '', passenger_gender = ''
                      WHERE seat_number = ?''', (seat_number,))
        conn.commit()
        st.success("TICKET CANCELED SUCCESSFULLY")
def train_functions():
    st.title("Train Administrator")
    functions = st.sidebar.selectbox(
        "Select train functions",
        ["Add train", "View trains", "Search train", "Delete train", "Book ticket", "Cancel ticket", "View seats"]
    )

    if functions == "Add train":
        st.header("Add New Train")
        with st.form(key='new_train_details'):
            train_number = st.text_input("Train Number")
            train_name = st.text_input("Train Name")
            departure_date = st.text_input("Date")
            start_destination = st.text_input("Start Destination")
            end_destination = st.text_input("End Destination")
            submitted = st.form_submit_button("Add Train")
            if submitted and train_name != "" and train_number != "" and start_destination != "" and end_destination != "":
                add_train(train_number, train_name, departure_date, start_destination, end_destination)
                st.success("Train added successfully")

    elif functions == "Book ticket":
        st.title("Book Train Ticket")
        train_number = st.text_input("Enter Train Number")
        seat_type = st.selectbox("Seat Type", ["Aisle", "Middle", "Window"], index=0)
        passenger_name = st.text_input("Passenger Name")
        passenger_age = st.number_input("Passenger Age", min_value=1)
        passenger_gender = st.selectbox("Passenger Gender", ["Male", "Female"], index=0)
        if st.button("Book Ticket"):
            if train_number and passenger_name and passenger_gender and passenger_age:
                book_tickets(train_number, passenger_name, passenger_gender, passenger_age, seat_type)
                st.success("Ticket booked successfully")

    elif functions == "Cancel ticket":
        st.title("Cancel Ticket")
        train_number = st.text_input("Enter Train Number")
        seat_number = st.number_input("Enter Seat Number", min_value=1)
        if st.button("Cancel Ticket"):
            if train_number and seat_number:
                cancel_tickets(train_number, seat_number)
                st.success("Ticket cancelled successfully")

    elif functions == "View seats":
        st.title("View Seats")
        train_number = st.text_input("Enter Train Number")
        if st.button("Submit"):
            if train_number:
                view_seats(train_number)

    elif functions == "Delete train":
        st.title("Delete Train")
        train_number = st.text_input("Enter Train Number")
        departure_date = st.date_input("Enter Date")
        if st.button("Delete Train"):
            if train_number:
                delete_train(train_number, departure_date)
                st.success("Train deleted successfully")

train_functions()        
