from flask import Flask, render_template, rendeATr_template_string, request, redirect, url_for, flash, session
from datetime import datetime, date, timedelta
from creds import TOKEN, CHAT_ID
from zoneinfo import ZoneInfo
import sqlite3
import telepot
import urllib3



bot = telepot.Bot(TOKEN)

app = Flask(__name__)
app.secret_key = "SuperSecretKey"
app.permanent_session_lifetime = timedelta(minutes=2)

db = sqlite3.connect("DB.db", check_same_thread=False)
cursor = db.cursor()

admin_db = sqlite3.connect("admin.db", check_same_thread=False)
ad_cursor = admin_db.cursor()

@app.route("/", methods=["GET", "POST"])
def home():
    db = sqlite3.connect("DB.db", check_same_thread=False)
    cursor = db.cursor()
    today_date = date.today().strftime("%d/%m/%Y")
    t24 = datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime("%H:%M:%S")
    hour = t24.split(":")[0]
    minute = t24.split(":")[1]
    second = t24.split(":")[2]
    hour = int(hour)
    if hour >= 12:
        AoP = "PM"
        current_time = f"{hour-12}:{minute}:{second} {AoP}"
    else:
        AoP = "AM"
        current_time = f"{hour}:{minute}:{second} {AoP}"

    if request.method == "POST":
        name = request.form["user_name"]
        if len(name) == 0:
            flash("Name not valid")
            return render_template("index.html")
        elif len(name) > 20:
            flash("Name should be less than 20 characters")
            return render_template("index.html")
        else:
            users_list = []
            cursor.execute("SELECT name FROM users")
            for user in cursor.fetchall():
                users_list.append(user[0])
            temp = []

            for x in users_list:
                if x not in temp:
                    temp.append(x)
            if name in temp:
                flash("Already added to the database")
            else:
                cursor.execute("INSERT INTO users VALUES(?,?,?)", (name, today_date, current_time))
                db.commit()
                bot.sendMessage(CHAT_ID, f"{name} is added to the database\nDate: {today_date}\nTime: {current_time}")
    return render_template("index.html")

@app.route("/database", methods=["GET", "POST"])
def db():
    db = sqlite3.connect("DB.db", check_same_thread=False)
    cursor = db.cursor()

    if request.method == "POST":
        delete_id = int(request.form["values"])
        print(delete_id)
        cursor.execute("SELECT name FROM users")
        delete_user = cursor.fetchall()[delete_id][0]
        bot.sendMessage(CHAT_ID, f"{delete_user} with id {delete_id+1} was reported")

    n = list(cursor.execute("SELECT name FROM users"))
    d = list(cursor.execute("SELECT date FROM users"))
    t = list(cursor.execute("SELECT time FROM users"))

    return render_template("database.html", names=n, dates=d, times=t, zip=zip, enumerate=enumerate)

@app.route("/contact", methods=["GET", "POST"])
def contact_me():
    db = sqlite3.connect("data.db")
    cursor1 = db.cursor()
    if request.method == "POST":
        name = request.form["Mname"]
        email = request.form["email"]
        msg = request.form["message"]
        if len(name) == 0 or len(email) == 0 or len(msg) == 0:
            flash("FILL ALL THE FIELDS TO SEND THE MESSAGE")
        else:
            cursor1.execute("INSERT INTO chats VALUES(?,?,?)", (name, email, msg))
            db.commit()
            bot.sendMessage(CHAT_ID, f"Message from {name}\nEmail: {email}\nMessage: {msg}")
            return render_template("msg.html")
    return render_template("contact.html")

@app.route("/admin")
def admin():
    if "username" in session:
        n = list(cursor.execute("SELECT name FROM users"))
        d = list(cursor.execute("SELECT date FROM users"))
        t = list(cursor.execute("SELECT time FROM users"))
        return render_template("admin.html", names=n, dates=d, times=t, zip=zip, enumerate=enumerate)
    else:
        print("Not in session")
        return redirect(url_for("admin_login"))

@app.route("/admin/delete/<id>")
def delete(id):
    cursor.execute("SELECT name FROM users")
    name = cursor.fetchall()[int(id)][0]
    print(name)
    query = "DELETE FROM users WHERE name=?"
    params = name,
    cursor.execute(query, params)
    db.commit()
    cursor.execute("SELECT name FROM users")
    for x in cursor.fetchall():
        print(x)
    return redirect(url_for("admin"))

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":

        session.permanent = True
        userName = request.form["username"]
        passWord = request.form["password"]
        print(userName, passWord)
        #ad_cursor.execute("CREATE TABLE administrator('username TEXT', 'password TEXT')")
        cursor.execute("INSERT INTO administrator VALUES('shahadil_naz', 'root@password')")
        Org_password = ad_cursor.fetchall()[0][1]
        ad_cursor.execute("SELECT * FROM administrator")
        print(cursor.fetchall())
        Org_username = ad_cursor.fetchall()[0][0]
        ad_cursor.execute("SELECT * FROM administrator")
        Org_password = ad_cursor.fetchall()[0][1]
        if userName == Org_username and passWord == Org_password:
            session["username"] = Org_username
            return redirect(url_for("admin"))
    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True)
