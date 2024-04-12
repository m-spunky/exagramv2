import streamlit as st
import mysql.connector
import os
import json



# Profile Authentication
def save_credentials(credentials):
    with open("credentials.txt", "w") as f:
        json.dump(credentials, f)

def load_credentials():
    try:
        with open("credentials.txt", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def login(credentials, username, password):
    saved_password = credentials.get(username)
    if saved_password == password:
        return True
    else:
        return False

def signup(credentials, username, password):
    if username not in credentials:
        credentials[username] = password
        save_credentials(credentials)
        return True
    else:
        return False









# Streamlit app
def main():
    st.set_page_config('Exagram')
   
    st.title("Exagram 🌐")
    # st.image('logoh-transformed.png')
    st.sidebar.header("MENU")

    # Initialize session state
    if 'user_credentials' not in st.session_state:
        st.session_state.user_credentials = load_credentials()

    action = st.sidebar.selectbox("Choose Action", ["Login", "Sign-up"])
    
    if action == "Login":
       
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if login(st.session_state.user_credentials, username, password):
                st.subheader(f"Welcome {username}")
                
                st.sidebar.success("Login Successful")
                st.session_state.logged_in = True
            else:
                st.sidebar.error("Invalid Credentials")

    elif action == "Sign-up":
        st.session_state.logged_in = False
        st.sidebar.subheader("Sign-up")
        new_username = st.sidebar.text_input("New Username")
        new_password = st.sidebar.text_input("New Password", type="password")
        if st.sidebar.button("Sign-up"):
            if signup(st.session_state.user_credentials, new_username, new_password):
                st.sidebar.success("Sign-up Successful")
            else:
                st.sidebar.error("Username already exists")

    # Show content if logged in
    if st.session_state.get('logged_in'):
        st.sidebar.header("Dashboard")
        action2 = st.sidebar.selectbox("Tools", ["f1","f2"])

        if action2 == 'f1':

            conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="tejas123",
            database="pyqs"
            )

            c = conn.cursor()

            c.execute(f'''CREATE TABLE IF NOT EXISTS dbms
                        (qid INTEGER PRIMARY KEY, module INTEGER, ques TEXT, dl INTEGER, rep INTEGER)''')
            conn.commit()

            def get_questions(subject , moduleno_filter=None, difficulty_filter=None, repetition_filter=None):
                query = f"SELECT * FROM {subject} WHERE 1=1"
                params = []
                if moduleno_filter is not None:
                    query += " AND module = %s"
                    params.append(moduleno_filter)
                if difficulty_filter:
                    query += " AND dl = %s"
                    params.append(difficulty_filter)
                if repetition_filter == "1 time":
                    query += " AND rep = 1"
                elif repetition_filter == "2 times":
                    query += " AND rep = 2"
                elif repetition_filter == "more than 3 times":
                    query += " AND rep > 3"
                c.execute(query, params)
                return c.fetchall()


            # Display all questions
            st.subheader("Display all questions")

            # Filter options

            subject_filter = st.selectbox("Filter by Subject:", ["DBMS","AOA","MP"])
            moduleno_filter = st.selectbox("Filter by module:", [1,2])
            difficulty_filter = st.selectbox("Filter by Marks:", [5,7,10])
            repetition_filter = st.selectbox("Filter by repetition:", [1,2,3])

            
            # Button to apply filters
            if st.button("Apply Filters"):
                if difficulty_filter == 5:
                    questions = get_questions(subject_filter,moduleno_filter,1, repetition_filter)
                elif difficulty_filter == 7:
                    questions = get_questions(subject_filter,moduleno_filter,2, repetition_filter)
                else:
                    questions = get_questions(subject_filter,moduleno_filter, 3, repetition_filter)
            else:
                questions = []
                



            # Display filtered questions
            for i,q in enumerate(questions):
                # st.write(q)
                st.write(f"Q.{i+1}) {q[2]} ")


            # Close connection to SQLite database
            conn.close()

        if action2 == 'f2':
            pass


if __name__ == "__main__":
    main()
