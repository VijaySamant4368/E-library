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
        owned_books = db.execute("SELECT * FROM books WHERE id in (SELECT book_id FROM owners WHERE owner_id = ?);", user_id)
        print(len(owned_books))
        shelf = getBooksDetails(owned_books)
    # except RuntimeError:    #no such column: id (The user doen't own anything )
    #     db.execute ("INSERT INTO owners (owner_id, book_id) values (?, 0);", user_id)
    #     shelf = [ {"name": "None", "author": "", "genre": list() } ]

    return render_template("shelf.html", username = user["username"], shelf= shelf)

@app.route("/my-uploads")
@login_required #Commented this so that I don't have to login again and again
def myUploads():
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    # try:    
    if True:
        owned_books = db.execute("SELECT * FROM books WHERE id in (SELECT book_id FROM owners WHERE owner_id = ?);", user_id)
        print(len(owned_books))
        uploaded_books = getBooksDetails(owned_books)

    return render_template("myUploads.html", username = user["username"], uploaded_books= uploaded_books)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        search = request.args["book_search"]
        searched_books = db.execute ("SELECT * FROM books WHERE name LIKE ?",  "%"+search+"%")
        books = getBooksDetails(searched_books)
            
        return render_template("search.html", books = books, message =  f"Showing results for query '{search}'")
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

@app.route("/author/<int:author_id>")
def author(author_id):
    author_name = db.execute("SELECT name FROM authors WHERE id = ?;", author_id)[0]["name"]
    
    searched_books = db.execute("SELECT * FROM books WHERE id in (SELECT book_id FROM bookAuthors WHERE author_id = ?);", (author_id,))

    if searched_books is None:
        abort(404)  # book not found

        
    books = getBooksDetails(searched_books)

    return render_template("search.html", books = books, message =  f"Showing results for Author '{author_name}'")

@app.route("/genre/<int:genre_id>")
def genre(genre_id):
    genre_name = db.execute("SELECT name FROM genres WHERE id = ?;", genre_id)[0]["name"]
    searched_books = db.execute("SELECT * FROM books WHERE id in (SELECT book_id FROM bookGenres WHERE genre_id = ?);", (genre_id,))

    if searched_books is None:
        abort(404)  # book not found

        
    books = getBooksDetails(searched_books)

    return render_template("search.html", books = books, message = f"Showing results for Genre '{genre_name}'")

@app.route("/owner/<int:owner_id>")
def owner(owner_id):
    owner_name = db.execute("SELECT username FROM users WHERE id = ?;", owner_id)[0]["username"]
    searched_books = db.execute("SELECT * FROM books WHERE id in (SELECT book_id FROM owners WHERE owner_id = ?);", owner_id)

    if searched_books is None:
        abort(404)  # book not found

        
    books = getBooksDetails(searched_books)

    print(len(books))

    return render_template("search.html", books = books, message = f"Showing results for books uploaded by '{owner_name}'")

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
        print("book id: ", book_id, "\nuser_id: ", user_id)
        db.execute("INSERT INTO owners(owner_id, book_id) VALUES(?, ?);", user_id, book_id)
        return render_template("upload.html", message=f"Book name: {name}, by {author_list}, of genre {genre_list}")
    
    elif request.method == "GET":
        genres = db.execute("SELECT * FROM genres")
        authors = db.execute("SELECT * FROM authors")
        return render_template("upload.html", message="", genres = genres, authors = authors )




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


def addGenres(genre_list:list[str]) ->None:
    """Add unknown genres to the list of authors, firstly checking if they are not already there

    Args:
        genre_list (list[str]): The list of known and unknown genres
    """
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
    """Inserts "book_id" and all the corresponding "genre_id"(s) into the table "boookGenres"

    Args:
        genre_list (list[str]): The list of name of the genre(s)
        book_id (int): The id of the book
    """
    for genre in genre_list:
        if not genre:   #if Whitespace
            continue
        genre_id = db.execute("SELECT id FROM genres WHERE name = ?;", genre)[0]["id"]
        db.execute("INSERT INTO bookGenres(book_id, genre_id) VALUES (? ,?);", book_id, genre_id)

