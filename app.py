import streamlit as st
import database as db
import calendar
from datetime import date

def render_month_calendar(habit_id):
    today = date.today()
    year, month = today.year, today.month

    completed_days = db.get_month_completions(habit_id, year, month)

    # first_weekday: 0=Monday ... 6=Sunday, days_in_month: e.g. 30
    first_weekday, days_in_month = calendar.monthrange(year, month)

    st.write(f"**{calendar.month_name[month]} {year}**")

    # Weekday headers
    header_cols = st.columns(7)
    for i, day_label in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
        header_cols[i].markdown(f"<div style='text-align:center'>{day_label}</div>", unsafe_allow_html=True)

    # Build the grid: blank spaces before day 1, then each day
    day_number = 1
    while day_number <= days_in_month:
        week_cols = st.columns(7)
        for weekday in range(7):
            if day_number == 1 and weekday < first_weekday:
                week_cols[weekday].write("")  # blank before month starts
            elif day_number > days_in_month:
                week_cols[weekday].write("")  # blank after month ends
            else:
                this_date = date(year, month, day_number)
                if day_number in completed_days:
                    dot = "🟢"
                elif this_date < today:
                    dot = "🔴"
                else:
                    dot = "⚪"  # today or future, not decided yet
                week_cols[weekday].markdown(
                    f"<div style='text-align:center'>{dot}<br>{day_number}</div>",
                    unsafe_allow_html=True,
                )
                day_number += 1

st.set_page_config(page_title="Habit Tracker", page_icon="🔥", layout="centered")
db.init_db()

st.title("📋 My Habits") 
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

        col1, col2, col3 = st.columns([5, 2, 1])

        with col1:
            st.write(f"**{habit['name']}**")

        with col2:
            st.write(f"🔥 {habit['streak']} day streak")

        with col3:
            checked = st.checkbox(
                "Done", value=done_today, key=f"check_{habit['id']}", label_visibility="collapsed"
            )
        if checked and not done_today:
            db.mark_done(habit["id"], habit["last_done"], habit["streak"])
            st.rerun()
        elif not checked and done_today:
            db.unmark_today(habit["id"], habit["last_done"], habit["streak"])
            st.rerun()
        with st.expander(f"📅 View {habit['name']}'s calendar"):
            render_month_calendar(habit["id"])    
