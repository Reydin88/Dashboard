from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def query_db(query, args=(), one=False):
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "1234":
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            error = "Неверный логин или пароль"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.before_request
def require_login():
    if request.endpoint not in ("login", "static") and not session.get("logged_in"):
        return redirect(url_for("login"))

@app.route("/")
def index():
    data = query_db("SELECT date, SUM(amount) as total FROM payments GROUP BY date")
    return render_template("index.html", data=data)

@app.route("/payments")
def payments():
    status_filter = request.args.get("status", "")
    if status_filter:
        payments = query_db("SELECT * FROM payments WHERE status=?", [status_filter])
    else:
        payments = query_db("SELECT * FROM payments")
    return render_template("payments.html", payments=payments, selected=status_filter)

@app.route("/withdrawals")
def withdrawals():
    withdrawals = query_db("SELECT * FROM withdrawals")
    return render_template("withdrawals.html", withdrawals=withdrawals)


@app.route("/payments/edit/<int:payment_id>", methods=["GET", "POST"])
def edit_payment(payment_id):
    payment = query_db("SELECT * FROM payments WHERE id=?", [payment_id], one=True)
    if request.method == "POST":
        new_status = request.form["status"]
        new_amount = request.form["amount"]
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        cur.execute("UPDATE payments SET status=?, amount=? WHERE id=?", (new_status, new_amount, payment_id))
        conn.commit()
        conn.close()
        return redirect(url_for("payments"))
    return render_template("edit_payment.html", payment=payment)

@app.route("/payments/delete/<int:payment_id>", methods=["POST"])
def delete_payment(payment_id):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM payments WHERE id=?", (payment_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("payments"))


import json
from werkzeug.security import generate_password_hash, check_password_hash

def load_settings():
    with open("settings.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f)

@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    settings = load_settings()
    message = ""
    if request.method == "POST":
        current = request.form["current_password"]
        new_user = request.form["username"]
        new_pass = request.form["new_password"]
        if current == settings["password"]:
            settings["username"] = new_user
            settings["password"] = new_pass
            save_settings(settings)
            message = "Настройки обновлены"
        else:
            message = "Неверный текущий пароль"
    return render_template("settings.html", message=message)

@app.route("/withdrawals/edit/<int:withdrawal_id>", methods=["GET", "POST"])
def edit_withdrawal(withdrawal_id):
    withdrawal = query_db("SELECT * FROM withdrawals WHERE id=?", [withdrawal_id], one=True)
    if request.method == "POST":
        new_status = request.form["status"]
        new_amount = request.form["amount"]
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        cur.execute("UPDATE withdrawals SET status=?, amount=? WHERE id=?", (new_status, new_amount, withdrawal_id))
        conn.commit()
        conn.close()
        return redirect(url_for("withdrawals"))
    return render_template("edit_withdrawal.html", withdrawal=withdrawal)

@app.route("/withdrawals/delete/<int:withdrawal_id>", methods=["POST"])
def delete_withdrawal(withdrawal_id):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM withdrawals WHERE id=?", (withdrawal_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("withdrawals"))

# Изменим login() с использованием settings.json
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    settings = load_settings()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == settings["username"] and password == settings["password"]:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            error = "Неверный логин или пароль"
    return render_template("login.html", error=error)
