pip install streamlit streamlit-pydantic

import streamlit as st
from streamlit_pydantic import st_form

import sqlite3
from sqlite3 import Error
from pydantic import BaseModel

# SQLite Database setup
DATABASE_FILE = "tasks.db"

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        is_done INTEGER DEFAULT 0
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)

# Pydantic model for Task
class TaskModel(BaseModel):
    name: str
    description: str = ""
    is_done: bool = False

# Streamlit app
def main():
    conn = create_connection()
    if conn is not None:
        create_table(conn)

    st.title("Task Management App")

    # Create Task Form
    task_form = st_form(key="task_form", form=TaskModel)

    if task_form:
        # Save Task to SQLite3
        task_data = task_form.json()
        save_task_to_db(conn, task_data)

    # List Tasks
    st.header("Task List")
    tasks = get_tasks_from_db(conn)

    for task in tasks:
        st.checkbox(task["name"], value=task["is_done"], key=task["id"])

    # Update Task status
    if st.button("Update Task Status"):
        update_task_status(conn, tasks)

def save_task_to_db(conn, task_data):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (name, description, is_done) VALUES (?, ?, ?)",
            (task_data["name"], task_data["description"], task_data["is_done"]),
        )
        conn.commit()
    except Error as e:
        print(e)

def get_tasks_from_db(conn):
    tasks = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        for row in rows:
            task = {"id": row[0], "name": row[1], "description": row[2], "is_done": row[3]}
            tasks.append(task)
    except Error as e:
        print(e)
    return tasks

def update_task_status(conn, tasks):
    try:
        cursor = conn.cursor()
        for task in tasks:
            cursor.execute("UPDATE tasks SET is_done = ? WHERE id = ?", (task["is_done"], task["id"]))
        conn.commit()
    except Error as e:
        print(e)

if __name__ == "__main__":
    main()
