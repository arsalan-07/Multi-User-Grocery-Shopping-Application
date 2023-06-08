from flask import Blueprint, render_template, request, redirect, session, url_for
import sqlite3

admin_bp = Blueprint('admin', __name__, template_folder='templates')

# SQLite Database Setup
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS admins
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              first_name TEXT,
              last_name TEXT,
              email TEXT,
              phone_number TEXT,
              password TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS products
             (id INTEGER,
              productname TEXT,
              manufacture_date TEXT,
              fexpiry_date TEXT,
              rate REAL,
              unit TEXT,
              quantity INTEGER,
              section_id INTEGER,
              FOREIGN KEY (section_id) REFERENCES sections(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS sections
             (id INTEGER PRIMARY KEY,
              section_name TEXT)''')

conn.commit()
conn.close()

# @admin_bp.route('/')
# def home():
#     return render_template('home.html')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['phone_number']

        # Check if admin exists in the database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admins WHERE email = ? AND password = ? AND phone_number = ?", (email, password, phone_number))
        admin = c.fetchone()
        conn.close()

        if admin:
            session['first_name'] = admin[1]
            return render_template('admin_dashboard.html', template='base_admin.html', email=email)
        else:
            return "No such user exists."

    return render_template('admin_login.html')


@admin_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']

        # Store admin details in SQLite database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO admins (first_name, last_name, email, phone_number, password) VALUES (?, ?, ?, ?, ?)",
                  (first_name, last_name, email, phone_number, password))
        conn.commit()
        conn.close()

        return redirect('/admin/login')

    return render_template('admin_signup.html')


@admin_bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        id = request.form['id']
        productname = request.form['productname']
        manufacture_date = request.form['manufacture_date']
        fexpiry_date = request.form['fexpiry_date']
        rate = request.form['rate']
        unit = request.form['unit']
        section = request.form['section_id']
        quantity = request.form['quantity']
        # Store product details in SQLite database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO products (id, productname, manufacture_date, fexpiry_date, rate, unit, quantity, section_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (id, productname, manufacture_date, fexpiry_date, rate, unit, quantity, section))

        conn.commit()
        conn.close()
        print("Product added succesfully")
        return redirect('/admin/product_list')

    return render_template('add_products.html')



@admin_bp.route('/product_list', methods=['GET', 'POST'])
def product_list():
    if request.method == 'POST':
        # Check the action requested by the admin
        action = request.form.get('action')
        if action == 'delete_product':
            # Retrieve the product ID to be deleted
            id = request.form.get('id')

            # Perform the necessary actions to delete the product from the database
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("DELETE FROM products WHERE id = ?", (id,))
            conn.commit()
            conn.close()

    # Retrieve the updated product list from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()

    return render_template('product_list_admin.html', products=products)

@admin_bp.route('/create_section', methods=['GET', 'POST'])
def create_section():
    if request.method == 'POST':
        section_id = request.form['id']
        section_name = request.form['section_name']
        # Store section in SQLite database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO sections (section_name,id) VALUES (?, ?)", (section_name,section_id))
        conn.commit()
        conn.close()

        return redirect('/admin/sections')

    return render_template('create_section.html')


@admin_bp.route('/sections')
def section_list():
    # Retrieve the list of sections from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sections")
    sections = c.fetchall()
    conn.close()

    return render_template('section_list_admin.html', sections=sections)



@admin_bp.route('/products_by_section/<int:section_id>')
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

    return render_template('products_by_section_admin.html', products=products, section_name=section_name,section_id=section_id)



@admin_bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        # Retrieve the updated product details from the form
        productname = request.form.get('productname')
        manufacture_date = request.form.get('manufacture_date')
        fexpiry_date = request.form.get('fexpiry_date')
        rate_per_unit = request.form.get('rate_per_unit')
        unit = request.form.get('unit')
        quantity = request.form.get('quantity')
        section_id = request.form.get('section_id')

        # Perform the necessary actions to update the product in the database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE products SET productname = ?, manufacture_date = ?, fexpiry_date = ?, rate = ?, unit = ?, section_id = ?, quantity = ? WHERE id = ?",
                  (productname, manufacture_date, fexpiry_date, rate_per_unit, unit, section_id, quantity, product_id))
        conn.commit()
        conn.close()
        print("Product edited successfully")

        # Redirect back to the product list page
        return redirect('/admin/product_list')

    # Retrieve the product details from the database based on the product ID
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()

    if product:
        return render_template('edit_product.html', product=product)
    else:
        return "Product not found"
    
    
    
@admin_bp.route('/edit_section/<int:section_id>', methods=['GET', 'POST'])
def edit_section(section_id):
    if request.method == 'POST':
        # Retrieve the updated section details from the form
        section_name = request.form.get('section_name')

        # Perform the necessary actions to update the section in the database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE sections SET section_name = ? WHERE id = ?", (section_name, section_id))
        conn.commit()
        conn.close()
        print("Section edited successfully")
        return redirect('/admin/sections')

    # Retrieve the section details from the database based on the section ID
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
    section = c.fetchone()
    conn.close()

    return render_template('edit_section.html', section=section)




@admin_bp.route('/admin/delete_section/<int:section_id>', methods=['GET', 'POST'])
def delete_section(section_id):
    # Connect to the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Check if the section exists in the database
    c.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
    section = c.fetchone()

    if section:
        # Delete the section from the database
        c.execute("DELETE FROM sections WHERE id = ?", (section_id,))
        conn.commit()
        conn.close()

        # Redirect the user to the admin section list page
        return redirect('/admin/sections')
    
    
@admin_bp.route('/admin/product_list', methods=['GET', 'POST'])
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
        if products == []:
            return redirect('/admin/product_list')
    return render_template('product_list_admin.html', products=products)



@admin_bp.route('/products_by_section/<int:section_id>', methods=['GET', 'POST'])
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
        print("admin search")
        print(section_id)
        print(products)
        if products == []:
            # return "Enter name to search"
            return redirect(url_for('admin.products_by_section', section_id=section_id))
        return render_template('product_list_admin_section.html', products=products)
    return render_template('product_list_admin_section.html', products=[])  # Empty list for initial rendering


@admin_bp.route('/logout')
def logout():
    # Log out the user
    session.pop('first_name', None)
    # Redirect the user to the login page or any other page
    return redirect('/admin/login')

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html', template='base_admin.html')
