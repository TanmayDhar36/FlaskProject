from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize app
app = Flask(__name__)
app.secret_key = 'Tanmay@98'  # 🔐 Replace with a strong key in production

# Setup PostgreSQL database (Render or local fallback)
db_uri = os.environ.get(
    'DATABASE_URL', 
    'postgresql://postgres:Tanmay%4098@localhost:5432/flask_blog'
)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ Models ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    blogs = db.relationship('Blog', backref='author', lazy=True)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ------------------ Routes ------------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return "User already exists!"

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials!"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/submit_blog', methods=['GET', 'POST'])
def submit_blog():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        blog = Blog(title=title, content=content, user_id=session['user_id'])
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('technical_blogs'))

    return render_template('submit_blog.html')

@app.route('/technical_blogs')
def technical_blogs():
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('technical_blogs.html', blogs=blogs)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_blogs = Blog.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', blogs=user_blogs)

# ------------------ Start App ------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Only runs if DB tables don't exist
    app.run(debug=True)
