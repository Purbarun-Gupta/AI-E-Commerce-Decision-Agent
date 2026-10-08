import streamlit as st


def display_user_message(message):

    st.markdown(
        f"""
        <div class="chat-message user">

            <div class="chat-bubble user-bubble">
                {message}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def display_ai_message(message):

    st.markdown(
        f"""
        <div class="chat-message ai">

            <div class="chat-bubble ai-bubble">
                {message}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def display_chat_history(messages):

    for message in messages:

        role = message.get("role")

        content = message.get("content", "")

        if role == "user":

            display_user_message(content)

        else:

            display_ai_message(content)


def add_message(role, content):

    if "messages" not in st.session_state:

        st.session_state.messages = []

    st.session_state.messages.append(
        {
            "role": role,
            "content": content
        }
    )


def clear_chat():

    st.session_state.messages = []


def get_chat_input():

    return st.chat_input(
        "Ask me anything about your e-commerce business..."
    )


def display_suggested_questions(
    questions
):

    st.markdown(
        """
        <div class="suggestions-title">
            Try asking
        </div>
        """,
        unsafe_allow_html=True
    )

    columns = st.columns(2)

    for index, question in enumerate(questions):

        with columns[index % 2]:

            if st.button(
                question,
                use_container_width=True,
                key=f"suggestion_{index}"
            ):

                st.session_state.pending_question = question

                st.rerun()


def show_thinking():

    return st.spinner(
        "CommerceAI is thinking..."
    )


def get_recent_questions():

    return st.session_state.get(
        "recent_questions",
        []
    )