from flask import Flask, render_template, send_file
import sqlite3
import os

app = Flask(__name__)

def query_db(query, args=(), one=False):
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def index():
    data = query_db("SELECT date, SUM(amount) as total FROM payments GROUP BY date")
    with open("_js_script.html", "r", encoding="utf-8") as f_js, open("_bottom_nav.html", "r", encoding="utf-8") as f_nav:
        js = f_js.read()
        nav = f_nav.read()
    return render_template("index.html", data=data, js=js, nav=nav)

@app.route("/backup")
def backup():
    return send_file("data.db", as_attachment=True)
