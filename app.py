"""
My website uses two kinds of users, 'Customers' and 'Administrators'.
Choose Register on the main page in order to register as a 'Customer'.
To login as an administrator, the user name is 'shopkeeper', password is 'qwerty'

An additional two 'Customers', 'k' and 'j' have been pre-inserted.
'j' is a fresh user, with no cart or orders.
'k' has a pre-filled cart, and 1 previous order to showcase interaction with the database.
Password for 'k' is '12'.  Password for 'j' is '12'.

If a 'Customer' headed to the checkout with a filled cart but never clicked on 'Pay Now',
The cart is saved until the user heads to the checkout again.
Cart details also update if the database is updated.
Price changes apply to old carts and old cart items with no corresponding book id are removed.

Discounts will be applied to logged in users for every 2nd order.
Discounts are set at 10% off to all items.
"""
from flask import Flask, render_template, request, make_response, session, redirect, url_for, g
from flask_session import Session
from forms import BookForm, LoginForm, RegistrationForm, SearchForm, CartForm, CheckoutForm, AddBookForm, OrderForm, AccountForm
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__) 
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"]= "secret-key"
app.config["SESSION_PERMANENT"]= False 
app.config["SESSION_TYPE"]= "filesystem" 
Session(app)


#obtains global variable for user id. can use in jinja without redefining it
#function activates before all functions
@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id", None)
    g.current_date = datetime.now().strftime("%Y-%m-%d")

#restricts routes to have logins
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(**kwargs)
    return wrapped_view


#----------------------------LOGIN FUNCTIONS----------------------------#
#register user
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id=form.user_id.data
        password=form.password.data
        password2 = form.password2.data
        db=get_db()

        possible_clashing_user = db.execute("""SELECT * FROM users
                                            WHERE user_id=?;""",(user_id,)).fetchone()
        if possible_clashing_user != None:
            form.user_id.errors.append("User id already taken!")
        else:
            #insert doesn't return db
            db.execute("""INSERT INTO users (user_id, password)
                            Values (?,?)""",(user_id, generate_password_hash(password),))
            #commit insertion to modify it
            db.commit()
            return redirect(url_for("login"))

    return render_template("register.html", form=form)

#login user
@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id=form.user_id.data
        password=form.password.data
        db=get_db()

        matching_user = db.execute("""SELECT * FROM users
                                            WHERE user_id=?;""",(user_id,)).fetchone()

    #checks for valid user input
        #check if user_id inside database                                    
        if matching_user == None:
            form.user_id.errors.append("Unknown User")
        #check if password is valid/exists for user
        elif not check_password_hash(matching_user["password"], password):
            form.user_id.errors.append("Password Incorrect")

    #once valid, store user id
        else:
            session["user_id"]=user_id
            
            db=get_db()
            admin = db.execute("""SELECT *
                                FROM admins
                                WHERE user_id = ?;""", (session["user_id"],)).fetchone()
            if admin != None:
                session["admin"]=True

            #allows next loaded page to be the one you tried to visit
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("books")
            return redirect(next_page)


    return render_template("login.html", form=form)

#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("books"))


#-----------------------------------------------------------------------------#


#----------------------------BOOK SEARCH FUNCTIONS----------------------------#

