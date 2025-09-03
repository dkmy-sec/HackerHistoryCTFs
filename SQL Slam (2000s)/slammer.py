from flask import Flask, request, render_template_string
import sqlite3


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        q = f"SELECT * FROM users WHERE username='{user}' AND password='{pw}'"
        c.execute(q)
        if c.fetchone():
            return "Flag: bithaven{sql_injection_master}"
        else:
            return "Login failed."
    return'''<form method="POST">
                <input type="text" name="username">
                <input type="password" name="password">
                <input type="submit">
            </form>'''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1434)
