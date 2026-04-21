from flask import Flask, render_template, request
from planner import generate_plan

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/plan", methods=["POST"])
def plan():
    user_data = {
        "name": request.form.get("name", "").strip(),
        "profession": request.form.get("profession", "").strip(),
        "sleep_hours": float(request.form.get("sleep_hours", 7)),
        "energy_level": int(request.form.get("energy_level", 5)),
        "stress_level": int(request.form.get("stress_level", 5)),
        "focus_level": int(request.form.get("focus_level", 5)),
        "wake_time": request.form.get("wake_time", "07:00"),
        "work_start": request.form.get("work_start", "09:00"),
        "work_end": request.form.get("work_end", "17:00"),
        "goals": request.form.get("goals", "").strip(),
        "tasks": request.form.get("tasks", "").strip(),
        "days_available": int(request.form.get("days_available", 7)),
        "deadline_pressure": int(request.form.get("deadline_pressure", 5)),
        "break_preference": request.form.get("break_preference", "medium").strip()
    }

    result = generate_plan(user_data)
    return render_template("result.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)