#index of all books
@app.route("/", methods=["GET", "POST"])
@app.route("/books", methods=["GET", "POST"])
def books():
    form=SearchForm()
    form.genre_search.choices = get_genres()
    form.genre_search.choices.insert(0, ("", "All"))
    #generate cart on visit
    if "cart" not in session:
        session["cart"] = {}
    #generate admin status on visit
    if "admin" not in session:
        session["admin"] = False

    books=None
    db=get_db()
    
    #create table upon loading
    books=db.execute("""SELECT * 
        FROM authors JOIN books
        ON books.author_id=authors.author_id
        ORDER BY books.title ASC;""").fetchall()

    if form.validate_on_submit():
        genre=form.genre_search.data
        #title can never be an empty string, as %% is always concatenated to it
        title="%"+form.title_search.data.strip()+"%"
       
    #genre filled, title filled
    #need Distinct here to prevent genre from creating duplicates
        if genre != "":
            books=db.execute("""SELECT DISTINCT books.title, authors.name, books.price, books.description, books.book_id
                                FROM authors 
                                JOIN books
                                JOIN genres
                                ON authors.author_id = books.author_id
                                AND genres.book_id = books.book_id
                                WHERE genre_name = ?
                                AND title LIKE ?
                                ORDER BY books.title ASC;""",(genre,title)).fetchall()

    #genre empty, title filled
        elif genre == "":
            books=db.execute("""SELECT DISTINCT books.title, authors.name, books.price, books.description, books.book_id
                                FROM authors 
                                JOIN books
                                JOIN genres
                                ON authors.author_id = books.author_id
                                AND genres.book_id = books.book_id
                                WHERE title LIKE ?
                                ORDER BY books.title ASC;""",(title,)).fetchall()

    return render_template("books.html", books=books, form=form, discount=discount())

#add books to db
@app.route("/add_book", methods=["GET","POST"])
def add_book():
    form=AddBookForm()
    db=get_db()
    message=""
    form.book_author.choices = get_authors()
    form.book_genre.choices = get_genres()

    if form.validate_on_submit():
        title=form.book_title.data
        author=form.book_author.data
        price=float(form.book_price.data)
        desc=form.book_desc.data
        check=db.execute("""SELECT title 
                            FROM books
                            JOIN authors
                            ON books.author_id = authors.author_id
                            WHERE books.title = ?
                            AND authors.author_id = ?;""",(title, author,)).fetchone()
        if check == None:
            #store new book
            db.execute("""INSERT INTO books (author_id, title, price, description)
                        VALUES (?,?,?,?);""",
                        (author, title, price, desc,))
            db.commit()

            #get book_id to add genres of new book
            book_id=db.execute("""SELECT book_id
                                FROM books
                                WHERE author_id = ?
                                AND title = ?;""",(author, title,)).fetchone()
            
            #each genre stored in list
            for genre in form.book_genre.data:
                db.execute("""INSERT INTO genres (book_id, genre_name)
                            VALUES (?,?);""",
                            (book_id["book_id"], genre,))
                db.commit()

            message="Book Added to database"
        else:
            message="Book already exists"

    return render_template("add_book.html", form=form, message=message)

#get genre for searching
def get_genres():
    db = get_db()
    genre=[]
    genres = db.execute("""SELECT DISTINCT genre_name FROM genres 
                            ORDER BY genre_name ASC;""").fetchall()
    for types in genres:
        #types represent each row in genres
        genre.append( (types["genre_name"],types["genre_name"]) )
    return(genre)

#get authors
def get_authors():
    db=get_db()
    author=[]
    authors= db.execute("""SELECT *
                            FROM authors""").fetchall()
    for person in authors:
        author.append( (person["author_id"], person["name"]) )
    return(author)
    
