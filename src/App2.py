import streamlit as st

st.set_page_config(page_title="App2", page_icon=":guardsman:")
st.title("FleetStat - Login ")

# ✅ Initialize session_state key before accessing it
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Login page 
def login():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "password":
            st.success("Login successful!")
            st.session_state['logged_in'] = True
        else:
            st.error("Invalid credentials")

# Main app logic
def main():
    if st.session_state['logged_in']:
        st.write("✅ Welcome to FleetStat!")
        # You can now add dashboard, charts, etc.
    else:
        login()

# ✅ Run the main logic
main()
