from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

FILE_PATH = BASE_DIR / "tasks.txt"


def load_tasks():
    tasks=[]
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            for raw in f:
                raw=raw.strip()
                if not raw:
                    continue

                if "|" not in raw:
                    tasks.append({"done": False, "text": raw})
                    continue

                status, text = raw.split("|", 1)
                tasks.append({"done": status =="1", "text": text.strip()})
    except FileNotFoundError:
        pass
    return tasks



def save_tasks(tasks):
    with open(FILE_PATH, "w", encoding="utf-8")as f:
        for t in tasks:
            status = "1" if t["done"] else "0"
            f.write(f"{status}|{t['text']}\n")

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
    if task:
        tasks = load_tasks()
        tasks.append({"done": False, "text": task})
        save_tasks(tasks)
    return redirect(url_for("home"))



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
