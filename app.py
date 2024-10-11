from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from models import db, Post, User
from forms import PostForm, RegistrationForm, LoginForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Inicializar o LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
# Redireciona para a página de login se o usuário não estiver autenticado
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required  # Certifica-se de que o usuário esteja logado
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data,
                    author=current_user)  # Associa o post ao usuário logado
        db.session.add(post)
        db.session.commit()
        flash('Sua publicação foi criada!', 'success')
        return redirect(url_for('home'))
    return render_template('post.html', title='New Post', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data,
                    email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Falha ao entrar. Usuário ou senha inválidos!', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('Autorização negada para editar essa publicação!', 'danger')
        return redirect(url_for('home'))

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Sua publicação foi atualizada!', 'success')
        return redirect(url_for('home', post_id=post.id))

    # Pre-fill the form with the current post data
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('edit_post.html', form=form, post=post)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('Autorização negada para excluir essa publicação!', 'danger')
        return redirect(url_for('home'))

    db.session.delete(post)
    db.session.commit()
    flash('Sua publicação foi excluida!', 'success')
    return redirect(url_for('home'))


@app.route('/post/<int:post_id>', methods=['GET'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('home.html', post=post)


if __name__ == "__main__":
    app.run(debug=True)
