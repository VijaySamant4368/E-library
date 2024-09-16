import io
import os

import datetime

from cs50 import SQL
from flask import Flask, abort, flash, make_response, redirect, render_template, request, send_file, session
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
def shelf():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    # try:    
    if True:
        owned_books = db.execute("SELECT * FROM owners WHERE owner_id = ?", user_id)
        
        shelf = []
        for book in owned_books:
            book_details = dict()
            book_details["name"] == book["name"]
            book_details["author"] == book["author"]
            book_details["genre"] == list( book["genre"] )
            shelf.append(book_details)
    # except RuntimeError:    #no such column: id (The user doen't own anything )
    #     db.execute ("INSERT INTO owners (owner_id, book_id) values (?, 0);", user_id)
    #     shelf = [ {"name": "None", "author": "", "genre": list() } ]

    return render_template("shelf.html", username = user["username"], shelf= shelf)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        search = request.args["book_search"]
        searched_books = db.execute ("SELECT * FROM books WHERE name LIKE ?",  "%"+search+"%")
        books = []
        for book in searched_books:
            temp_book = dict()
            temp_book["name"] = book["name"]
            temp_book["author"] = getBookAuthor(book["id"])
            temp_book["genre"] = getBookGenre(book["id"])
            temp_book["uploader"] = db.execute("SELECT * FROM users WHERE id = ?", book["uploader_id"])[0]
            temp_book["id"] = book["id"]  # Will need the book ID to fetch the image

            books.append(temp_book)
            
        return render_template("search.html", books = books)
        # return "<img src='data:image/jpeg;base64, " + base64.b64encode(uploaded_file.read()).decode('ascii') + "'>"


@app.route("/cover/<int:book_id>")
def cover(book_id):
    
    book_data = db.execute("SELECT cover FROM books WHERE id = ?", (book_id,))[0]

    if book_data is None:
        abort(404)  # Image not found

    return send_file(
        io.BytesIO(book_data['cover']),
        mimetype='image/jpeg'  # Adjust mime type based on your image format
    )

@app.route("/book/<int:book_id>")
def book(book_id):
    
    book_data = db.execute("SELECT book FROM books WHERE id = ?", (book_id,))[0]

    if book_data is None:
        abort(404)  # book not found

    response = make_response(io.BytesIO(book_data['book']))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % 'yourfilename'
    return response

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    user_id = session["user_id"]
    if request.method == "POST":
        name = request.form.get("name")
        author_list = request.form.getlist("author")
        genre_list = request.form.getlist("genre")
        addGenres(genre_list)
        addAuthors(author_list)

        cover = request.files.get("cover")
        book = request.files.get("book")
        binary_cover = cover.read()
        binary_book = book.read()
        
        db.execute("INSERT INTO books(name, book, cover, uploader_id) VALUES (?, ?, ?, ?);", 
                                                name,  binary_book, binary_cover, user_id)
        book_id = db.execute("SELECT * FROM books ORDER BY id DESC LIMIT 1;")[0]["id"]
        addGenresToBook(genre_list, book_id)
        addAuthorsToBook(author_list, book_id)
        return render_template("upload.html", message=f"Book name: {name}, by {author_list}, of genre {genre_list}")
    
    elif request.method == "GET":
        genres = db.execute("SELECT * FROM genres")
        authors = db.execute("SELECT * FROM authors")
        return render_template("upload.html", message="", genres = genres, authors = authors )



# @app.route("/history")
# @login_required
# def history():
#     """Show history of transactions"""
#     user_id = session["user_id"]
#     history = []
#     transctions = db.execute("SELECT * FROM history WHERE user_id = ?;", user_id)
#     for transction in transctions:
#         action = db.execute("SELECT * FROM TRANSACTION_ACTIVITY WHERE id = ?", transction["action"]) [0] ["action"]
#         symbol = transction["symbol"]
#         quantity = transction["quantity"]
#         price = usd(transction["price"])
#         time = transction["date_time"]

#         history. append( { "action" : action , "symbol" : symbol, "quantity" : quantity, "price" : price, "time" : time })

#     return render_template("history.html", history = history)


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


# @app.route("/quote", methods=["GET", "POST"])
# @login_required
# def quote():
#     """Get stock quote."""
#     if request.method=="POST":
#         symbol = request.form.get("symbol")
#         stock = lookup(symbol)
#         if stock:
#             return render_template("quote.html", result="price of one share of "+stock["symbol"]+" is "+usd(stock["price"]))
#         else:
#             return apology("invalid symbol", 400)
#     else:
#         return render_template("quote.html", result="")
#     # return apology("TODO")


# @app.route("/buy", methods=["GET", "POST"])
# @login_required
# def buy():
#     """Buy shares of stock"""
#     if request.method=="POST":
#         symbol = request.form.get("symbol")
#         if not symbol:
#             return apology("missing symbol", 400)

#         try:
#             quantity=int(request.form.get("shares") )
#         except:
#             return apology("invalid number of shares", 400)
#         if(quantity<1):
#             return apology("invalid number of shares", 400)

#         stock=lookup(symbol)
#         if not stock:
#             return apology("invalid symbol", 400)

#         ###LOGIC FOR ADDING DATA TO A NEW DATABASE AND DEDUCTINGG MONEY
#         price = stock["price"]
#         total = price*quantity
#         user_id = session["user_id"]
#         balance = db.execute("SELECT cash FROM users WHERE id=?", user_id)[0]["cash"]
#         if total>balance:
#             return apology("Not enough cash in balance", 400)

