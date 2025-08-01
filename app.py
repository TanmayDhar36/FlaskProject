from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_blog_uwis_user:oAwIDzz0rh9lRpauWxu36kUuPJ1taabF@dpg-d26adfili9vc73d2hjl0-a.oregon-postgres.render.com/flask_blog_uwis'
#postgresql://flask_blog_uwis_user:oAwIDzz0rh9lRpauWxu36kUuPJ1taabF@dpg-d26adfili9vc73d2hjl0-a.oregon-postgres.render.com/flask_blog_uwis
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='blogs')

# Routes
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or Email already exists.", "danger")
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully!", "success")
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        password = request.form['password']
        user = User.query.filter((User.username == uname) | (User.email == uname)).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Logged in!", "success")
            return redirect(url_for('home'))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('login'))

@app.route('/technical_blogs')
def technical_blogs():
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('technical_blogs.html', blogs=blogs)

@app.route('/submit_blog', methods=['GET', 'POST'])
def submit_blog():
    if 'user_id' not in session:
        flash("Login required", "warning")
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        blog = Blog(title=title, content=content, author_id=session['user_id'])
        db.session.add(blog)
        db.session.commit()
        flash("Blog submitted!", "success")
        return redirect(url_for('technical_blogs'))
    return render_template('submit_blog.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Login required", "warning")
        return redirect(url_for('login'))
    blogs = Blog.query.filter_by(author_id=session['user_id']).order_by(Blog.id.desc()).all()
    return render_template('dashboard.html', blogs=blogs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
