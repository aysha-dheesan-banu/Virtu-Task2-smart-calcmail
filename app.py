import streamlit as st
import smtplib
from email.message import EmailMessage
import sqlite3
from streamlit_option_menu import option_menu

# --- Background and Page Config ---
st.set_page_config(page_title="SmartCalcMail", layout="wide")

page_bg = """
<style>
body {
background: linear-gradient(to right, #d4fc79, #96e6a1);
}
[data-testid="stSidebar"] {
background-image: linear-gradient(to bottom, #11998e, #38ef7d);
color: white;
}
h1, h2, h3, h4 {
color: #2c3e50;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# --- Database setup ---
conn = sqlite3.connect('calculator_history.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS history (operation TEXT, result TEXT)''')
conn.commit()

# --- Navigation Menu ---
with st.sidebar:
    selected = option_menu(
        menu_title="SmartCalcMail Hub",
        options=["📬 Email Sender", "🧠 Calculator"],
        icons=["envelope", "calculator"],
        menu_icon="rocket",
        default_index=0,
    )

# --- Email Function ---
def send_email(sender, app_password, receiver, subject, body, attachment=None):
    try:
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.set_content(body)

        if attachment is not None:
            file_data = attachment.read()
            file_name = attachment.name
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, app_password)
            smtp.send_message(msg)

        st.success("✅ Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        st.error("❌ Authentication failed: Use an App Password instead of your Gmail password.")
        st.info("🔒 Generate one here: https://myaccount.google.com/apppasswords")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")

# --- Calculator Function ---
def calculate(num1, num2, operation):
    try:
        if operation == "Add":
            result = num1 + num2
        elif operation == "Subtract":
            result = num1 - num2
        elif operation == "Multiply":
            result = num1 * num2
        elif operation == "Divide":
            if num2 == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            result = num1 / num2
        else:
            raise ValueError("Invalid operation.")

        explanation = f"{num1} {operation} {num2} = {round(result, 2)}"
        c.execute("INSERT INTO history (operation, result) VALUES (?, ?)", (f"{num1} {operation} {num2}", str(result)))
        conn.commit()

        return round(result, 2), explanation
    except Exception as e:
        return f"Error: {e}", None

# --- Email Sender UI ---
if selected == "📬 Email Sender":
    st.markdown("## 💌 Send an Email with Ease")
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            sender_email = st.text_input("📤 Sender Gmail")
            sender_password = st.text_input("🔑 App Password", type="password")
            receiver_email = st.text_input("📥 Receiver Email")
            subject = st.text_input("✉️ Subject")

        with col2:
            body = st.text_area("📝 Message Body", height=150)
            file = st.file_uploader("📎 Upload Attachment", type=["txt", "pdf", "png", "jpg", "jpeg", "csv"])

    if st.button("🚀 Send Email"):
        if sender_email and sender_password and receiver_email:
            send_email(sender_email, sender_password, receiver_email, subject, body, file)
        else:
            st.warning("⚠️ Please fill in all required fields.")

    with st.expander("❓ How to Generate an App Password"):
        st.markdown("""
        1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
        2. Choose 'Mail' as the app and 'Other' as the device.
        3. Copy the generated password and paste it above.
        """)

# --- Calculator UI ---
if selected == "🧠 Calculator":
    st.markdown("## 🔢 Smart Calculator with History")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            num1 = st.number_input("🔹 Enter First Number", format="%.2f")
        with col2:
            num2 = st.number_input("🔸 Enter Second Number", format="%.2f")

        operation = st.selectbox("⚙️ Choose Operation", ["Add", "Subtract", "Multiply", "Divide"])

        if st.button("📲 Calculate"):
            result, explanation = calculate(num1, num2, operation)
            st.success(f"✅ Result: {result}")
            if explanation:
                st.info(f"🧠 Explanation: {explanation}")

    with st.expander("📜 View History"):
        c.execute("SELECT * FROM history ORDER BY rowid DESC LIMIT 10")
        rows = c.fetchall()
        if rows:
            for op, res in rows:
                st.markdown(f"🔍 `{op}` = **{res}**")
        else:
            st.info("No calculations yet.")

# Footer
st.markdown("---")
st.caption("🚀 Created with ❤️ using Streamlit | SmartCalcMail Hub")








