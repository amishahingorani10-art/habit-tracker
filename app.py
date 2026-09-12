import streamlit as st
import database as db
import calendar
from datetime import date


def render_month_calendar(habit_id, created_date_str):
    today = date.today()
    year, month = today.year, today.month
    created_date = date.fromisoformat(created_date_str) if created_date_str else today

    completed_days = db.get_month_completions(habit_id, year, month)
    first_weekday, days_in_month = calendar.monthrange(year, month)

    st.write(f"**{calendar.month_name[month]} {year}**")

    header_cols = st.columns(7)
    for i, day_label in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
        header_cols[i].markdown(f"<div style='text-align:center'>{day_label}</div>", unsafe_allow_html=True)

    day_number = 1
    while day_number <= days_in_month:
        week_cols = st.columns(7)
        for weekday in range(7):
            if day_number == 1 and weekday < first_weekday:
                week_cols[weekday].write("")
            elif day_number > days_in_month:
                week_cols[weekday].write("")
            else:
                this_date = date(year, month, day_number)
                if day_number in completed_days:
                    dot = "🟢"
                elif this_date < created_date:
                    dot = "⚪"
                elif this_date < today:
                    dot = "🔴"
                else:
                    dot = "⚪"

                week_cols[weekday].markdown(
                    f"<div style='text-align:center; line-height:1.2;'>"
                    f"<span style='font-size:0.8rem;'>{day_number}</span><br>"
                    f"<span style='font-size:0.5rem;'>{dot}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                day_number += 1


st.set_page_config(page_title="Habit Tracker", page_icon="🔥", layout="centered")
db.init_db()
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #FAF7F2;
}

h1 {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    color: #2B2620;
    letter-spacing: -0.5px;
}

div[data-testid="stMarkdownContainer"] p {
    color: #2B2620;
    font-size: 1rem;
}

/* Streak text is now the 3rd column */
div[data-testid="column"]:nth-of-type(3) div[data-testid="stMarkdownContainer"] p {
    color: #C98A3E;
    font-weight: 600;
}

input[type="checkbox"] {
    accent-color: #FCE4EC;
    transform: scale(1.3);
}

.stTextInput input {
    border-radius: 8px;
    border: 1px solid #DDD6C9;
    padding: 10px;
    background-color: #FFFFFF;
}

button[kind="primaryFormSubmit"], .stFormSubmitButton button {
    background-color: #FCE4EC;
    color: #8E4F63;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}

.stFormSubmitButton button:hover {
    background-color: #F9C9D6;
}

button[kind="secondary"] {
    background-color: #FFFFFF;
    color: #B8493D;
    border: 1px solid #B8493D;
    border-radius: 8px;
}

div[data-testid="stExpander"] {
    border: 1px solid #DDD6C9;
    border-radius: 10px;
    background-color: #FFFFFF;
}
div[data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 0.5rem;
}
div[data-testid="stMarkdownContainer"] p {
    margin: 0;
}

hr {
    border-color: #DDD6C9;
}

div[data-testid="column"] div[data-testid="stMarkdownContainer"] div {
    font-size: 0.85rem;
    color: #6B6355;
    padding: 4px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; padding: 10px 0 20px 0;'>
    <div style='font-size: 2.5rem;'>📋</div>
    <h1 style='margin-bottom: 0;'>My Habits</h1>
    <p style='color:#8A8272; font-size:0.95rem; margin-top:4px;'>
        Small steps, tracked daily.
    </p>
</div>
""", unsafe_allow_html=True)
with st.form("add_habit_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    with col1:
        new_habit = st.text_input(
            "Add a new habit", placeholder="e.g. Drink water", label_visibility="collapsed"
        )
    with col2:
        submitted = st.form_submit_button("+ Add", use_container_width=True)

    if submitted and new_habit.strip():
        db.add_habit(new_habit.strip())
        st.rerun()

st.divider()

habits = db.get_all_habits()

if not habits:
    st.info("No habits yet — add one above to get started!")
else:
    for habit in habits:
        done_today = db.is_done_today(habit["last_done"])

        col1, col2, col3 = st.columns([0.2, 4, 2])

        with col1:
            checked = st.checkbox(
                "Done", value=done_today, key=f"check_{habit['id']}", label_visibility="collapsed"
            )

        with col2:
            st.write(f"**{habit['name']}**")

        with col3:
            st.write(f"🔥 {habit['streak']} ")

        if checked and not done_today:
            db.mark_done(habit["id"], habit["last_done"], habit["streak"])
            st.rerun()
        elif not checked and done_today:
            db.unmark_today(habit["id"], habit["last_done"], habit["streak"])
            st.rerun()

        with st.expander(f"📅 View {habit['name']}'s calendar"):
            render_month_calendar(habit["id"], habit["created_date"])

    st.divider()

    with st.expander("🗑️ Remove a habit"):
        habit_names = {h["name"]: h["id"] for h in habits}
        to_delete = st.selectbox("Choose a habit to remove", options=list(habit_names.keys()))
        if st.button("Delete", type="secondary"):
            db.delete_habit(habit_names[to_delete])
            st.rerun()

st.caption("Data is saved locally in habits.db — it'll still be here next time you open the app.")
st.markdown("""
<div style='text-align:center; padding: 30px 0 10px 0; color:#B5AC9C; font-size:0.8rem;'>
    Built with 🩷 using Streamlit & SQLite
</div>
""", unsafe_allow_html=True)