#individual book
#includes ability to edit price
@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    form=BookForm()
    db=get_db()
    quantity=1
    cart_quantity=None
    if 'cart' in session: #if book_id of current book exists
        if book_id in session["cart"]:
            cart_quantity=session["cart"][book_id]["quantity"] #cart_quantity value assigned book's quantity

    book=db.execute("""SELECT DISTINCT books.title, authors.name, books.price, books.description
                        FROM authors 
                        JOIN books
                        JOIN genres
                        ON authors.author_id = books.author_id
                        AND genres.book_id = books.book_id
                        WHERE books.book_id = ?;""", (book_id,)).fetchone()

    genre=db.execute("""SELECT genres.genre_name
                        FROM books JOIN genres
                        ON books.book_id=genres.book_id
                        WHERE books.book_id = ?;""", (book_id,)).fetchall()

    genres = db.execute("""SELECT DISTINCT genre_name FROM genres 
                                ORDER BY genre_name ASC;""").fetchall()

    #shopkeeper functions
    if form.validate_on_submit() and session["admin"]:
       
        new_price = form.edit_price.data
        db.execute("""UPDATE books
                    SET price = ?
                    WHERE book_id = ?;""",(float(new_price), book_id,))
        db.commit()
            
        #recall database
        book=db.execute("""SELECT DISTINCT books.title, authors.name, books.price, books.description
                        FROM authors 
                        JOIN books
                        JOIN genres
                        ON authors.author_id = books.author_id
                        AND genres.book_id = books.book_id
                        WHERE books.book_id = ?;""", (book_id,)).fetchone()

        genre=db.execute("""SELECT genres.genre_name
                        FROM books JOIN genres
                        ON books.book_id=genres.book_id
                        WHERE books.book_id = ?;""", (book_id,)).fetchall()

        genres = db.execute("""SELECT DISTINCT genre_name FROM genres 
                                ORDER BY genre_name ASC;""").fetchall()


        #delete entry from db
        if form.delete_entry.data==True:
            db.execute("""DELETE FROM books
                    WHERE book_id = ?;""",(book_id,))
            db.commit()
            return redirect(url_for("books"))
      
    #Regular user function for buying a book
    elif form.validate_on_submit():
        quantity = form.quantity.data
       
       #for login required, use redirect(url_for()) to allow arguments to pass into add_to_cart function
        return redirect(url_for("add_to_cart", book_id=book_id, quantity=quantity, price=book["price"]))
        
    #allows boxes to contain previous data
    form.edit_price.data = book["price"]
        

    return render_template("book.html", form=form, book=book, cart_quantity=cart_quantity, genre=genre, genres=genres, discount=discount())
#-----------------------------------------------------------------------------#

#-----------------------------ACCOUNT/ADMIN FUNCTIONS----------------------------------#
#account details. password change.
@app.route("/account", methods=["POST","GET"])
def account():
    form = AccountForm()
    db=get_db()
    #clear any previous changes made 
    changes=[]
    
    if form.validate_on_submit():
        #fetch matching user
        matching_user = db.execute("""SELECT * FROM users
                                        WHERE user_id= ?;""",(g.user,)).fetchone()

        #user_id change
        new_user_id = form.new_user_id.data
        #password change
        old_password=form.old_password.data
        new_password=form.new_password.data

        #password must be entered for any account changes to occur
        #if password confirmation fails, error occurs
        if not check_password_hash(matching_user["password"], old_password):
            form.old_password.errors.append("Password Incorrect")
        else:
            #if change to id
            if new_user_id != "":
                #see if new_user_id already exists
                possible_clashing_user = db.execute("""SELECT * FROM users
                                                    WHERE user_id=?;""",(new_user_id,)).fetchone()

                #clashing user prevents password change from occuring
                if possible_clashing_user != None:
                    form.new_user_id.errors.append("Username  already taken!")
                    #clear name from input box after submit
                    form.new_user_id.data=""
                    return render_template("account.html", form=form, changes=changes)

                else:
                    #update that user_id across all databases
                    db.execute("""UPDATE users 
                                SET user_id = ?
                                WHERE user_id = ?;""",(new_user_id, g.user))
                    db.commit()
                    db.execute("""UPDATE cart
                                SET user_id = ?
                                WHERE user_id = ?;""",(new_user_id, g.user))
                    db.commit()
                    db.execute("""UPDATE orders 
                                SET user_id = ?
                                WHERE user_id = ?;""",(new_user_id, g.user))
                    db.commit()
                    changes.append("Username has been successfully changed")
                    session["user_id"]=new_user_id
                    g.user = session.get("user_id", None)

            #if changes to password
            if new_password != "":
                db.execute("""UPDATE users
                            SET password = ?
                            WHERE user_id = ?;""",(generate_password_hash(new_password), g.user,))
                db.commit()
                changes.append("Password has been successfully changed")
    
    #clear name from input box after submit
    form.new_user_id.data=""
    return render_template("account.html", form=form, changes=changes)

