import json
import os
from datetime import datetime

class ProductivityManager:
    def __init__(self, data_file="productivity_data.json"):
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    # Ensure schema
                    if "tasks" not in data: data["tasks"] = []
                    if "scratchpad" not in data: data["scratchpad"] = ""
                    return data
            except:
                return {"tasks": [], "scratchpad": ""}
        return {"tasks": [], "scratchpad": ""}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_task(self, title, date_str, time_str=None, end_time=None, reminder=False, category="Other"):
        """
        date_str: YYYY-MM-DD
        time_str: HH:MM (Start Time)
        end_time: HH:MM (End Time)
        reminder: boolean
        """
        task = {
            "id": int(datetime.now().timestamp() * 1000),
            "title": title,
            "date": date_str,
            "time": time_str,
            "end_time": end_time,
            "reminder": reminder,
            "category": category,
            "completed": False
        }
        self.data["tasks"].append(task)
        self.save_data()
        return task

    def toggle_task(self, task_id):
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                self.save_data()
                return task
        return None

    def delete_task(self, task_id):
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        self.save_data()

    def get_tasks_for_date(self, date_str):
        return [t for t in self.data["tasks"] if t["date"] == date_str]

    def get_all_tasks(self):
        return self.data["tasks"]

    def get_upcoming_tasks(self, limit=10):
        # Get tasks from tomorrow onwards
        today = datetime.now().strftime("%Y-%m-%d")
        all_tasks = self.data["tasks"]
        future = [t for t in all_tasks if t["date"] > today and not t["completed"]]
        future.sort(key=lambda x: x["date"])
        return future[:limit]

    def get_scratchpad(self):
        return self.data.get("scratchpad", "")

    def save_scratchpad(self, content):
        self.data["scratchpad"] = content
        self.save_data()
