import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify

from datetime import datetime, timedelta
from datetime import date


from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///habits.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


#############################################################################################################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################################################

@app.route("/skuska")
def skuska():
    return render_template("skuska.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def homepage():
    """ Main page """
    # Habits overview
    user_id = session["user_id"]

    if (request.args.get("email") and request.args.get("email") != "Email fail"):
        flash("You have been signed up for the newsletter!", "success")
    elif (request.args.get("email") == "Email fail"):
        flash("Subscription unsuccessful, please provide a valid email address", "fail")

    # updating expiration values
    habits = db.execute("SELECT * FROM habits WHERE user_id = ?", user_id)

    now = datetime.now()
    currMonth = now.month
    currDay = now.day
    currYear = now.year

    # convert now to string format str_now = '2021/10/20'
    str_now = "{}/{:02d}/{:02d}".format(currYear, currMonth, currDay)

    # convert string str_now to date object
    d1 = datetime.strptime(str_now, "%Y/%m/%d")

    if len(habits) > 0:
        for habit in habits:
            habit_id = habit["id"]
            endMonth = habit["ende_month"]
            endDay = habit["ende_day"]
            endYear = habit["ende_year"]

            # convert to string format str_end = '2022/2/20'
            str_d2 = "{}/{:02d}/{:02d}".format(endYear, endMonth, endDay)


            # convert string str_end to date object
            d2 = datetime.strptime(str_d2, "%Y/%m/%d")

            expiration = d2 - d1
            expiration = expiration.days

            db.execute("UPDATE habits SET expiration = ? WHERE id=?", expiration, habit_id)


            if expiration < 0:
                db.execute("UPDATE habits SET expired = true WHERE id=?", habit_id)
            else:
                db.execute("UPDATE habits SET expired = false WHERE id=?", habit_id)


    return render_template("homepage.html", habits=habits)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if (request.method == "POST"):
        if not (request.form.get("username")):
            return apology("must provide username")
        if not (request.form.get("password")):
            return apology("must provide password")
        if not (request.form.get("confirmation")):
            return apology("must confirm password",)
        if (request.form.get("password") != request.form.get("confirmation")):
            return apology("passwords don't match")

        usrnm = request.form.get("username")
        psswrd = request.form.get("password")

        skuska = db.execute("SELECT * FROM users WHERE username IS ?", usrnm)
        if len(skuska) != 0:
            flash("Username is already taken", "fail")
            return redirect("register")

        hashed_p = generate_password_hash(psswrd)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", usrnm, hashed_p)

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Incorrect username of password", "fail")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/new_habit", methods=["POST"])
@login_required
def newhabit():
    user_id = session["user_id"]
    name = request.form.get("habit-name")
    if not name:
        return apology("Please enter a name")

    description = request.form.get("description")
    if not description:
        return apology("Please a enter a description")

    color = request.form.get("color-inp")
    if not color:
        return apology("Please choose a color")

    now = datetime.now()
    start_month = now.month
    start_day = now.day
    start_year = now.year

    duration = request.form.get("duration")
    if duration:
        end_date = datetime.now() + timedelta(days=int(duration))
        end_month = end_date.month
        end_day = end_date.day
        end_year = end_date.year
    else:
        end_month = 2;
        end_day = 14;
        end_year = 2103;


    expiration = 1

    weekdays = request.form.getlist('weekday')
    if weekdays:
        days_select = ""
        for day in weekdays:
            day = str(day)
            days_select = days_select + day + ","

        db.execute("INSERT INTO habits (user_id, name, description, color, start_month, start_day, start_year, ende_month, ende_day, ende_year, expiration, expired, weekdays) VALUES (?,?,?,?,?,?,?,?,?,?,?,false,?)", user_id, name, description, color, start_month, start_day, start_year, end_month, end_day, end_year, expiration, days_select)
        return redirect("/")

    days_select = "1,2,3,4,5,6,7,"
    db.execute("INSERT INTO habits (user_id, name, description, color, start_month, start_day, start_year, ende_month, ende_day, ende_year, expiration, expired, weekdays) VALUES (?,?,?,?,?,?,?,?,?,?,?,false,?)", user_id, name, description, color, start_month, start_day, start_year, end_month, end_day, end_year, expiration, days_select)
    return redirect("/")