#fetch orders
@app.route("/orders", methods=["GET", "POST"])
def orders():
    form=OrderForm()
    db=get_db()

    #load table of all orders, if admin
    if session["admin"]:
        orders=db.execute("""SELECT orders.user_id AS user_id, 
                                    orders.book_id AS book_id,   
                                    books.title AS title, 
                                    orders.quantity AS quantity, 
                                    orders.price AS price,
                                    orders.date AS date
                            FROM orders JOIN books
                            ON books.book_id = orders.book_id
                            ORDER BY date DESC;""").fetchall()
    else:
        orders=db.execute("""SELECT books.title AS title, orders.book_id AS book_id,
                                    orders.quantity AS quantity, orders.price AS price,
                                    orders.date AS date
                            FROM orders JOIN books
                            ON books.book_id = orders.book_id
                            WHERE orders.user_id = ?
                            ORDER BY date DESC;""", (g.user,)).fetchall()

    if form.validate_on_submit():
        customer = form.customer_id.data
        if form.date.data == None:
            date = ""
        else:
            date = (form.date.data).strftime("%Y-%m-%d")

        if customer != "" and date != "":
            orders=db.execute("""SELECT orders.user_id AS user_id, 
                                    orders.book_id AS book_id,   
                                    books.title AS title, 
                                    orders.quantity AS quantity, 
                                    orders.price AS price,
                                    orders.date AS date
                                FROM orders JOIN books
                                ON books.book_id = orders.book_id
                                WHERE orders.user_id = ?
                                AND orders.date = ?
                                ORDER BY date DESC;""", (customer, date)).fetchall()

        elif customer != "" and date == "":
            orders=db.execute("""SELECT orders.user_id AS user_id, 
                                    orders.book_id AS book_id,   
                                    books.title AS title, 
                                    orders.quantity AS quantity, 
                                    orders.price AS price,
                                    orders.date AS date
                                FROM orders JOIN books
                                ON books.book_id = orders.book_id
                                WHERE orders.user_id = ?
                                ORDER BY date DESC;""", (customer,)).fetchall()

        elif customer == "" and date != "":
            orders=db.execute("""SELECT orders.user_id AS user_id, 
                                    orders.book_id AS book_id,   
                                    books.title AS title, 
                                    orders.quantity AS quantity, 
                                    orders.price AS price,
                                    orders.date AS date
                                FROM orders JOIN books
                                ON books.book_id = orders.book_id
                                WHERE date = ?
                                ORDER BY date DESC;""", (date,)).fetchall()

        elif customer == "" and date == "":
            orders=db.execute("""SELECT orders.user_id AS user_id, 
                                    orders.book_id AS book_id,   
                                    books.title AS title, 
                                    orders.quantity AS quantity, 
                                    orders.price AS price,
                                    orders.date AS date
                                FROM orders JOIN books
                                ON books.book_id = orders.book_id
                                ORDER BY date DESC;""").fetchall()
    total=0
    for row in orders:
        total+=row["price"]
    

    return render_template("orders.html", form=form, orders=orders, total=total )


#----------------------------CART AND CHECKOUT FUNCTIONS----------------------------#

