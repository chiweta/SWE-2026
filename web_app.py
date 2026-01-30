from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

FILE_PATH = BASE_DIR / "tasks.txt"


def load_tasks():
    tasks = []
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue

                parts = raw.split("|", 2)

                # Old format: "text"
                if len(parts) == 1:
                    tasks.append({"done": False, "date": date.today().isoformat(), "text": parts[0]})
                    continue

                # Old format: "done|text"
                if len(parts) == 2:
                    status, text = parts
                    tasks.append({"done": status == "1", "date": date.today().isoformat(), "text": text.strip()})
                    continue

                # New format: "done|date|text"
                status, d, text = parts
                tasks.append({"done": status == "1", "date": d.strip(), "text": text.strip()})

    except FileNotFoundError:
        pass

    return tasks




def save_tasks(tasks):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        for t in tasks:
            status = "1" if t["done"] else "0"
            f.write(f"{status}|{t['date']}|{t['text']}\n")


def toggle_done(num):
    tasks= load_tasks()
    if 1 <= num <= len(tasks):
        tasks[num - 1]["done"]= not tasks[num -1]["done"]
        save_tasks(tasks)
@app.get("/")
def home():
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks)


@app.post("/add")
def add():
    task = request.form.get("task", "").strip()
    task_date = request.form.get("date", "").strip() or date.today().isoformat()

    if task:
        tasks = load_tasks()
        tasks.append({"done": False, "date": task_date, "text": task})
        save_tasks(tasks)

    return redirect(url_for("home"))

@app.get("/events")
def events():
    tasks = load_tasks()
    return jsonify([
        {
            "title": ("✅ " if t["done"] else "") + t["text"],
            "start": t["date"],   # YYYY-MM-DD
            "allDay": True
        }
        for t in tasks
        if t.get("date")
    ])




@app.post("/delete_selected")
def delete_selected():
    nums = request.form.getlist("nums")  # list of strings like ["1", "3", "5"]

    try:
        nums = sorted({int(n) for n in nums}, reverse=True)
    except ValueError:
        return redirect(url_for("home"))

    tasks = load_tasks()

    for n in nums:
        if 1 <= n <= len(tasks):
            tasks.pop(n - 1)

    save_tasks(tasks)
    return redirect(url_for("home"))


@app.post("/mark_done")
def mark_done():
    num_str = request.form.get("num", "").strip()
    try:
        num = int(num_str)
    except ValueError:
        return redirect(url_for("home"))

    toggle_done(num)
    return redirect(url_for("home"))

@app.post("/delete_all")
def delete_all():
    save_tasks([])
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
