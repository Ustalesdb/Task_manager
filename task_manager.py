import sys
import os
import json
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox, QLineEdit, QInputDialog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_MAIN = os.path.join(BASE_DIR, "main_win.ui")
PATH_LOGIN = os.path.join(BASE_DIR, "checkpss.ui")
TASKS_PATH = os.path.join(BASE_DIR, "saved_tasks.json")

listt = []
is_admin = False


def load_tasks():
    global listt
    try:
        with open(TASKS_PATH, "r", encoding="utf-8") as f:
            listt = json.load(f)
    except FileNotFoundError:
        listt = []


def saved_tasks():
    with open(TASKS_PATH, "w", encoding="utf-8") as f:
        json.dump(listt, f, ensure_ascii=False, indent=2)


def get_color_for_priority(priority: int):
    if priority == 1:
        return "#e20d0d"  
    elif priority == 2:
        return "#f1a50b"  
    elif priority == 3:
        return "#04AA04"  
    return "#ffffff"


def display_tasks():
    win.textBrowser.clear()
    if not listt:
        win.textBrowser.append("<i>No tasks yet...</i>")
        return

    for i, task in enumerate(listt):
        name = task.get("owner", "")
        text = task.get("task", "")
        color = task.get("color", "#ffffff")
        priority = task.get("Priority", "N/A")
        html_line = f'''
        <p style="margin:4px 0;">
            <span style="font-size:18px; color:{color};">●</span>
            <b style="color:#aaffaa;">[{i}] {name}</b>
            <span style="color:#ffffff;"> — {text}</span>
            <span style="color:#2A7D5F;"> (Priority: {priority})</span>
        </p>
        '''
        win.textBrowser.append(html_line)

    win.pushButton.setEnabled(is_admin)
    win.db.setEnabled(is_admin)


def del_task():
    if not is_admin:
        QMessageBox.warning(win, "Access denied", "Only admin can delete tasks")
        return

    if not listt:
        QMessageBox.information(win, "Info", "No tasks to delete")
        return

    index_str, ok = QInputDialog.getText(win, "Delete task", "Enter task index:")
    if not ok or not index_str.strip():
        return

    try:
        index = int(index_str)
        if 0 <= index < len(listt):
            reply = QMessageBox.question(win, 'Confirm delete',
                                         f'Delete task "{listt[index]["task"]}"?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                del listt[index]
                saved_tasks()
                display_tasks()
        else:
            QMessageBox.warning(win, 'Error', 'Invalid index!')
    except ValueError:
        QMessageBox.warning(win, 'Error', 'Index must be a number!')


def write_tasks():
    if not is_admin:
        QMessageBox.warning(win, "Access denied", "Only admin can add tasks!")
        return

    task_text = win.plainTextEdit.toPlainText().strip()
    if not task_text:
        QMessageBox.warning(win, "Warning", "Task cannot be empty!")
        return

    owner, ok = QInputDialog.getText(win, "For whom", "Enter first and last name:")
    if not ok or not owner.strip():
        return

    priority, ok = QInputDialog.getItem(
        win, 'Priority', 'Select task importance:',
        ["1 - high", "2 - medium", "3 - low"], 1, False)
    if not ok:
        return

    prty_lvl = int(priority.split('-')[0].strip())
    color = get_color_for_priority(prty_lvl)
    new_task = {"owner": owner.strip(), "task": task_text,
                "color": color, "Priority": prty_lvl}
    listt.append(new_task)
    saved_tasks()
    display_tasks()
    win.plainTextEdit.clear()


def check_password():
    global is_admin
    usrn = win1.ln.text().strip().lower()
    pssw = win1.ln2.text().strip().lower()

    if usrn == "admin" and pssw == "123":
        QMessageBox.information(win1, "Info", "Success — admin mode")
        is_admin = True
    else:
        QMessageBox.warning(win1, "Info", "Incorrect password, user mode")
        is_admin = False

    win1.close()
    open_main_window()


def open_main_window():
    global win
    win = uic.loadUi(PATH_MAIN)
    win.setFixedSize(1164, 455)
    win.pushButton.clicked.connect(write_tasks)
    win.db.clicked.connect(del_task)
    load_tasks()
    display_tasks()
    win.show()


app = QApplication(sys.argv)
win1 = uic.loadUi(PATH_LOGIN)
win1.pb.clicked.connect(check_password)
win1.ln2.setEchoMode(QLineEdit.Password)
win1.setFixedSize(664, 375)
load_tasks()
win1.show()
sys.exit(app.exec_())