#checks is previous cart exists
#used when the cart is first visited 
def check_previous_cart():
    db=get_db()
    #allow anyone to view cart, but only retain user carts
    if "obtained_previous_cart" not in session:
        session["obtained_previous_cart"]=False
    
    #if user is logged in, can retain previous cart
    #this should only occur ONCE per viewing of cart
    if "user_id" in session and session["obtained_previous_cart"]==False:
        session["obtained_previous_cart"]=True
        
        #if cart has previous order
        #fill cart with previous items
        previous_cart=db.execute("""SELECT *
                                    FROM cart
                                    WHERE user_id = ?;""",(g.user,)).fetchall()
        if previous_cart!=None:
            #user_id, book_id, quantity, price (of total products) in previous_cart
            #remember, SELECT statements held in dictionaries
            #for row in previous_cart makes each row a dictionary
            
            for row in previous_cart:
                
                book_id=row["book_id"]
                quantity=row["quantity"]
                #price starts as float
                price=row["price"]/quantity

                #if book_id in previous cart, compare to database
                book=db.execute("""SELECT books.price
                                    FROM books
                                    JOIN cart
                                    ON books.book_id = cart.book_id
                                    WHERE cart.book_id = ?;""",(book_id,)).fetchone()
                
                #don't update cart if no price found
                #if no price found, book_id doesn't exist
                #delete the item
                if book is None:
                    db.execute("""DELETE FROM cart
                                WHERE book_id = ?;""",(book_id,))
                    db.commit()

                else:
                    #update prices on cart with the db
                    if price != book["price"]:

                        total_price=book["price"]*quantity*discount()

                        price=book["price"]
                        db.execute("""UPDATE cart
                                    SET price = ?
                                    WHERE book_id = ?
                                    AND user_id = ?;""",(total_price, book_id, g.user))
                        db.commit()
                

                    #add items to cart but don't return back to cart as for loop needs to operate
                    add_to_cart(book_id, quantity, price, check_cart=True)

#gets titles and the total cost of books
def get_book_titles_totals():
    total=0
    titles={}
    db=get_db()
    #add book id to titles dict
    
    for book_id in session["cart"]:
        book = db.execute('''SELECT * FROM books
                        WHERE book_id = ?;''',(book_id,)).fetchone()
        
        #get total
        price=book["price"]
        quantity=session["cart"][book_id]["quantity"]

        #total represents total costs of products combined
        total+=round(price*quantity*discount(),2)

        #get titles
        title = book["title"]
        titles[book_id] = title
    return(titles, total)

#cart
@app.route("/cart", methods=["GET", "POST"])
def cart():
    #cart contains id of item and quantity
    #title will contain their names
    form=CartForm()
    if g.user is not None:
        check_previous_cart()
    titles_total=get_book_titles_totals()
    titles = titles_total[0]
    total = titles_total[1]
        
    if form.validate_on_submit():
        #redirect to checkout
        return redirect(url_for("checkout"))

    return render_template("cart.html", cart=session["cart"], total=("%.2f" % total), titles=titles, form=form, discount=discount())

#checkout for finalising purchase
#saves cart in database
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    given_discount=discount()
    form = CheckoutForm()
    db=get_db()
    check_previous_cart()
    titles_total=get_book_titles_totals()
    titles=titles_total[0]
    total=titles_total[1]

    #check if user has previous cart
    #if so, use old cart's order number

    user_cart = db.execute("""SELECT MAX(order_id) AS previous_order_id
                            FROM cart
                            WHERE user_id = ?""", (g.user,)).fetchone()

    latest_order = db.execute("""SELECT
                                MAX(order_id) AS latest_order_id
                                FROM
                                    (
                                    SELECT user_id, order_id
                                    FROM cart
                                    UNION
                                    SELECT user_id, order_id
                                    FROM orders
                                    );""").fetchone()
    #check if orders and cart are empty
    # if so, then the user will have first order                                       
    if latest_order["latest_order_id"] == None:
        order_number = 1
    #if there is no previous user cart
    #order number is now latest of all carts
    elif user_cart["previous_order_id"]==None:
        order_number = latest_order["latest_order_id"]+1
    else:
        #if user has old cart, no need to change order number
        order_number = user_cart["previous_order_id"]



    #overrite user cart entry
    db.execute("""DELETE FROM cart
                    WHERE user_id = ?;""",(g.user))
    db.commit()

    for book_id in session["cart"]:
        db.execute("""INSERT INTO cart (order_id, user_id, book_id, quantity, price)
                        VALUES (?,?,?,?,?);
                        """,
                        (order_number, g.user, book_id, session["cart"][book_id]["quantity"], session["cart"][book_id]["price"]))
        #add entry into cart table at db
        db.commit()

    #remember, form fields must be filled
    if form.validate_on_submit():
        #if true, then transaction confirmed
        for book_id in session["cart"]:

            #record cart items and order
            db.execute("""INSERT INTO orders (order_id, user_id, book_id, quantity, price, date)
                            VALUES (?,?,?,?,?,?);""",
                            (order_number, g.user, book_id, session["cart"][book_id]["quantity"], session["cart"][book_id]["price"], g.current_date,)) 
            db.commit()

        #remove cart items
        db.execute("""DELETE FROM cart
                    WHERE order_id = ?;""",(order_number,))
        db.commit()

        return redirect(url_for("payment_confirmed", order_number=order_number, total=total, given_discount=given_discount))

    return render_template("checkout.html", cart=session["cart"], total=("%.2f" % total), titles=titles, form=form)