@app.route("/day", methods=["GET", "POST"])
@login_required
def newday():
    user_id = session["user_id"]

    den = int(request.args.get("day"))
    mesiac = int(request.args.get("month"))
    rok = int(request.args.get("year"))

    dateObj = datetime(rok, mesiac, den)
    dateObj = dateObj.date()
    dateObj = dateObj.weekday()
    dayIndex = dateObj + 2 # to know which day of the week it is, as int

    if (request.method == "POST"):

        if (request.form.get("action") == "edit_day"):
            den = request.form.get("day")
            mesiac = request.form.get("month")
            rok = request.form.get("year")

            habit_id = request.form.get("habit_id")
            evaluation = request.form.get("evaluation")
            evaluation = int(evaluation)
            db.execute("UPDATE days SET evaluation=? WHERE (month = ? AND day = ? AND year = ? AND habit_id = ?)", evaluation, mesiac, den, rok, habit_id)

            notes = request.form.get("notes")
            if notes:
                db.execute("UPDATE days SET pozn=? WHERE (month = ? AND day = ? AND year = ? AND habit_id = ?)", notes, mesiac, den, rok, habit_id)

            habits = db.execute("SELECT * FROM habits JOIN days ON habits.id = days.habit_id WHERE (days.user_id=? AND month=? AND day=? AND year=? AND expired=false)", user_id, mesiac, den, rok)

            future_travel = 0
            hashsymbol = habit_id
            return render_template("day.html", den=den, mesiac=mesiac, rok=rok, habits=habits, future_travel=future_travel, dayIndex=dayIndex, hashsymbol=hashsymbol)

        elif (request.method == "POST" and request.form.get("action") == "delete_record"):
            habit_id = request.form.get("habit_id")
            db.execute("UPDATE days SET pozn=NULL, evaluation=NULL WHERE (habit_id=? AND month=? AND day=? AND year=?)", habit_id, mesiac, den, rok)

            habits = db.execute("SELECT * FROM habits JOIN days ON habits.id = days.habit_id WHERE (days.user_id=? AND month=? AND day=? AND year=? AND expired=false)", user_id, mesiac, den, rok)
            future_travel = 0
            return render_template("day.html", den=den, mesiac=mesiac, rok=rok, habits=habits, future_travel=future_travel, dayIndex=dayIndex)


    if mesiac > 12:
        mesiac = 1
        rok += 1

    if mesiac < 1:
        mesiac = 12
        rok -= 1


    ### GET route

    today = datetime.now()
    today_day = today.day
    today_month = today.month
    today_year = today.year

    future_travel = 0

    if rok > today_year:
        future_travel = 1
        return render_template("day.html", den=den, mesiac=mesiac, rok=rok, future_travel=future_travel)

    if den > today_day:
        if mesiac >= today_month:
            if rok == today_year:
                future_travel = 1
                return render_template("day.html", den=den, mesiac=mesiac, rok=rok, future_travel=future_travel)

    if mesiac > today_month:
        if rok == today_year:
            future_travel = 1
            return render_template("day.html", den=den, mesiac=mesiac, rok=rok, future_travel=future_travel)

    habits_ids = db.execute("SELECT id FROM habits WHERE (user_id = ?)", user_id) # vsetky habit ids daneho usera

    days_skuska = db.execute("SELECT * FROM days WHERE (user_id=? AND month=? AND day=? AND year=?)", user_id, mesiac, den, rok) # vsetky records na dany den daneho usera; ak riadkov bude menej ako habits_ids, znamena to, ze tak chyba riadok niektoreho habitu

    if len(days_skuska) != len(habits_ids):
        for n in habits_ids:
            n = n["id"]
            skuska = db.execute("SELECT habit_id FROM days WHERE (user_id=? AND month=? AND day=? AND year=? AND habit_id=?)", user_id, mesiac, den, rok, n)
            if len(skuska) == 0:
                db.execute("INSERT INTO days (user_id, habit_id, month, day, year) VALUES (?,?,?,?,?)", user_id, n, mesiac, den, rok)

    if today_month == mesiac and today_day == den and today_year == rok: #ked ide o today
        habits = db.execute("SELECT * FROM habits LEFT JOIN days ON habits.id = days.habit_id WHERE (habits.user_id=? AND month=? AND day=? AND year=? AND expired=false)", user_id, mesiac, den, rok)
        return render_template("day.html", den=den, mesiac=mesiac, rok=rok, habits=habits, today_day=today_day, today_month=today_month, today_year=today_year, future_travel=future_travel, dayIndex=dayIndex)
    else:
        habits = db.execute("SELECT * FROM habits LEFT JOIN days ON habits.id = days.habit_id WHERE ( ( (start_year < ?) OR (start_year = ? AND start_month < ?) OR (start_year = ? AND start_month = ? AND start_day <= ?)) AND ( (ende_year > ?) OR (ende_year = ? AND ende_month > ?) OR (ende_year = ? AND ende_month = ? AND ende_day >= ?)) AND habits.user_id=? AND month=? AND day=? AND year=? )", rok, rok, mesiac, rok, mesiac, den, rok, rok, mesiac, rok, mesiac, den, user_id, mesiac, den, rok) # selectne habits vramci casoveho rozmedzia medzi zaciatkom a koncom habitu
        return render_template("day.html", den=den, mesiac=mesiac, rok=rok, habits=habits, today_day=today_day, today_month=today_month, today_year=today_year, future_travel=future_travel, dayIndex=dayIndex)


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if (request.method == "POST"):
        user_id = session["user_id"]
        habit_id = request.form.get("habit_id")

        ende_month = request.form.get("ende_month")
        ende_day = request.form.get("ende_day")
        ende_year = request.form.get("ende_year")
        start_month = request.form.get("start_month")
        start_day = request.form.get("start_day")
        start_year = request.form.get("start_year")

        today = datetime.now()
        mesiac = today.month
        den = today.day
        rok = today.year

        habit_name = request.form.get("habit_name")
        habit_description = request.form.get("habit_description")
        color = request.form.get("color_val")
        weekdays = request.form.get("weekdays")
        return render_template("edit.html", start_month=start_month, start_day=start_day, start_year=start_year, habit_id=habit_id, habit_name=habit_name, habit_description=habit_description, color=color, ende_month=ende_month, ende_day=ende_day, ende_year=ende_year, weekdays=weekdays, mesiac=mesiac, den=den, rok=rok)

    else: # GET save changes and render homepage
        user_id = session["user_id"]
        habit_id = request.args.get("habit-id")

        name = request.args.get("habit-name")
        if not name:
            return apology("Please enter a name")

        description = request.args.get("description")
        if not description:
            return apology("Please a enter a description")

        color = request.args.get("color")
        if not color:
            return apology("Please choose a color")


        weekdays = request.args.getlist('weekday')
        if weekdays:
            days_select = ""
            for day in weekdays:
                day = str(day)
                days_select = days_select + day + ","
        else:
            days_select = "1,2,3,4,5,6,7,"


        start_month = int(request.args.get("start_month"))
        start_day = int(request.args.get("start_day"))
        start_year = int(request.args.get("start_year"))

        ende_day = (request.args.get("ende_day"))
        ende_month = (request.args.get("ende_month"))
        ende_year = (request.args.get("ende_year"))

        if not ende_day or not ende_month or not ende_year:
            ende_day = 14
            ende_month = 2
            ende_year = 2103

        ende_day = int(ende_day)
        ende_month = int(ende_month)
        ende_year = int(ende_year)


        if ende_month > 12:
            return apology("Please choose a valid month")

        if ende_month == 2 and ende_day > 28:
            return apology("February has only 28 days")

        if ende_month == 1 or ende_month == 3 or ende_month == 5 or ende_month == 7 or ende_month == 8 or ende_month == 10 or ende_month == 12:
            if ende_day > 31:
                return apology("This month has only 31 days")

        if ende_month == 4 or ende_month == 6 or ende_month == 9 or ende_month == 11:
            if ende_day > 30:
                return apology("This month has only 30 days")

        if ende_year < 2023:
            return apology("Choose a valid year")

        if start_day > ende_day:
            if start_month >= ende_month:
                if start_year == ende_year:
                    return apology("Please don't travel into the past")

        if start_month > ende_month:
            if start_year == ende_year:
                return apology("Please don't travel into the past")

        db.execute("UPDATE habits SET name = ?, description = ?, color = ?, ende_month = ?, ende_day = ?, ende_year = ?, weekdays = ? WHERE id = ?", name, description, color, ende_month, ende_day, ende_year, days_select, habit_id)
        return redirect("/")


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    habit_id = request.form.get("habit_id")
    db.execute("DELETE FROM days WHERE habit_id=?", habit_id)
    db.execute("DELETE FROM habits WHERE id=?", habit_id)
    return redirect("/")


