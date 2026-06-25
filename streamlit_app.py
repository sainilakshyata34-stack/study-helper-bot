import streamlit as st
from google import genai
from pypdf import PdfReader
st.set_page_config(
    page_title="Study Helper Bot",
    page_icon="📚",
    layout="wide"
)
st.info("""
🚀 Free Mode:
Using the app's shared API key.
Questions may be limited if the shared quota is exhausted.

🔑 Personal API Key Mode:
Enter your own Gemini API key for higher usage limits.
""")

user_key = st.text_input(
    "Enter your Gemini API Key (Optional)",
    type="password"
)

if user_key:
    api_key = user_key
else:
    api_key = st.secrets["GEMINI_API_KEY"]  # your shared key

client = genai.Client(api_key=api_key)


# Page Settings
# =========================
st.set_page_config(
    page_title="Study Helper Bot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Study Helper Bot")
st.caption("AI-powered Study Assistant")

# =========================
# PDF Upload
# =========================
uploaded_file = st.file_uploader(
    "📄 Upload PDF Notes",
    type=["pdf"]
)

pdf_text = ""

if uploaded_file:
    try:
        reader = PdfReader(uploaded_file)

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text

        st.success("✅ PDF uploaded successfully!")

    except Exception as e:
        st.error(f"PDF Error: {e}")

# =========================
# Session State
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.header("⚙️ Settings")

    mode = st.selectbox(
        "Choose Mode",
        [
            "Ask Question",
            "Notes Generator",
            "Quiz Generator",
            "Study Planner"
        ]
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# =========================
# Display Chat History
# =========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# Chat Input
# =========================
user_input = st.chat_input("Type your question here...")

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # =========================
    # Mode Prompts
    # =========================

    if mode == "Ask Question":
        prompt = f"""
        Answer clearly and simply:

        {user_input}
        """

    elif mode == "Notes Generator":
        prompt = f"""
        Create detailed study notes on:

        {user_input}

        Include:
        - Definitions
        - Key Concepts
        - Important Points
        - Summary
        """

    elif mode == "Quiz Generator":
        prompt = f"""
        Create a quiz on:

        {user_input}

        Include:
        - 10 MCQs
        - 4 options each
        - Correct answers
        """

    elif mode == "Study Planner":
        prompt = f"""
        Create a study plan for:

        {user_input}

        Include:
        - Daily goals
        - Weekly goals
        - Revision plan
        - Productivity tips
        """

    # =========================
    # PDF Integration
    # =========================

    if uploaded_file and pdf_text.strip():
        prompt = f"""
        Use the uploaded PDF to answer.

        PDF Content:
        {pdf_text[:10000]}

        User Request:
        {prompt}
        """

    # =========================
    # Gemini Response
    # =========================

    try:

        with st.chat_message("assistant"):

            with st.spinner("🤖 Thinking..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                answer = response.text

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

    except Exception as e:

        error_text = str(e)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            st.error(
                "⚠️ Gemini API quota exceeded. Please wait or use another API key."
            )
        else:
            st.error(f"Error: {error_text}")
