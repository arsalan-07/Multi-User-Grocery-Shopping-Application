from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3

user_bp = Blueprint('user', __name__, template_folder='templates')

# SQLite Database Setup
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              first_name TEXT,
              last_name TEXT,
              email TEXT,
              password TEXT)''')

# Create the orders table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS orders
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              product_id INTEGER,
              product_name TEXT,
              price REAL,
              quantity INTEGER,
              FOREIGN KEY (product_id) REFERENCES products(id))''')

conn.commit()
conn.close()


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user exists in the database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['first_name'] = user[1]
            return render_template('user_dashboard.html', template='base.html', email=email)
        else:
            return "No such user exists."

    return render_template('user_login.html')


@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        # Store user details in SQLite database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                  (first_name, last_name, email, password))
        conn.commit()
        conn.close()

        return redirect('/user/login')

    return render_template('user_signup.html')

@user_bp.route('/sections')
def section_list():
    # Retrieve the list of sections from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sections")
    sections = c.fetchall()
    conn.close()

    return render_template('section_list_user.html', sections=sections)


@user_bp.route('/product_list')
def user_product_list():
    # Retrieve the product list from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return render_template('product_list_user.html', products=products)


@user_bp.route('/products_by_section/<int:section_id>')
def products_by_section(section_id):
    # Retrieve the section name from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT section_name FROM sections WHERE id = ?", (section_id,))
    section_name = c.fetchone()[0]
    
    # Retrieve the products for the specified section ID from the database
    c.execute("SELECT * FROM products WHERE section_id = ?", (section_id,))
    products = c.fetchall()
    conn.close()

    return render_template('products_by_section_user.html', products=products, section_name=section_name,section_id=section_id)



@user_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Retrieve the product details from the database based on the product ID
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()

    if product is not None and product[6] is not None and product[6] > 0:  # Assuming the quantity column is at index 7
        # Check if the product is already in the user's orders
        c.execute("SELECT * FROM orders WHERE product_id = ?", (product_id,))
        existing_order = c.fetchone()

        if existing_order is not None:
            # If the product is already in the user's orders, increment the quantity
            new_quantity = existing_order[4] + 1  # Assuming the quantity column is at index 4
            c.execute("UPDATE orders SET quantity = ? WHERE product_id = ?", (new_quantity, product_id))
            conn.commit()
        else:
            # Insert the purchased product details into the "orders" table
            c.execute("INSERT INTO orders (product_id, product_name, price, quantity) VALUES (?, ?, ?, ?)",
                      (product[0], product[1], product[4], 1))  # Assuming the respective columns for product_id, product_name, price, and quantity
            conn.commit()

        # Calculate the new quantity after adding to cart
        new_quantity = product[6] - 1  # Subtracting 1 from the current quantity
        print(new_quantity)
        if new_quantity >= 0:
            # Update the product quantity in the database
            c.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
            conn.commit()

            conn.close()

            # Perform any other necessary actions related to adding to cart, such as updating the product status

            # Redirect the user to a success message or relevant route
            return "Product added to cart successfully"
        else:
            # If the product quantity is insufficient, return an error message
            conn.close()
            return "Insufficient quantity. Product cannot be added to cart."
    else:
        # If the product is not found or the quantity is zero or None, return an error message
        conn.close()
        return "Error: Product not available."



@user_bp.route('/product_list', methods=['GET', 'POST'])
def search_product_list():
    if request.method == 'POST':
        # Retrieve the search query from the form
        search_query = request.form.get('search_query')

        # Retrieve the filtered product list from the database based on the search query
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE productname LIKE ? OR rate LIKE ? OR manufacture_date LIKE ? OR fexpiry_date LIKE ? OR id LIKE ?", ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
        products = c.fetchall()
        conn.close()
        print("search")
        print(products)
        if products == []:
            return redirect('/user/product_list')
        return render_template('product_list_user.html', products=products)


@user_bp.route('/products_by_section/<int:section_id>', methods=['GET', 'POST'])
def search_product_list_by_section(section_id):
    if request.method == 'POST':
        # Retrieve the search query from the form
        search_query = request.form.get('search_query')
        # Retrieve the filtered product list from the database based on the search query
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE (productname LIKE ? OR rate LIKE ? OR manufacture_date LIKE ? OR fexpiry_date LIKE ? OR id LIKE ?) AND section_id = ?", ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', section_id))
        products = c.fetchall()
        conn.close()
        print("user search")
        print(section_id)
        print(products)
        if not products:  # Check if products list is empty
            # Redirect to the products_by_section URL
            print("Enter")
            return redirect(url_for('user.products_by_section', section_id=section_id))
        return render_template('product_list_user_section.html', products=products)
    return render_template('product_list_user_section.html', products=[])  # Empty list for initial rendering



@user_bp.route('/orders')
def user_orders():
    # Retrieve the purchased products from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    orders = c.fetchall()
    conn.close()
    
    # It will show the total amount of money which need to pay to the user
    total_amount = 0  # Variable to store the total amount

    # Calculate the total amount
    for order in orders:
        price = order[3]  # Assuming the price column is at index 3
        quantity = order[4]  # Assuming the quantity column is at index 4
        total_amount += price * quantity
        
    return render_template('user_orders.html',  orders=orders, total_amount=total_amount)


@user_bp.route('/logout')
def logout():
    # Log out the user
    session.pop('first_name', None)
    # Redirect the user to the login page or any other page
    return redirect('/user/login')

@user_bp.route('/user_dashboard')
def user_dashboard():
    return render_template('user_dashboard.html', template='base.html')




