import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime, timedelta


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


#################################################################################################################################################################
#################################################################################################################################################################
## pojde to??? 
## kto vie 

@app.route("/skuska")
def skuska():
    return render_template("skuska.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def homepage():
    """ Main page """
    # Habits overview
    user_id = session["user_id"]

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
            return apology("This username is already taken")

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
            sprava = 1
            return redirect("/login")

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

    db.execute("INSERT INTO habits (user_id, name, description, color, start_month, start_day, start_year, ende_month, ende_day, ende_year, expiration) VALUES (?,?,?,?,?,?,?,?,?,?,?)", user_id, name, description, color, start_month, start_day, start_year, end_month, end_day, end_year, expiration)
    return redirect("/")



@app.route("/day", methods=["GET", "POST"])
@login_required
def newday():
    user_id = session["user_id"]

    den = int(request.args.get("day"))
    mesiac = int(request.args.get("month"))
    rok = int(request.args.get("year"))

    if (request.method == "POST"):

        den = request.form.get("day")
        mesiac = request.form.get("month")
        rok = request.form.get("year")

        habit_id = request.form.get("habit_id")
        notes = request.form.get("notes")
        evaluation = request.form.get("evaluation")
        evaluation = int(evaluation)
        print(evaluation)

        db.execute("UPDATE days SET pozn=?, evaluation=? WHERE (month = ? AND day = ? AND year = ? AND  habit_id = ?)", notes, evaluation, mesiac, den, rok, habit_id)

        habits = db.execute("SELECT * FROM habits JOIN days ON habits.id = days.habit_id WHERE (days.user_id=? AND month=? AND day=? AND year=?)", user_id, mesiac, den, rok)
        return render_template("day.html", den=den, mesiac=mesiac, rok=rok, habits=habits)


    if mesiac > 12:
        mesiac = 1
        rok += 1

    if mesiac < 1:
        mesiac = 12
        rok -= 1




    # vybrat len tie habit ids, ktore este neexpirovali                   start
    habits_ids = db.execute("SELECT id FROM habits WHERE (user_id = ? AND ( ( (start_year < ?) OR ( start_month < ? AND start_year == ?) OR (  start_day < ? AND start_month <= ? AND start_year == ? ) ) ) )", user_id, rok, mesiac, rok, den, mesiac, rok) # vsetky habit ids daneho usera

    days_skuska = db.execute("SELECT * FROM days WHERE (user_id=? AND month=? AND day=? AND year=?)", user_id, mesiac, den, rok) # vsetky records na dany den daneho usera; ak riadkov bude menej ako habits_ids, znamena to, ze tak chyba riadok niektoreho habitu

    if len(days_skuska) != len(habits_ids):
        for n in habits_ids:
            n = n["id"]
            skuska = db.execute("SELECT habit_id FROM days WHERE (user_id=? AND month=? AND day=? AND year=? AND habit_id=?)", user_id, mesiac, den, rok, n)
            if len(skuska) == 0:
                db.execute("INSERT INTO days (user_id, habit_id, month, day, year) VALUES (?,?,?,?,?)", user_id, n, mesiac, den, rok)

    # najprv tabulka kde budu vsetky habits daneho usera, pricom start_date musi byt mensi a ende_date vacsi ako current date
    habits = db.execute("SELECT * FROM (SELECT * FROM habits LEFT JOIN days ON habits.id = days.habit_id) WHERE (user_id=? AND month=? AND day=? AND year=? )", user_id, mesiac, den, rok)

    return render_template("day.html", den=den, mesiac=mesiac, rok=rok, habits=habits)


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
        habit_name = request.form.get("habit_name")
        habit_description = request.form.get("habit_description")
        color = request.form.get("color_val")
        print(user_id, start_month, start_day, start_year, habit_name, habit_description, color)
        return render_template("edit.html", start_month=start_month, start_day=start_day, start_year=start_year, habit_id=habit_id, habit_name=habit_name, habit_description=habit_description, color=color, ende_month=ende_month, ende_day=ende_day, ende_year=ende_year)

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

        '''

        if ende_year < 2023:
            return apology("Choose a valid year")

        if start_day > ende_day:
            if start_month >= ende_month:
                if start_year == ende_year:
                    return apology("Please don't travel into the past")

        if start_month > ende_month:
            if start_year == ende_year:
                return apology("Please don't travel into the past")
        '''

        db.execute("UPDATE habits SET name = ?, description = ?, color = ?, ende_month = ?, ende_day = ?, ende_year = ? WHERE id = ?", name, description, color, ende_month, ende_day, ende_year, habit_id)
        return redirect("/")

@app.route("/delete", methods=["POST"])
@login_required
def delete():
    habit_id = request.form.get("habit_id")
    print(habit_id)
    print(type(habit_id))
    db.execute("DELETE FROM days WHERE habit_id=?", habit_id)
    db.execute("DELETE FROM habits WHERE id=?", habit_id)
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


