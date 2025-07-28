from flask import Flask, render_template, request, redirect, session, send_file, abort, flash
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.utils import secure_filename    # No need to use it and uncomment it
import io
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = 'Your seceret key'
db = SQLAlchemy(app)


class Blog(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(2000), nullable=False)
    # image = db.Column(db.LargeBinary)

    def __repr__(self):
        return f"{self.title} - {self.content}"
        # return f"{self.title} - {self.content} - {self.image}"

class Register(db.Model):
    id = db.Column(db.Integer, primary_key = True )
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"{self.name} - {self.email} - {self.password}"

class Product(db.Model):
    product_id = db.Column(db.Integer(), primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_desc = db.Column(db.String(1000), nullable=False)
    product_price = db.Column(db.Integer(), nullable=False)

    def __reper__(self):
        return f"{self.product_name} - {self.product_desc} - {self.product_price}"

class Leads(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"{self.name} - {self.email} - {self.message}"

class Order(db.Model):
    order_id = db.Column(db.Integer(), primary_key=True)
    order_name = db.Column(db.String(100), nullable=False)
    order_product = db.Column(db.String(100), nullable=False)
    order_amount = db.Column(db.Integer(), nullable=False)
    order_mobile = db.Column(db.Integer(), nullable=False)
    order_address = db.Column(db.String(200), nullable=False)
    order_payment_mode = db.Column(db.String(100), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.order_name} - {self.order_product} - {self.order_amount} - {self.order_mobile} - {self.order_address}  - {self.order_payment_mode}"

@app.route('/')
def index():
    blog = Blog.query.all()
    return render_template('index.html', blog = blog)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        print("name: ",name)
        print("email: ",email)
        print("pass: ",password)

        regis = Register(name=name, email=email, password=password)
        db.session.add(regis)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']

        regis = Register.query.filter_by(email=email, password=password).first()
        if regis:
            session['user_id'] = regis.id

            return redirect('/admin')
        else:
            return render_template('login.html', error = "Invalid email or password!!!")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    user_id = session.get('user_id')        # Get ID from session
    if not user_id:
        return render_template('admin.html', regis=None)
    
    regis = Register.query.get(user_id)     # Fetch user details from DB

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        blog = Blog(title = title, content = content)
        db.session.add(blog)
        db.session.commit()
        return redirect('/admin')

    blog = Blog.query.all()
    
    return render_template('admin.html', blog = blog, regis=regis)

@app.route('/blog')
def blog():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/blog/<string:title>')
def show_full_blog(title):
    blogs = Blog.query.filter_by(title=title).first_or_404()
    return render_template('fullblog.html', blogs = blogs)

@app.route('/delete/<string:title>')
def delete_blog(title):
    blog = Blog.query.filter_by(title=title).first_or_404()
    db.session.delete(blog)
    db.session.commit()
    return redirect('/admin')

@app.route('/edit/<string:title>', methods=['GET', 'POST'])
def edit(title):
    user_id = session.get('user_id')        # Get ID from session
    if not user_id:
        return render_template('admin.html', regis=None)
    
    regis = Register.query.get(user_id)     # Fetch user details from DB
    blog = Blog.query.filter_by(title=title).first_or_404()

    if request.method == 'POST':        
        blog.title =  request.form['title']
        blog.content = request.form['content']
        db.session.commit()
        return redirect('/admin') 
    
    return render_template('edit.html', blog=blog, regis=regis)

@app.route('/shop')
def shop():
    products = Product.query.all()
    return render_template('shop.html', products=products)

@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method=='POST':
        lead = Leads(name=request.form['name'], email=request.form['email'], message=request.form['message'])
        db.session.add(lead)
        db.session.commit()
        flash("Your message has been sent successfully!", "success")
        return redirect('/contact')
    return render_template('contact.html')

@app.route('/admin/products', methods=['GET', 'POST'])
def add_product():
    user_id = session.get('user_id')            # Get Id from session
    if not user_id:
        return render_template('admin.html')
    
    if request.method == 'POST':
        product = Product(product_name=request.form['product-name'], product_desc=request.form['product-desc'], product_price=request.form['product-price'])
        db.session.add(product)
        db.session.commit()
    products = Product.query.all()
    regis = Register.query.get(user_id)         # Fetch user details from DB
    return render_template('add_products.html', regis=regis, products=products)

@app.route('/admin/products/delete/<int:id>')
def product_delete(id):
    product = Product.query.filter_by(product_id=id).first()
    db.session.delete(product)
    db.session.commit()
    return redirect('/admin/products')

@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
def product_edit(id):
    user_id = session.get('user_id')    # Check if user is logged in
    if not user_id:
        return render_template('admin.html', regis=None)
   
    regis = Register.query.get(user_id)
    product = Product.query.filter_by(product_id=id).first_or_404()
   
    if request.method == 'POST':
        product.product_price = request.form['product-price']
        product.product_name = request.form['product-name']
        product.product_desc = request.form['product-desc']
        db.session.commit()
        return redirect('/admin/products')
   
    return render_template('edit_product.html', regis=regis, product=product)

@app.route('/shop/<string:pname>/<int:pid>')
def product_detail(pname, pid):
    product = Product.query.filter_by(product_id=pid).first_or_404()
    return render_template('Product-detail.html', product=product)    

@app.route('/buy/<string:pname>', methods=['GET', 'POST'])
def buy_product(pname):
    product = Product.query.filter_by(product_name=pname).first_or_404()
    if request.method=='POST':
        order = Order(order_name = request.form['name'], order_product = request.form['product'], order_amount = request.form['amount'], order_mobile = request.form['mobile'], order_address = request.form['address'], order_payment_mode = request.form['payment-mode'])
        db.session.add(order)
        db.session.commit()
        return redirect(f'/purchase-success/{order.order_id}')
    return render_template('buy.html', product=product)

@app.route('/purchase-success/<int:id>')
def purchase_sucess(id):
    order = Order.query.filter_by(order_id=id).first_or_404()
    return render_template('purchase-success.html', order=order)

@app.route('/my-order')
def my_order():
    order = Order.query.all()
    return render_template('my-order.html', order=order)

@app.route('/order/delete/<int:id>')
def delete_order(id):
    delete_order = Order.query.filter_by(order_id=id).first_or_404()
    db.session.delete(delete_order)
    db.session.commit()
    return redirect('/my-order')

# @app.route('/contact')
# def contact():
    

with app.app_context():
    db.create_all()
    # This Command we can use if we want to delete any particular table from database
    # tableName.__table__.drop(db.engine)

if __name__ == '__main__':
    
    app.run(debug=True)
