FILE_NAME = "tasks.txt"

def add_task():
    task = input("What task would you like to add? ").strip()
    if not task:
        print("Task cannot be empty.")
        return

    with open(FILE_NAME, "a", encoding="utf-8") as file:
        file.write(task + "\n")

    print(f'Task "{task}" added successfully!')


def view_tasks():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            tasks = file.readlines()

        if not tasks:
            print("No tasks found.")
            return

        print("Here are your tasks:")
        for index, task in enumerate(tasks, start=1):
            print(f"{index}. {task.strip()}")

    except FileNotFoundError:
        print("No tasks found.")


def delete_task():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            tasks = file.readlines()

        if not tasks:
            print("No tasks to delete.")
            return

        print("Which task do you want to delete?")
        for i, task in enumerate(tasks, start=1):
            print(f"{i}) {task.strip()}")

        num_str = input("Enter the task number: ").strip()
        num = int(num_str)

        if num < 1 or num > len(tasks):
            print("Invalid task number.")
            return

        deleted = tasks.pop(num - 1)

        with open(FILE_NAME, "w", encoding="utf-8") as file:
            file.writelines(tasks)

        print(f'Deleted: "{deleted.strip()}"')

    except FileNotFoundError:
        print("No tasks to delete.")
    except ValueError:
        print("Please enter a valid number.")
def clear_all():
    confirmation=input("Are you sure you want to clear all tasks? (yes/no):").strip().lower()
    if confirmation=="yes":
        with open(FILE_NAME,"w",encoding="utf-8") as file:
            file.write("")
        print("All tasks have been cleared.")
    else:
        print("Clear all tasks operation cancelled.")

while True:
    print("\nThis is the task tracker application!")
    choice = input("Select 1 to add, 2 to view, 3 to delete, 4 to exit, or 5 to clear all tasks: ").strip()

    if choice == "1":
        add_task()
    elif choice == "2":
        view_tasks()
    elif choice == "3":
        delete_task()
    elif choice == "4":
        print("Exiting the task tracker. Bye!")
        break
    elif choice == "5":
        clear_all()
    else:
        print("Invalid option. Please try again.")
