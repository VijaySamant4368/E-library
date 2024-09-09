import os

import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required #Commented this so that I don't have to login again and again
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    owned_books = db.execute("SELECT * FROM owners WHERE id = ?", user_id)

    shelf = []


    return render_template("index.html", username = user["username"], stocks= owned_stocks)

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    history = []
    transctions = db.execute("SELECT * FROM history WHERE user_id = ?;", user_id)
    for transction in transctions:
        action = db.execute("SELECT * FROM TRANSACTION_ACTIVITY WHERE id = ?", transction["action"]) [0] ["action"]
        symbol = transction["symbol"]
        quantity = transction["quantity"]
        price = usd(transction["price"])
        time = transction["date_time"]

        history. append( { "action" : action , "symbol" : symbol, "quantity" : quantity, "price" : price, "time" : time })

    return render_template("history.html", history = history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)



        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", message="")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method=="POST":
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        if stock:
            return render_template("quote.html", result="price of one share of "+stock["symbol"]+" is "+usd(stock["price"]))
        else:
            return apology("invalid symbol", 400)
    else:
        return render_template("quote.html", result="")
    # return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method=="POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("missing symbol", 400)

        try:
            quantity=int(request.form.get("shares") )
        except:
            return apology("invalid number of shares", 400)
        if(quantity<1):
            return apology("invalid number of shares", 400)

        stock=lookup(symbol)
        if not stock:
            return apology("invalid symbol", 400)

        ###LOGIC FOR ADDING DATA TO A NEW DATABASE AND DEDUCTINGG MONEY
        price = stock["price"]
        total = price*quantity
        user_id = session["user_id"]
        balance = db.execute("SELECT cash FROM users WHERE id=?", user_id)[0]["cash"]
        if total>balance:
            return apology("Not enough cash in balance", 400)

        owned_qunatity = db.execute("SELECT quantity  FROM stocks WHERE user_id=? AND symbol=? ", user_id, symbol)
        db.execute("UPDATE users SET cash=? WHERE id=?", balance-total, user_id)

        if owned_qunatity:
            db.execute("UPDATE stocks SET quantity=? WHERE user_id=? AND symbol=?", owned_qunatity[0]["quantity"]+quantity, user_id, symbol)
        else:
            db.execute("INSERT INTO stocks(user_id, symbol, quantity) VALUES (?,?,?)", user_id, symbol, quantity )

        # action 1 == Buy
        import datetime
        db.execute("INSERT INTO history(user_id, symbol, quantity, price, action, date_time) VALUES (?,?,?,?, 1, ?);", user_id, symbol, quantity, price, datetime.datetime.now())

        return redirect("/")
    else:
        return render_template("buy.html", message="")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        if(not username):
            return apology("must provide username", 400)
        if(not password):
            return apology("must provide password", 400)
        if(password != confirm):
            return apology("passwords does not match", 400)

        hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users(username, hash)  VALUES(?, ?)", username, hash)   #Will raise error if duplicate username
        except:
            return apology("username already exists", 400)

        # # Redirect user to home page
        # return redirect("/")          # def index() has '@login required' so it redirects to login page WILL CORRECT LATER(try to)
        return render_template("login.html", message="Registered Successfully!!! Now login with the username and password you just provided")

    else:       #GET, i.e. display
        return render_template("register.html", message="")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("missing symbol", 400)

        try:
            quantity=int(request.form.get("shares") )
        except:
            return apology("invalid number of shares", 400)
        if(quantity<1):
            return apology("invalid number of shares", 400)

        user_id = session["user_id"]

        owned_qunatity = db.execute("SELECT * FROM stocks WHERE user_id = ? AND symbol = ?", user_id, symbol)
        if ( len(owned_qunatity)==0 or owned_qunatity[0]["quantity"]<quantity):
            return apology("Not Enough number of shares", 400)

        #symbol would be valid since it was there in the useer's bought shares
        price = lookup(symbol)["price"]
        total = price*quantity
        owned_cash = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["cash"]
        db.execute("UPDATE users SET cash = ? WHERE id = ?", owned_cash+total, user_id)
        db.execute("UPDATE stocks SET quantity = ? WHERE user_id = ? AND symbol=?", owned_qunatity[0]["quantity"]-quantity, user_id, symbol)

        # action 2 == Sell
        db.execute("INSERT INTO history(user_id, symbol, quantity, price, action, date_time) VALUES (?,?,?,?, 2, ?);", user_id, symbol, quantity, price, datetime.datetime.now())

        return redirect("/")

    else:
        stocks=[]
        user_stocks= db.execute("SELECT * FROM stocks WHERE user_id  = ?", session["user_id"])
        for stock in user_stocks:
            stocks.append(stock["symbol"])
        return render_template("sell.html", symbols = stocks)


