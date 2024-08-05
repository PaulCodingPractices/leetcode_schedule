import random
import json
import os
import time
from datetime import datetime
import schedule
from plyer import notification
from PyQt5 import QtWidgets

# Path to the problems file
problems_file_path = "problems.json"


# Load the problems list from JSON file
def load_problems():
    try:
        with open(problems_file_path, 'r') as problems_file:
            problems = json.load(problems_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        problems = {}
        print(f"Error loading problems file: {e}")
    return problems


important_problems = load_problems()

progress_file_path = "daily_progress.json"

if not os.path.exists(progress_file_path):
    with open(progress_file_path, 'w') as progress_file:
        json.dump({}, progress_file)

try:
    with open(progress_file_path, 'r') as progress_file:
        progress = json.load(progress_file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    progress = {}
    print(f"Error loading progress file: {e}")


def create_weekly_schedule(problems):
    weekly_tasks = []
    for category in problems:
        selected_problem = random.choice(problems[category])
        weekly_tasks.append({"category": category, "problem": selected_problem})

    while len(weekly_tasks) < 7:
        category = random.choice(list(problems.keys()))
        selected_problem = random.choice(problems[category])
        weekly_tasks.append({"category": category, "problem": selected_problem})

    random.shuffle(weekly_tasks)
    return weekly_tasks


weekly_schedule = create_weekly_schedule(important_problems)


def save_schedule(schedule, filename="weekly_schedule.json"):
    try:
        with open(filename, 'w') as schedule_file:
            json.dump(schedule, schedule_file)
    except IOError as e:
        print(f"Error saving schedule file: {e}")


save_schedule(weekly_schedule)


def notify(problem):
    notification.notify(
        title='Problem Reminder',
        message=f"Solve {problem['category']} problem - {problem['problem']['name']} ({problem['problem']['difficulty']})",
        timeout=10
    )


def set_reminders():
    for task in weekly_schedule:
        schedule.every().day.at("12:00").do(notify, task)
        schedule.every().day.at("20:00").do(notify, task)


set_reminders()


def mark_task_done(category, problem_name):
    date = datetime.now().strftime("%Y-%m-%d")
    if date not in progress:
        progress[date] = []
    progress[date].append({"category": category, "problem": problem_name})

    try:
        with open(progress_file_path, 'w') as progress_file:
            json.dump(progress, progress_file)
    except IOError as e:
        print(f"Error saving progress file: {e}")


class TaskTrackerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Task Tracker')

        self.layout = QtWidgets.QVBoxLayout()

        self.instructions = QtWidgets.QLabel('Select the problem you have solved:')
        self.layout.addWidget(self.instructions)

        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(important_problems.keys())
        self.layout.addWidget(self.category_combo)

        self.problem_combo = QtWidgets.QComboBox()
        self.update_problems()
        self.layout.addWidget(self.problem_combo)

        self.category_combo.currentIndexChanged.connect(self.update_problems)

        self.mark_done_button = QtWidgets.QPushButton('Mark as Done')
        self.mark_done_button.clicked.connect(self.mark_as_done)
        self.layout.addWidget(self.mark_done_button)

        self.update_problems_button = QtWidgets.QPushButton('Update Problems List')
        self.update_problems_button.clicked.connect(self.update_problems_list)
        self.layout.addWidget(self.update_problems_button)

        self.setLayout(self.layout)

    def update_problems(self):
        category = self.category_combo.currentText()
        self.problem_combo.clear()
        self.problem_combo.addItems([problem['name'] for problem in important_problems[category]])

    def mark_as_done(self):
        category = self.category_combo.currentText()
        problem_name = self.problem_combo.currentText()
        mark_task_done(category, problem_name)
        QtWidgets.QMessageBox.information(self, 'Success', f'Marked {problem_name} as done.')

    def update_problems_list(self):
        new_problems, ok = QtWidgets.QInputDialog.getText(self, 'Update Problems List',
                                                          'Enter new problems list in JSON format:')
        if ok:
            try:
                new_problems_dict = json.loads(new_problems)
                with open(problems_file_path, 'w') as problems_file:
                    json.dump(new_problems_dict, problems_file)
                global important_problems
                important_problems = new_problems_dict
                self.category_combo.clear()
                self.category_combo.addItems(important_problems.keys())
                self.update_problems()
                QtWidgets.QMessageBox.information(self, 'Success', 'Problems list updated successfully.')
            except json.JSONDecodeError as e:
                QtWidgets.QMessageBox.critical(self, 'Error', f'Invalid JSON format: {e}')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    task_tracker = TaskTrackerApp()
    task_tracker.show()
    app.exec_()

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
