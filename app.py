import streamlit as st
import sqlite3
import os
import datetime
import time
import pandas as pd

# ---------- Page Config ----------
st.set_page_config(page_title="AI ADHD Companion", page_icon="🧠", layout="wide")

# ---------- Database Path ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "adhd.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

# ---------- Database Initialization ----------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        task TEXT,
                        status TEXT,
                        priority TEXT,
                        created_date TEXT
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS focus_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        duration INTEGER
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS task_quiz_scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task TEXT,
                        score INTEGER,
                        date TEXT
                    )""")
    conn.commit()
    conn.close()

init_db()

# ---------- Task Functions ----------
def add_task(task_text, priority):
    conn = get_connection()
    cursor = conn.cursor()
    date = str(datetime.date.today())
    cursor.execute("INSERT INTO tasks (user_id, task, status, priority, created_date) VALUES (?,?,?,?,?)",
                   (1, task_text, "Pending", priority, date))
    conn.commit()
    conn.close()

def get_tasks(filter=None):
    conn = get_connection()
    cursor = conn.cursor()
    if filter in ["Pending","Completed"]:
        cursor.execute("SELECT task,status,priority,created_date FROM tasks WHERE status=?", (filter,))
    else:
        cursor.execute("SELECT task,status,priority,created_date FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task_status(task, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status=? WHERE task=?", (new_status, task))
    conn.commit()
    conn.close()

def delete_task(task):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE task=?", (task,))
    conn.commit()
    conn.close()

# ---------- Focus Timer ----------
def log_focus_time(minutes):
    conn = get_connection()
    cursor = conn.cursor()
    date = str(datetime.date.today())
    cursor.execute("INSERT INTO focus_log (date, duration) VALUES (?,?)", (date, minutes))
    conn.commit()
    conn.close()

def get_focus_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date,SUM(duration) FROM focus_log GROUP BY date")
    data = cursor.fetchall()
    conn.close()
    return data

# ---------- Progress ----------
def get_progress_data():
    tasks = get_tasks()
    total = len(tasks)
    completed = sum(1 for t in tasks if t[1]=="Completed")
    pending = total - completed
    return total, completed, pending

def get_motivation_message(score):
    if score>=90:
        return "🔥 Excellent! Keep going!"
    elif score>=70:
        return "💪 Great job! Stay consistent!"
    elif score>=40:
        return "🙂 Good start!"
    elif score>0:
        return "⚡ Small wins matter!"
    else:
        return "🚀 Let's start today!"

# ---------- Sidebar Navigation ----------
page = st.sidebar.selectbox("Navigate to:", ["🏠 Dashboard","📋 Tasks","⏱️ Focus Timer","📝 MCQ Quiz","💾 Export/Reports"])

# ---------- Pages ----------

# --- Dashboard ---
if page=="🏠 Dashboard":
    st.title("🧠 AI ADHD Companion Dashboard")
    st.subheader("📊 Progress Overview")

    total, completed, pending = get_progress_data()
    if total > 0:
        progress_percent = int((completed / total) * 100)
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Completed Tasks", completed, delta=f"{progress_percent}%")
        col2.metric("⏳ Pending Tasks", pending)
        col3.metric("🔥 Focus Score", f"{progress_percent}%")

        # Animated progress bar
        progress_bar = st.progress(0)
        for i in range(progress_percent+1):
            progress_bar.progress(i)
            time.sleep(0.01)

        st.info(get_motivation_message(progress_percent))
        if progress_percent == 100:
            st.balloons()
    else:
        st.write("No tasks yet! Start adding tasks to track your focus.")

# --- Tasks ---
elif page=="📋 Tasks":
    st.title("📋 Task Management")
    task_input = st.text_input("Enter your task")
    priority = st.selectbox("Select Priority", ["Low","Medium","High"])
    if st.button("Add Task"):
        if task_input:
            add_task(task_input, priority)
            st.success("Task Added!")
            st.rerun()

    filter_option = st.selectbox("Filter Tasks", ["All","Completed","Pending"])
    tasks = get_tasks(filter_option if filter_option!="All" else None)
    if tasks:
        for task,status,prio,created in tasks:
            color = "#8fd694" if prio=="Low" else "#f7d060" if prio=="Medium" else "#f56c6c"
            st.markdown(
                f"<div style='background-color:{color};padding:15px;border-radius:15px;margin-bottom:10px;'>"
                f"<b>{task}</b><br>Status: {status}<br>Priority: {prio}<br>Created: {created}</div>",
                unsafe_allow_html=True
            )
            c1,c2 = st.columns([1,1])
            if c1.button("Done", key=task+"_done"):
                update_task_status(task,"Completed")
                st.rerun()
            if c2.button("Delete", key=task+"_delete"):
                delete_task(task)
                st.rerun()
    else:
        st.write("No tasks found.")

# --- Focus Timer ---
elif page=="⏱️ Focus Timer":
    st.title("⏱️ Focus Timer")
    focus_minutes = st.number_input("Set Focus Time (minutes)", 1,120,25)
    if "timer_running" not in st.session_state:
        st.session_state.timer_running=False
    if "time_left" not in st.session_state:
        st.session_state.time_left=focus_minutes*60

    col1,col2=st.columns(2)
    if col1.button("Start Focus Session"):
        st.session_state.timer_running=True
        st.session_state.time_left=focus_minutes*60
    if col2.button("Reset Timer"):
        st.session_state.timer_running=False
        st.session_state.time_left=focus_minutes*60

    if st.session_state.timer_running:
        mins=st.session_state.time_left//60
        secs=st.session_state.time_left%60
        color="red" if st.session_state.time_left<300 else "#8fd694"
        st.markdown(f"<h1 style='color:{color};'>{mins:02d}:{secs:02d}</h1>",unsafe_allow_html=True)
        time.sleep(1)
        st.session_state.time_left-=1
        if st.session_state.time_left<=0:
            st.success("🎉 Focus Session Completed!")
            log_focus_time(focus_minutes)
            st.balloons()
            st.session_state.timer_running=False
        st.rerun()

    # Weekly Focus Chart
    st.subheader("📈 Weekly Focus Analytics")
    focus_data=get_focus_data()
    if focus_data:
        df=pd.DataFrame(focus_data,columns=["Date","Minutes"])
        df["Date"]=pd.to_datetime(df["Date"])
        st.line_chart(df.set_index("Date")["Minutes"])
    else:
        st.write("No focus sessions yet.")

# --- MCQ Quiz ---
elif page=="📝 MCQ Quiz":
    st.title("📝 Task-Based MCQ Quiz")
    mcq_bank = {
        "Default":[
            {"question":"What is the main goal of this task?","options":["Priority","Urgency","Fun","Ignore"],"answer":"Priority"},
            {"question":"Is this task urgent?","options":["Low","Medium","High","Critical"],"answer":"High"}
        ]
    }
    tasks=get_tasks()
    if tasks:
        for task,status,prio,_ in tasks:
            st.markdown(f"🎯 **Task:** {task}  (Priority: {prio})")
            mcqs=mcq_bank.get(task, mcq_bank["Default"])
            score=0
            for i,q in enumerate(mcqs):
                ans=st.radio(q["question"], q["options"], key=f"{task}_{i}")
                if ans==q["answer"]:
                    score+=1
            if st.button(f"Submit Quiz for {task}"):
                conn=get_connection()
                cursor=conn.cursor()
                today=str(datetime.date.today())
                cursor.execute("INSERT INTO task_quiz_scores(task,score,date) VALUES(?,?,?)",(task,score,today))
                conn.commit()
                conn.close()
                st.success(f"Quiz Score for '{task}': {score}/{len(mcqs)}!")
                if score==len(mcqs):
                    st.balloons()
    else:
        st.write("Add tasks to unlock quizzes!")

# --- Export / Reports ---
elif page=="💾 Export/Reports":
    st.title("💾 Export / Reports")
    tasks_df=pd.read_sql("SELECT * FROM tasks",get_connection())
    focus_df=pd.read_sql("SELECT * FROM focus_log",get_connection())
    quiz_df=pd.read_sql("SELECT * FROM task_quiz_scores",get_connection())

    col1,col2,col3=st.columns(3)
    col1.metric("Total Tasks", len(tasks_df))
    col2.metric("Focus Sessions", len(focus_df))
    col3.metric("Quizzes Taken", len(quiz_df))

    st.download_button("📥 Download Tasks CSV", tasks_df.to_csv(index=False), "tasks.csv")
    st.download_button("📥 Download Focus CSV", focus_df.to_csv(index=False), "focus.csv")
    st.download_button("📥 Download Quiz CSV", quiz_df.to_csv(index=False), "quiz.csv")
