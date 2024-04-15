import streamlit as st
# import mysql.connector
import os
import json
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import base64
from streamlit_chat import message



load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


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
        action2 = st.sidebar.selectbox("Tools", ["PYQs","ExaBuddy","AIQPs"])

        if action2 == 'PYQs':
            pass

        # if action2 == 'f1':

        #     conn = mysql.connector.connect(
        #     host="localhost",
        #     user="root",
        #     password="tejas123",
        #     database="pyqs"
        #     )

        #     c = conn.cursor()

        #     c.execute(f'''CREATE TABLE IF NOT EXISTS dbms
        #                 (qid INTEGER PRIMARY KEY, module INTEGER, ques TEXT, dl INTEGER, rep INTEGER)''')
        #     conn.commit()

        #     def get_questions(subject , moduleno_filter=None, difficulty_filter=None, repetition_filter=None):
        #         query = f"SELECT * FROM {subject} WHERE 1=1"
        #         params = []
        #         if moduleno_filter is not None:
        #             query += " AND module = %s"
        #             params.append(moduleno_filter)
        #         if difficulty_filter:
        #             query += " AND dl = %s"
        #             params.append(difficulty_filter)
        #         if repetition_filter == "1 time":
        #             query += " AND rep = 1"
        #         elif repetition_filter == "2 times":
        #             query += " AND rep = 2"
        #         elif repetition_filter == "more than 3 times":
        #             query += " AND rep > 3"
        #         c.execute(query, params)
        #         return c.fetchall()


        #     # Display all questions
        #     st.subheader("Display all questions")

        #     # Filter options

        #     subject_filter = st.selectbox("Filter by Subject:", ["DBMS","AOA","MP"])
        #     moduleno_filter = st.selectbox("Filter by module:", [1,2])
        #     difficulty_filter = st.selectbox("Filter by Marks:", [5,7,10])
        #     repetition_filter = st.selectbox("Filter by repetition:", [1,2,3])

            
        #     # Button to apply filters
        #     if st.button("Apply Filters"):
        #         if difficulty_filter == 5:
        #             questions = get_questions(subject_filter,moduleno_filter,1, repetition_filter)
        #         elif difficulty_filter == 7:
        #             questions = get_questions(subject_filter,moduleno_filter,2, repetition_filter)
        #         else:
        #             questions = get_questions(subject_filter,moduleno_filter, 3, repetition_filter)
        #     else:
        #         questions = []
                



        #     # Display filtered questions
        #     for i,q in enumerate(questions):
        #         # st.write(q)
        #         st.write(f"Q.{i+1}) {q[2]} ")


        #     # Close connection to SQLite database
        #     conn.close()

        if action2 == 'ExaBuddy':

            # F2 functionality

            def initialize_session_state_chat():
                if 'history' not in st.session_state:
                    st.session_state['history'] = []

                if 'generated' not in st.session_state:
                    st.session_state['generated'] = ["Hello! Ask me anything about 🤗"]

                if 'past' not in st.session_state:
                    st.session_state['past'] = ["Hey! 👋"]

            def get_pdf_text(pdf_docs):
                text=""
                for pdf in pdf_docs:
                    pdf_reader= PdfReader(pdf)
                    for page in pdf_reader.pages:
                        text+= page.extract_text()
                return  text

            def get_text_chunks(text):
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
                chunks = text_splitter.split_text(text)
                return chunks

            def get_vector_store(text_chunks):
                embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
                vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
                vector_store.save_local("faiss_index")

            def get_conversational_chain():
                prompt_template = """
                consider context as syllabus and answer question asked on given syllabus, if the answer is not in
                provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
                Context:\n {context}?\n
                Question: \n{question}\n

                Answer:
                """

                model = ChatGoogleGenerativeAI(model="gemini-pro",
                                        temperature=0.3)

                prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
                chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

                return chain

            def user_input_chain(user_question,history):
                embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
                
                new_db = FAISS.load_local("faiss_index", embeddings,allow_dangerous_deserialization=True)
                docs = new_db.similarity_search(user_question)

                chain = get_conversational_chain()

                
                response = chain.invoke(
                    {"input_documents":docs, "question": user_question}
                    , return_only_outputs=True)
                history.append((user_question, response["output_text"]))

                return response["output_text"]



            initialize_session_state_chat()

            st.title("Document Processing")
            uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
        
            if st.button("Submit & Process"):
                raw_text = get_pdf_text(uploaded_files)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)  
                st.success("Done")



            reply_container = st.container()
            container = st.container()

            with container:
                with st.form(key='my_form', clear_on_submit=True):
                    user_input = st.text_input("Question:", placeholder="Questions About Syllabus :", key='input')
                    submit_button = st.form_submit_button(label='Send')

                if submit_button and user_input:
                    with st.spinner('Generating response...'):
                        output = user_input_chain(user_input, st.session_state['history'])

                    st.session_state['past'].append(user_input)
                    st.session_state['generated'].append(output)

                if st.button("clear"):
                    st.session_state['history'].clear()

            if st.session_state['generated']:
                    with reply_container:
                        for i in range(len(st.session_state['generated'])):
                            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                            message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")


        if action2 == "AIQPs":
            def get_pdf_text(pdf_docs):
                text=""
                for pdf in pdf_docs:
                    pdf_reader= PdfReader(pdf)
                    for page in pdf_reader.pages:
                        text+= page.extract_text()
                return  text

            def get_text_chunks(text):
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
                chunks = text_splitter.split_text(text)
                return chunks

            def get_vector_store(text_chunks):
                embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
                vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
                vector_store.save_local("faiss_index")

            def get_conversational_chain():
            #  Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
            #     provided context just say
                prompt_template = """
                consider context as syllabus and generate a question paper on it which contains Q1:MCQ Q2:short answers Q3:brief answers Q4:application based questions on given syllabus, if the answer is not in
                provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
                Context:\n {context}?\n
                Question: \n{question}\n

                Answer:
                """

                model = ChatGoogleGenerativeAI(model="gemini-pro",
                                        temperature=0.3)

                prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
                chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

                return chain

            def user_input_chain():
                embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
                
                user_question = "generate a question paper"
                new_db = FAISS.load_local("faiss_index", embeddings,allow_dangerous_deserialization=True)
                docs = new_db.similarity_search(user_question)

                chain = get_conversational_chain()

                
                response = chain.invoke(
                    {"input_documents":docs, "question": user_question}
                    , return_only_outputs=True)
                
                return response["output_text"]




            st.title("AIQPs")
            uploaded_files1 = st.file_uploader("Upload files", accept_multiple_files=True)

            if st.button("Submit & Process"):
                raw_text = get_pdf_text(uploaded_files1)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)  
                st.success("Done")

                reply_container = st.container()

                with reply_container:
                    output = user_input_chain()
                    st.markdown(output)


if __name__ == "__main__":
    main()