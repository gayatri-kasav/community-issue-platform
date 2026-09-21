from flask import Flask, render_template, request, redirect
from database import get_connection

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/report")
def report():
    return render_template("report.html")


@app.route("/submit", methods=["POST"])
def submit():

    name = request.form["name"]
    category = request.form["category"]
    location = request.form["location"]
    description = request.form["description"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO complaints
        (name, category, location, description)
        VALUES (%s, %s, %s, %s)
        RETURNING complaint_id""",
        (name, category, location, description)
    )

    complaint_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return render_template("success.html", complaint_id=complaint_id)
@app.route("/complaints")
def complaints():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM complaints
        ORDER BY complaint_id ASC
    """)

    complaints = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("complaints.html", complaints=complaints)

@app.route("/track", methods=["GET", "POST"])
def track():

    if request.method == "POST":

        complaint_id = request.form["complaint_id"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM complaints WHERE complaint_id = %s",
            (complaint_id,)
        )

        complaint = cursor.fetchone()

        cursor.close()
        conn.close()

        if complaint:
            return render_template("track_result.html", complaint=complaint)
        else:
            return render_template("track_not_found.html")

    return render_template("track.html")

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            return redirect("/admin_dashboard")

        else:
            return "Invalid Username or Password"

    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM complaints
        ORDER BY complaint_id ASC
    """)

    complaints = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_dashboard.html", complaints=complaints)

@app.route("/update_status", methods=["POST"])
def update_status():

    complaint_id = request.form["complaint_id"]
    status = request.form["status"]
    resolution_remarks = request.form["resolution_remarks"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE complaints
        SET status = %s,
            resolution_remarks = %s
        WHERE complaint_id = %s
        """,
        (status, resolution_remarks, complaint_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin_dashboard")

if __name__ == "__main__":
    app.run(debug=True)