
import streamlit as st
import pandas as pd
import random
import json
from io import BytesIO

# Constants
DATA_FILE = "grammar_structures_translated.xlsx"
USERS_FILE = "users.json"

st.set_page_config(page_title="B2 Grammar Trainer", layout="centered")

def load_data():
    return pd.read_excel(DATA_FILE)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def show_flashcards(df):
    st.header("Flashcards")
    idx = st.session_state.get("flashcard_idx", 0)
    if idx >= len(df):
        st.success("You have reviewed all flashcards!")
        if st.button("Restart Flashcards"):
            st.session_state["flashcard_idx"] = 0
        return

    row = df.iloc[idx]
    st.markdown(f"### Spanish: {row['Spanish']}")
    if st.button("Show English"):
        st.markdown(f"**English:** {row['English Affirmative']}")
        st.markdown(f"**Grammatical Structure:** {row['Grammatical Structure']}")

    if st.button("Next"):
        st.session_state["flashcard_idx"] = idx + 1

def quiz(df):
    st.header("Grammar Quiz")
    questions = st.session_state.get("questions", [])
    current = st.session_state.get("current_q", 0)
    score = st.session_state.get("score", 0)

    if not questions:
        # Generate 5 random questions
        questions = random.sample(list(df.index), 5)
        st.session_state["questions"] = questions
        st.session_state["current_q"] = 0
        st.session_state["score"] = 0
        current = 0
        score = 0

    idx = questions[current]
    row = df.iloc[idx]

    st.markdown(f"**Question {current+1} of 5:** What is the grammatical structure in English of this sentence?")
    st.markdown(f"Spanish sentence: *{row['Spanish']}*")

    options = [
        row['Grammatical Structure'],
        "Subject + Verb",
        "Verb + Object",
        "Simple Sentence",
        "Complex Sentence"
    ]
    random.shuffle(options)
    answer = st.radio("Choose the correct grammatical structure:", options, key=f"q{current}")

    if st.button("Submit Answer"):
        if answer == row['Grammatical Structure']:
            st.success("Correct!")
            st.session_state["score"] = score + 1
        else:
            st.error(f"Wrong! Correct answer: {row['Grammatical Structure']}")

        st.session_state["current_q"] = current + 1

        if current + 1 >= 5:
            st.balloons()
            st.success(f"Quiz finished! Your score: {st.session_state['score']}/5")
            # Save score to users
            user = st.session_state.get("user", "Anonymous")
            users = load_users()
            if user not in users or st.session_state["score"] > users.get(user, 0):
                users[user] = st.session_state["score"]
                save_users(users)
            # Clear quiz state
            st.session_state["questions"] = []
            st.session_state["current_q"] = 0
            st.session_state["score"] = 0
            if st.button("Restart Quiz"):
                st.experimental_rerun()
        else:
            st.experimental_rerun()

def show_ranking():
    st.header("Ranking")
    users = load_users()
    sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)
    for i, (user, score) in enumerate(sorted_users):
        st.write(f"{i+1}. **{user}** - Score: {score}/5")

def main():
    st.title("B2 Grammar Trainer - Interactive App")

    df = load_data()

    # User input - no registration needed
    user = st.text_input("Enter your username (no registration):")
    if user.strip():
        st.session_state["user"] = user.strip()
    else:
        user = st.session_state.get("user", "Anonymous")

    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Go to:", ["Flashcards", "Quiz", "Ranking", "Download Data"])

    if menu == "Flashcards":
        show_flashcards(df)
    elif menu == "Quiz":
        quiz(df)
    elif menu == "Ranking":
        show_ranking()
    elif menu == "Download Data":
        st.header("Download grammar data")
        towrite = BytesIO()
        df.to_excel(towrite, index=False)
        towrite.seek(0)
        st.download_button(label="Download Excel file", data=towrite, file_name="grammar_structures_translated.xlsx")

if __name__ == "__main__":
    main()
    