def getBookGenre(book_id:int)   -> list[str]:
    """Returns a list of all genres of a given book. If no genre mentioned, returns [{"name": "genre not mentioned", "id":0}]

    Args:
        book_id (int): The id of the book whose authors are required

    Returns:
        list[dict]: List of dict of all the genres, with key 'name' as the name of the genre, and 'id' as the genre id
    """
    genre_table = db.execute("SELECT name,id FROM genres WHERE id IN (SELECT genre_id FROM bookGenres WHERE book_id = ?);", book_id)
    #if no genre mentioned, table bookGenres won't have any value
    if not genre_table:
        return [{"name": "genre not mentioned", "id":0}]

    genre_list = []
    for genre_row in genre_table:
        genre_details = dict()
        genre_details["name"] = genre_row["name"]
        genre_details["id"] = genre_row["id"]
        genre_list.append(genre_details)
    return genre_list
    
def getBooksByAuthor(author_id_list:list[int])  -> list[id]:
    """Returns list of book_id(s) by given authors

    Args:
        author_id_list (list[int]): The list of the author_id(s)

    Returns:
        list[id]: List of book_id(s) by given author(s)
    """
    books_id = []
    books_table = db.execute("SELECT id FROM books WHERE author_id IN (?);", author_id_list)
    for books_row in books_table:
        books_id.append(books_row[id])
    return books_id

def addAuthors(author_list:list[str]) ->None:
    """Add unknown authors to the list of authors, firstly checking if they are not already there

    Args:
        author_list (list[str]): The list of known and unknown authors
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
    """Insert "book_id" and all the corresponding "author_id"(s) into the table "boookAuthors"

    Args:
        author_list (list[str]): The list of name of the author(s)
        book_id (int): The id of the book
    """
    for author in author_list:
        if not author:   #if Whitespace
            continue
        author_id = db.execute("SELECT id FROM authors WHERE name = ?;", author)[0]["id"]
        db.execute("INSERT INTO bookAuthors(book_id, author_id) VALUES (? ,?);", book_id, author_id)

def getBookAuthor(book_id:int)  -> list[dict]:
    """Returns a list of all authors of a given book. If no author mentioned, returns [{"name": "author not mentioned", "id":0}]

    Args:
        book_id (int): The id of the book whose authors are required

    Returns:
        list[dict]: List of dict of all the authors, with key 'name' as the name of the author, and 'id' as the author id
    """
    author_table = db.execute("SELECT name, id FROM authors WHERE id IN (SELECT author_id FROM bookAuthors WHERE book_id = ?);", book_id)
    #if no author mentioned, table bookauthors won't have any value
    if not author_table:
        return [{"name": "author not mentioned", "id":0}]

    author_list = []
    for author_row in author_table:
        author_details = dict()
        author_details["name"] = author_row["name"]
        author_details["id"] = author_row["id"]
        author_list.append(author_details)
    return author_list

def getBookOwner(uploader_id:int)   -> dict:
    """Returns a dict with uploader details

    Args:
        uploader_id (int): The id of the uploader

    Returns:
        dict: dict with 'name' as the username of the uploader and 'id' as the id of the user
    """
    owner = db.execute("SELECT * FROM users WHERE id = ?", uploader_id)[0]
    owner_name = db.execute("SELECT username FROM users WHERE id = ?;", uploader_id)[0]["username"]
    return {"name": owner_name, "id": owner["id"]}


def getBooksDetails(searched_books:list[dict]) -> list[dict]:
    """Given a list of books, returns a list of dicts with required format to be passed to HTML

    Args:
        searched_books (list[dict]): List of dicts of different books, with basic infos from the books Table

    Returns:
        list[dict]: List of dicts of books with advance details
    """
    books = []
    for book in searched_books:
        temp_book = dict()
        temp_book["name"] = book["name"]
        temp_book["author"] = getBookAuthor(book["id"])
        temp_book["genre"] = getBookGenre(book["id"])
        temp_book["uploader"] = getBookOwner(book["uploader_id"])
        temp_book["id"] = book["id"]  # Will need the book ID to fetch the image

        books.append(temp_book)
    return books