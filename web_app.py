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


# --------- Storage helpers (txt file) ---------
def load_tasks():
    """
    Supports:
      - old: "text"
      - old: "done|text"
      - new: "done|date|text"
    """
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


# --------- Pages ---------
@app.get("/")
def home():
    selected_date = request.args.get("date") or date.today().isoformat()
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks, selected_date=selected_date)


# --------- Actions (POST) ---------
@app.post("/add")
def add():
    task = request.form.get("task", "").strip()
    day = request.form.get("date", "").strip() or date.today().isoformat()

    if task:
        tasks = load_tasks()
        tasks.append({"done": False, "text": task, "date": day})
        save_tasks(tasks)

    return redirect(url_for("home", date=day))


@app.post("/delete_day_selected")
def delete_day_selected():
    day = request.form.get("date", "").strip() or date.today().isoformat()

    ids = request.form.getlist("ids")
    try:
        ids = sorted({int(x) for x in ids}, reverse=True)
    except ValueError:
        return redirect(url_for("home", date=day))

    tasks = load_tasks()
    for i in ids:
        if 1 <= i <= len(tasks):
            tasks.pop(i - 1)

    save_tasks(tasks)
    return redirect(url_for("home", date=day))


@app.post("/delete_all_for_day")
def delete_all_for_day():
    day = request.form.get("date", "").strip() or date.today().isoformat()
    tasks = [t for t in load_tasks() if t.get("date") != day]
    save_tasks(tasks)
    return redirect(url_for("home", date=day))


# IMPORTANT: this is called via fetch() in JS, so return 204 (no redirect)
@app.post("/toggle_done")
def toggle_done_api():
    task_id = request.form.get("id", "").strip()
    try:
        idx = int(task_id)
    except ValueError:
        return ("", 400)

    tasks = load_tasks()
    if 1 <= idx <= len(tasks):
        tasks[idx - 1]["done"] = not tasks[idx - 1]["done"]
        save_tasks(tasks)

    return ("", 204)


# --------- JSON feeds for the calendar + daily list ---------
@app.get("/events")
def events():
    tasks = load_tasks()
    out = []

    for i, t in enumerate(tasks, start=1):
        out.append({
            "title": ("✅ " if t["done"] else "") + t["text"],
            "start": t["date"],
            "allDay": True,
            "extendedProps": {"id": i},
        })

    return jsonify(out)


@app.get("/tasks_for_day")
def tasks_for_day():
    day = request.args.get("date", "").strip()
    tasks = load_tasks()

    day_tasks = []
    for i, t in enumerate(tasks, start=1):
        if t.get("date") == day:
            day_tasks.append({
                "id": i,
                "text": t["text"],
                "done": t["done"],
                "date": t["date"],
            })

    return jsonify(day_tasks)


if __name__ == "__main__":
    app.run(debug=True)
