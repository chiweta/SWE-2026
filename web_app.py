from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
app = Flask(__name__)
FILE_PATH = Path(__file__).with_name("tasks.txt")


def get_tasks():
    try:
        with open(FILE_PATH, "r", encoding="utf-8")as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        return []


@app.get("/")
def home():
    tasks = get_tasks()
    return render_template("index.html", tasks=tasks)


@app.post("/add")
def add():
    task = request.form.get("task", "").strip()
    if task:
        with open(FILE_PATH, "a", encoding="utf-8")as f:
            f.write(task + "\n")
    print("WROTE TO:", FILE_PATH)
    return redirect(url_for("home"))


@app.post("/delete_selected")
def delete_selected():
    nums = request.form.getlist("nums")  # list of strings like ["1", "3", "5"]

    try:
        nums = sorted({int(n) for n in nums}, reverse=True)
    except ValueError:
        return redirect(url_for("home"))

    tasks = get_tasks()

    for n in nums:
        if 1 <= n <= len(tasks):
            tasks.pop(n - 1)

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        for t in tasks:
            f.write(t + "\n")

    return redirect(url_for("home"))


@app.post("/mark_done")
def mark_done():


if __name__ == "__main__":
    app.run(debug=True)