@app.route("/payment_confirmed/<int:order_number>/<float:total>/<float:given_discount>", methods=["GET", "POST"])
def payment_confirmed(order_number, total, given_discount):
    filepath="receipts/receipt.order_%d.txt" % order_number
  
    directory = 'static/receipts'
    file_name = "receipt.order_%d.txt" % order_number
    completeName = os.path.join(directory, file_name)
    if session["cart"] != {}:
        titles=get_book_titles_totals()[0]
        file = open(completeName, "w")

        file.write("Customer: %s \nDate: %s \n\n" % (g.user,g.current_date) )
        for book_id in session["cart"]:
            file.write("\nBook: " + titles[book_id] )
            file.write("\nQuantity: " + str(session["cart"][book_id]["quantity"]))
            file.write("\nPrice: " + "%.2f" % (session["cart"][book_id]["price"]))

        file.write("\n\nTotal: " + "%.2f" % total)
        if given_discount<1:
                file.write("\n*Discount of " + "%.2f" % ((1-given_discount)*100) + "%" + " has been applied")

        file.close()
    #clear cart
    session["cart"]={}

    return render_template("payment_confirmed.html", filepath=filepath)



#create coupons/discounts
def discount():
    #user is logged in
    discount = 1
    if g.user is not None:
        db=get_db()
        order = db.execute("""SELECT COUNT(DISTINCT order_id) AS num_order
                                FROM orders
                                WHERE user_id = ?;""", (g.user,)).fetchone()
        if order !=None:
            num_order = order["num_order"]
            #if it's customer's second time ordering, give 10% discount on an item
            #calculated based on discount*total
            if (1+num_order) % 2 == 0:
                discount = 0.9
            #else, discount remains as 1
    return discount
    
#add item to cart
@app.route("/add_to_cart/<int:book_id>/<int(signed=True):quantity>/<float:price>", methods=["GET", "POST"])
@app.route("/add_to_cart/<int:book_id>/<int(signed=True):quantity>/<float:price>/<check_cart>", methods=["GET", "POST"])
def add_to_cart(book_id, quantity, price, check_cart=False):

    if book_id not in session["cart"]:
        session["cart"][book_id]={} #creates quantity/price/title 

        #price assigned to str later to allow 2 numbers after 2 decimal places
        session["cart"][book_id]["price"]=0
        session["cart"][book_id]["quantity"]=0
      
    #set quantity and limit
    session["cart"][book_id]["quantity"]+=quantity
    total_quantity=session["cart"][book_id]["quantity"]

    if total_quantity<=0:
        #remove cart item is quantity at or below 0
        session["cart"].pop(book_id)

    elif total_quantity>100:
        session["cart"][book_id]["quantity"]=100

    #obtain total price of good(s)
    #reason for if is so that it occurs if book_id isn't removed for negative quantity
    if book_id in session["cart"]:

        #record cost of product. account for their amounts
        session["cart"][book_id]["price"]=round(total_quantity*price*discount(), 2)
        
    #turns true when dealing with previous cart so nothing returned
    if check_cart==False:
        return redirect( url_for("cart", book_id=book_id))

