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
            message = "Congrats! 🍾 Flag: bithaven{sql_injection_master}"
        else:
            message = "Login failed."

            # show result inside the same template + a back button
        return render_template_string(TPL, message=message)

    # first visit → just render the form
    return render_template_string(TPL, message=None)


# Re-usable HTML template -------------------------------------------------
TPL = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>SQL Slammer – Log in</title>
    <style>
        body        {font-family:system-ui, sans-serif; background:#222; color:#eee; display:flex;
                     height:100vh; align-items:center; justify-content:center;}
        .card       {background:#333; padding:2rem 3rem; border-radius:8px; width:320px;
                     box-shadow:0 4px 20px rgba(0,0,0,.6);}
        h1          {margin-top:0; font-size:1.4rem; letter-spacing:.03em;}
        label,input {display:block; width:100%;}
        label       {margin:.8rem 0 .3rem;}
        input[type=text], input[type=password] {
                     padding:.6rem .7rem; border:none; border-radius:4px; font-size:1rem;}
        .toggle     {margin:.4rem 0 1rem; font-size:.85rem;}
        button      {width:100%; padding:.7rem; border:none; border-radius:4px;
                     background:#39c4b6; color:#fff; font-size:1rem; cursor:pointer;}
        .msg        {margin-bottom:1rem; text-align:center; font-weight:600;}
        a.retry     {color:#00adff; display:block; text-align:center; margin-top:1.2rem;}
    </style>
</head>
<body>
    <div class="card">
        {% if message %}
            <div class="msg">{{ message }}</div>
            <a class="retry" href="/">⟵ Try again</a>
        {% else %}
            <h1>Login</h1>
            <form method="POST" autocomplete="off">
                <label>Username
                    <input type="text" name="username" required>
                </label>
                <label>Password
                    <input id="pw" type="password" name="password" required>
                </label>
                <label class="toggle">
                    <input type="checkbox" onclick="pw.type=this.checked?'text':'password'">
                    show password
                </label>
                <button type="submit">Submit</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""
# ------------------------------------------------------------------------


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1434)