#         owned_qunatity = db.execute("SELECT quantity  FROM stocks WHERE user_id=? AND symbol=? ", user_id, symbol)
#         db.execute("UPDATE users SET cash=? WHERE id=?", balance-total, user_id)

#         if owned_qunatity:
#             db.execute("UPDATE stocks SET quantity=? WHERE user_id=? AND symbol=?", owned_qunatity[0]["quantity"]+quantity, user_id, symbol)
#         else:
#             db.execute("INSERT INTO stocks(user_id, symbol, quantity) VALUES (?,?,?)", user_id, symbol, quantity )

#         # action 1 == Buy
#         import datetime
#         db.execute("INSERT INTO history(user_id, symbol, quantity, price, action, date_time) VALUES (?,?,?,?, 1, ?);", user_id, symbol, quantity, price, datetime.datetime.now())

#         return redirect("/")
#     else:
#         return render_template("buy.html", message="")

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


# @app.route("/sell", methods=["GET", "POST"])
# @login_required
# def sell():
#     """Sell shares of stock"""
#     if request.method == "POST":
#         symbol = request.form.get("symbol")
#         if not symbol:
#             return apology("missing symbol", 400)

#         try:
#             quantity=int(request.form.get("shares") )
#         except:
#             return apology("invalid number of shares", 400)
#         if(quantity<1):
#             return apology("invalid number of shares", 400)

#         user_id = session["user_id"]

#         owned_qunatity = db.execute("SELECT * FROM stocks WHERE user_id = ? AND symbol = ?", user_id, symbol)
#         if ( len(owned_qunatity)==0 or owned_qunatity[0]["quantity"]<quantity):
#             return apology("Not Enough number of shares", 400)

#         #symbol would be valid since it was there in the useer's bought shares
#         price = lookup(symbol)["price"]
#         total = price*quantity
#         owned_cash = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["cash"]
#         db.execute("UPDATE users SET cash = ? WHERE id = ?", owned_cash+total, user_id)
#         db.execute("UPDATE stocks SET quantity = ? WHERE user_id = ? AND symbol=?", owned_qunatity[0]["quantity"]-quantity, user_id, symbol)

#         # action 2 == Sell
#         db.execute("INSERT INTO history(user_id, symbol, quantity, price, action, date_time) VALUES (?,?,?,?, 2, ?);", user_id, symbol, quantity, price, datetime.datetime.now())

#         return redirect("/")

#     else:
#         stocks=[]
#         user_stocks= db.execute("SELECT * FROM stocks WHERE user_id  = ?", session["user_id"])
#         for stock in user_stocks:
#             stocks.append(stock["symbol"])
#         return render_template("sell.html", symbols = stocks)

def addGenres(genre_list:list[str]) ->None:
    print(genre_list)
    old_genres = db.execute("SELECT name FROM genres;")
    old_genre_list = []
    for old_genre in old_genres:
        old_genre_list.append(old_genre["name"])
    for genre in genre_list:
        if genre.strip().lower() not in old_genre_list and genre.strip().lower():
            db.execute ("INSERT INTO genres(name) VALUES (?)", genre)
            old_genre_list += genre 

def addGenresToBook(genre_list:list[str], book_id:int)  -> None:
    for genre in genre_list:
        if not genre:   #if Whitespace
            continue
        genre_id = db.execute("SELECT id FROM genres WHERE name = ?;", genre)[0]["id"]
        db.execute("INSERT INTO bookGenres(book_id, genre_id) VALUES (? ,?);", book_id, genre_id)

def getBookGenre(book_id:int)   -> list[str]:
    genre_table = db.execute("SELECT name FROM genres WHERE id IN (SELECT genre_id FROM bookGenres WHERE book_id = ?);", book_id)
    #if no genre mentioned, table bookGenres won't have any value
    if not genre_table:
        return ["Genre not mentioned"]

    genre_list = []
    for genre_row in genre_table:
        genre_list.append(genre_row["name"])
    return genre_list
    
def getBooksByAuthor(author_id_list:list[int]):
    books_id = []
    for author_id in author_id_list:
        books_table = db.execute("SELECT id FROM books WHERE author_id = ?;", author_id)
        for books_row in books_table:
            books_id.append(books_row[id])
    return books_id

def addAuthors(author_list:list[str]) ->None:
    """
    Adds unknown authors to table of authors
    """
    print(author_list)
    old_authors = db.execute("SELECT name FROM authors;")
    old_author_list = []
    for old_author in old_authors:
        old_author_list.append(old_author["name"])
    for author in author_list:
        if author.strip().lower() not in old_author_list and author.strip().lower():
            db.execute ("INSERT INTO authors(name) VALUES (?)", author)
            old_author_list += author 
    
def addAuthorsToBook(author_list:list[str], book_id:int)  -> None:
    for author in author_list:
        if not author:   #if Whitespace
            continue
        author_id = db.execute("SELECT id FROM authors WHERE name = ?;", author)[0]["id"]
        db.execute("INSERT INTO bookAuthors(book_id, author_id) VALUES (? ,?);", book_id, author_id)

def getBookAuthor(book_id:int)  -> list[str]:
    author_table = db.execute("SELECT name FROM authors WHERE id IN (SELECT author_id FROM bookAuthors WHERE book_id = ?);", book_id)
    #if no author mentioned, table bookauthors won't have any value
    if not author_table:
        return ["author not mentioned"]

    author_list = []
    for author_row in author_table:
        author_list.append(author_row["name"])
    return author_list