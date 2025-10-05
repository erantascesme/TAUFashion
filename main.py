# flask imports:
import mysql.connector
from flask import Flask, request, redirect, render_template, session
from flask_session import Session
from classes import *
import datetime
import math

app = Flask(__name__)  # initialize flask app

# ---------- config sessions in app ---------
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# ---------- config MySQL connection in app ---------
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="TAUFashion"
)

# Handle 404 Not Found
@app.errorhandler(404)
def page_not_found(e):
    return redirect("/")

# Handle 500 Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return redirect("/")

# Handle any other exception
@app.errorhandler(Exception)
def handle_exception(e):
    return redirect("/")

@app.route('/', methods=["POST", "GET"])  # home page
def login():
    if session.get("user"):
        return redirect('/store')
    session_message = session.get('message')
    session["message"] = None
    cursor = mydb.cursor()
    if request.method == "POST":  # when Login is pressed
        # retrieve data from form:
        password = request.form["password"]
        email = request.form["email"]
        cursor.execute('SELECT email, username, is_admin FROM users WHERE email = %s AND password = %s',
                       (email, password))
        cur_user = cursor.fetchone()
        cursor.close()
        if cur_user:
            user = User(email=cur_user[0], username=cur_user[1], is_admin=cur_user[2])
            session["user"] = user
            return redirect("/store")
        else:
            cursor.close()
            return render_template("login.html",
                                   message="The details you have entered are not valid. \
                                            If you don't have an account, please Sign Up.")

    else:
        return render_template("login.html", message=session_message)


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":  # when Login is pressed
        password = request.form["password"]
        email = request.form["email"]
        username = request.form["username"]
        gender = request.form["gender"]
        faculty = request.form["faculty"]
        date_of_birth = request.form["dob"]
        cursor = mydb.cursor()
        # check whether email exists already:
        cursor.execute('''SELECT email FROM users''')
        emails_known = cursor.fetchall()
        if (email) in emails_known:
            return render_template('/signup', message="An account with that email already exists. /"
                                                      "Please login or sign up with a different email.")
        else:
            # if User is new - create an instance of User class, and update users list and users_tokens dict
            cursor.execute(
                f'''insert into users (email, username, password, is_admin, gender, faculty, date_of_birth) values (%s, %s, %s, %s, %s, %s, %s);''',
                (email, username, password, 0, gender, faculty, date_of_birth))
            mydb.commit()
            user = User(email, username, 0)
            session["user"] = user  # start a session of the user
            cursor.close()
            return redirect("/store")

    else:
        return render_template("signup.html")


@app.route('/store', methods=["POST", "GET"])
def store():
    if not session.get("user"):
        session['message'] = 'You must Login first.'
        return redirect("/")
    session_message_success = session.get('message_success')
    session_message_error = session.get('message_error')
    session["message_success"] = None
    session["message_error"] = None

    cursor = mydb.cursor()
    products = get_all_products(cursor, in_stock=True)

    if request.method == "POST":  # when submit is pressed
        products_bought = {}
        bought_something = False
        for product in products:
            quantity = request.form.get('order_' + str(product.id))
            if int(quantity) > 0:
                bought_something = True
                update_stock_amount(cursor, mydb, product.id, product.amount-int(quantity))
                products_bought[product.id] = quantity

        if bought_something:
            cursor.execute('''SELECT max(order_id) FROM transactions''')
            fetch = cursor.fetchone()
            new_order_id = fetch[0] + 1 if fetch[0] is not None else 1
            new_transaction = Transaction(new_order_id, session.get("user").email, datetime.datetime.now())
            new_transaction.insert_to_db(cursor, mydb)
            print(products_bought)
            new_transaction.insert_products_to_db(cursor, mydb, products_bought)
            cursor.close()
            session["message_success"] = ("Your purchase has been made successfully!")
            return redirect('/store')
        else:
            cursor.close()
            session["message_error"] = ("It seems that you tried to make an order with no items. Please choose wanted "
                                  "quantity for the items you desire.")
            return redirect('/store')

    else:
        cursor.close()
        return render_template("store_homepage.html", message_success=session_message_success,
                               message_error=session_message_error,
                               products=products, num_products=len(products), num_rows=math.ceil(len(products)))


@app.route('/my_account')
def my_account():
    if not session.get("user"):
        session['message'] = 'You must Login first.'
        return redirect("/")
    cursor = mydb.cursor()
    user = session.get("user")
    cursor.execute('select * from transactions where user_email = %s order by order_datetime desc', (user.email,))
    fetch_transactions = cursor.fetchall()
    transactions = []
    for tr in fetch_transactions:
        print(tr, tr[0], tr[1], tr[2])
        transaction = Transaction(tr[0], tr[1], tr[2])
        print(transaction)
        transaction.calc_total_cost(cursor)
        transactions.append(transaction)
    cursor.close()
    return render_template("my_account.html", transactions=transactions)

@app.route('/stock_management', methods=['POST','GET'])
def stock_management():
    if not session.get("user"):
        session['message'] = 'You must Login first.'
        return redirect("/")
    message = session.get('message')
    session["message"] = None
    cursor = mydb.cursor()
    products = get_all_products(cursor)

    if request.method == "POST":  # add a new product post request
        new_product = Product(0,
                              request.form['product_name'],
                              int(request.form['amount_in_stock']),
                              float(request.form['cost']),
                              request.form['img_url'],
                              bool(request.form['is_campaigned']))
        print(request.form['product_name'],
                              int(request.form['amount_in_stock']),
                              float(request.form['cost']),
                              request.form['img_url'],
                              bool(request.form['is_campaigned']))
        new_product.insert_to_db(cursor, mydb)
        cursor.close()
        session['message'] = "New product has been added successfully!"
        return redirect("/stock_management")
    else:
        cursor.close()
        return render_template("stock_management.html", products=products, message=message)


@app.route('/update_stock', methods=["POST"])
def update_stock():
    if not session.get("user"):
        session['message'] = 'You must Login first.'
        return redirect("/")
    cursor = mydb.cursor()
    print('reached')
    update_stock_amount(cursor,mydb, request.form['product_to_update'], request.form['amount'])
    cursor.close()
    session['message'] = "Item amount was updated successfully!"
    return redirect('/stock_management')


@app.route('/logout')
def logout():
    session["user"] = None
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)

mydb.close()