@app.route("/email", methods=["POST"])
@login_required
def signup():
    user_id = session["user_id"]
    email = request.form.get("email")

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    def check(email):
        if(re.fullmatch(regex, email)):
            return True
        else:
            return False

    if (check(email) == True):
        db.execute("UPDATE users SET email=? WHERE id=?", email, user_id)
    else:
        email = "Email fail"

    return redirect(url_for('homepage', email=email)) #ked pouzivam url_for v redirect funkcii, musim dat ako nazov routu nie route name ale main funkciu v tom route, in this case homepage()


@app.route('/habit', methods=['GET'])
@login_required
def get_habit_data():
    # Retrieve the habit data from the database
    user_id = session["user_id"]
    habit_id = request.args.get("id")
    mesiac = int(request.args.get('mesiac'))
    rok = int(request.args.get('rok'))

    data = []
    #TODO
    if mesiac == 2:
        for m in range(28):
            dataDict = db.execute("SELECT month, day, year, evaluation, name, color FROM days LEFT JOIN habits ON habits.id=days.habit_id WHERE (habits.user_id = ? AND habit_id = ? AND month=? AND day=? AND year=?)", user_id, habit_id, mesiac, m, rok)
            if len(dataDict) == 0:
                dataDict.append("No record for this day")
            data.append(dataDict)
    elif mesiac == 2 or 4 or 6 or 9 or 11:
        for m in range(30):
            dataDict = db.execute("SELECT month, day, year, evaluation, name, color FROM days LEFT JOIN habits ON habits.id=days.habit_id WHERE (habits.user_id = ? AND habit_id = ? AND month=? AND day=? AND year=?)", user_id, habit_id, mesiac, m, rok)
            if len(dataDict) == 0:
                dataDict.append("No record for this day")
            data.append(dataDict)
    elif mesiac == 1 or 3 or 5 or 7 or 8 or 10 or 12:
        for m in range(31):
            dataDict = db.execute("SELECT month, day, year, evaluation, name, color FROM days LEFT JOIN habits ON habits.id=days.habit_id WHERE (habits.user_id = ? AND habit_id = ? AND month=? AND day=? AND year=?)", user_id, habit_id, mesiac, m, rok)
            if len(dataDict) == 0:
                dataDict.append("No record for this day")
            data.append(dataDict)
    #appendnut dictionary do listu


    # Return the data in JSON format
    return jsonify(data)

@app.route("/getcolor", methods=["GET"])
@login_required
def get_color():
    user_id = session["user_id"]
    habit_id = request.args.get("habit_id")
    color = db.execute("SELECT color FROM habits WHERE (user_id=? AND id=?)", user_id, habit_id)
    color = color[0]["color"]
    color = str(color)
    return color


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


