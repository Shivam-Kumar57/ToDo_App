from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Todo
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.secret_key = 'MY_key'


db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            form.email.errors.append("Invalid email")
        elif not check_password_hash(user.password, form.password.data):
            form.password.errors.append("Incorrect password")
        else:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route("/index", methods=["GET", "POST"])
@app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
def index(todo_id=None):
    todo = None

    if todo_id is not None:
        todo = Todo.query.get(todo_id)

    if request.method == "POST":
        title = request.form.get("title", "")
        if todo:  # Update
            todo.title = title
            db.session.commit()
            flash("Todo item updated successfully")
        else:     # New task
            todo = Todo(title=title)
            db.session.add(todo)
            db.session.commit()
            flash("Todo item added successfully")

        return redirect(url_for("index"))

    todos = Todo.query.order_by(Todo.id.desc()).all()
    return render_template("index.html", todos=todos, todo=todo)

@app.route('/todo-delete/<int:todo_id>', methods=["POST"])
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash("🗑️ Todo item deleted successfully", "success")
    else:
        flash("❌ Todo item not found", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
