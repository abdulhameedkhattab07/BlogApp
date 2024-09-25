import os
import uuid
from flask import session, request, Flask, flash, redirect, url_for, session, logging, render_template, send_from_directory
from cs50 import SQL
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from data import RegisterForm, ArticleForm, EditForm, extract_usernames, get_news

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower in app.config['ALLOWED_EXTENSIONS']

#confiq  Database
db = SQL("sqlite:///flaskapp.db")

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        elif 'admin' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Only For Admin', 'danger')
            return redirect(url_for('login'))
    return wrap

#static file path
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

#home
@app.route("/")
def home():
    articles = db.execute("SELECT * FROM articles WHERE likes >= 8 LIMIT 10")
    return render_template("home.html", type=type, articles=articles)


#articles
@app.route("/articles", methods=['GET', 'POST'])
def articles():

    if request.method == 'POST':
        articletype = request.form.get('article-type')

        if articletype:
            articles = db.execute('SELECT * FROM articles WHERE type = ? ORDER BY create_date DESC', articletype)
        else:
            articles = db.execute('SELECT * FROM articles ORDER BY create_date DESC')

        return render_template('articles.html', articles=articles)
    
    articles = db.execute('SELECT * FROM articles ORDER BY create_date DESC')
    return render_template('articles.html', articles=articles)
    

    

#single article
@app.route("/article/<string:id>")
def article(id):
    article = db.execute('SELECT * FROM articles WHERE id = ?', id)[0]
    author = article['author']
    comments = db.execute('SELECT * FROM comments WHERE article_id = ?', id)

    return render_template('article.html', article=article, comments=comments)
    
#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        type = form.type.data
        password = generate_password_hash(str(form.password.data), method='pbkdf2', salt_length=16)
        db_username_check = db.execute("SELECT * FROM users WHERE username = ?", username)
        db_email_check = db.execute("SELECT * FROM users WHERE email = ?", email)

        if len(db_username_check) == 1:
            flash('Username Already Taken', 'danger')
            return redirect(url_for('register'))
        elif db_email_check:
            flash('Email Already Taken', 'danger')
            return redirect(url_for('register'))
        elif not type:
            flash('Must Select an account type', 'danger')
            return redirect(url_for('register'))
        
        # Set db
        db.execute("INSERT INTO users (name, email, username, password, type) VALUES(?, ?, ?, ?, ?)", name, email, username, password, type)

        #flash
        flash('You are Now Registered and can log in', 'success')

        #redirect to home
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form fields
        username = request.form.get('username')
        password_candidate = request.form.get('password')

        result = db.execute("SELECT * FROM users WHERE username = ?", username) 
        if username == 'ADMIN' and password_candidate == 'admin':
            session['admin'] = username
            flash('Logged in as Admin', 'success')
            return redirect(url_for('admindashboard'))
        
        if len(result) != 1:
            # ensure username exist
            error = 'Username Does Not Exist'
            return render_template('login.html', error=error)
        #compare passwords
        if not check_password_hash(result[0]['password'], password_candidate): 
            error = 'Invalid login'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            session['username'] = username
            session['id'] = result[0]['id']
            session['email'] = result[0]['email']

            flash('You are now logged in', 'success')
            return redirect(url_for('dashboard'))
    return render_template('login.html')


# #admin
@app.route('/admindashboard')
@is_admin
def admindashboard():
    users = db.execute('SELECT * FROM users ORDER BY register_date DESC')
    articles = db.execute('SELECT * FROM articles ORDER BY create_date DESC')
    return render_template('admin.html', users=users, articles=articles)

# admin add new user
@app.route('/admindashboard/add_user', methods=['GET', 'POST'])
@is_admin
def add_user():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        type = form.type.data
        password = generate_password_hash(str(form.password.data), method='pbkdf2', salt_length=16)
        db_username_check = db.execute("SELECT * FROM users WHERE username = ?", username)
        db_email_check = db.execute("SELECT * FROM users WHERE email = ?", email)

        if len(db_username_check) == 1:
            flash('Username Already Taken', 'danger')
            return redirect(url_for('register'))
        elif db_email_check:
            flash('Email Already Taken', 'danger')
            return redirect(url_for('register'))
        elif not type:
            flash('Must Select an account type', 'danger')
            return redirect(url_for('register'))
        
        # Set db
        db.execute("INSERT INTO users (name, email, username, password, type) VALUES(?, ?, ?, ?, ?)", name, email, username, password, type)

        #flash
        flash('User Registered Successfully', 'success')

        #redirect to home
        return redirect(url_for('admindashboard'))
    return render_template('add_user.html', form=form)

    

#delete user as admin
@app.route('/admindashboard/del_user/<string:id>', methods=['POST'])
@is_admin
def del_user(id):
    try:
        db.execute('DELETE FROM users WHERE id = ?', id)
        flash('User Deleted Successfully', 'success')
    except Exception as e:
        flash('An Error Occured', 'danger')
    return redirect(url_for('admindashboard'))


#logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

#dasboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    articles = db.execute('SELECT * FROM articles WHERE author = ?', session['username'])
    no_of_articles = len(articles)
    user = db.execute('SELECT * FROM users WHERE username = ?', session['username'])[0]
    type = user['type']
    subscription = db.execute('SELECT COUNT(*) as count FROM subscriptions WHERE blogger_id = ?', session['id'])[0]['count']
    if len(articles) > 0:
        return render_template('dashboard.html', no_of_articles=no_of_articles, articles=articles, user=user, type=type, subscription=subscription)
    else:
        return render_template('dashboard.html', type=type, user=user)
    
# profile page
@app.route('/dashboard/profile', methods=['GET', 'POST'])
@is_logged_in
def profile():
    form = EditForm(request.form)
    user = db.execute('SELECT * FROM users WHERE id = ?', session['id'])[0]

    #populate register form fields
    form.name.data = user['name']
    form.username.data = user['username']
    form.email.data = user['email']
    form.bio.data = user['bio']
    form.type.data = user['type']
    form.blog.data = user['blogname']

    if request.method == 'POST':
        if user['type'] == 'Blogger':
            blogname = request.form['blog']
        else:
            blogname = 'User...'
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        bio = request.form['bio']
        # image = request.files['image']
        # filename = str(uuid.uuid1())+os.path.splitext(image.filename)[1]
        # image.save(os.path.join("static/uploads", filename))
        
        if username == session['username']:
            msg1 = 'Seems You didnt change your username'
        elif email == session['email']:
            msg2 = 'Seems You didnt change your email'
        elif blogname == user.blogname:
            msg3 = 'Seems You didnt change your email'
        else:
            db_username_check = db.execute("SELECT * FROM users WHERE username = ?", username)
            db_email_check = db.execute("SELECT * FROM users WHERE email = ?", email)
            db_blogname_check = db.execute("SELECT * FROM users WHERE blogname = ?", blogname)
            if db_username_check:
                flash('Username Already Taken!', 'danger')
                return redirect(url_for('profile'))
            elif db_email_check:
                flash('Email Already Exists', 'danger')
                return redirect(url_for('profile'))
            if db_blogname_check:
                flash('Blog Name Already Exist', 'danger')
                return redirect(url_for('profile'))
        
        db.execute('UPDATE users SET name = ?, username = ?, email = ?, bio = ?, blogname = ? WHERE id = ?', name, username, email, bio, blogname, session['id'])
        flash('Infos Updated Successfully', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user, form=form)


#subscribe to a blog
@app.route('/dashboard/subscribe/<string:blogger_id>', methods=['POST'])
@is_logged_in
def subscribe(blogger_id):
    user_id = session['id']
    #check if already subscibed
    if session['id'] == blogger_id:
        flash("You cant subscribe to yourself!")
        return redirect(url_for('dashboard'))
    subscription = db.execute('SELECT * FROM subscriptions WHERE user_id = ? AND blogger_id = ?', user_id, blogger_id)
    if subscription:
        flash('You are Already Subscribed to this blogger', 'success')
        return redirect(url_for('my_subscriptions', blogger_id=blogger_id))
    else:
        db.execute('INSERT INTO subscriptions (user_id, blogger_id) VALUES(?, ?)', user_id, blogger_id)
        flash('Subscribed Successfully', 'success')
        return redirect(url_for('my_subscriptions', blogger_id=blogger_id))

# all blogs
@app.route('/dashoard/bloggers')
def bloggers():
    bloggers = db.execute("SELECT * FROM users WHERE type = ? ORDER BY name ASC", 'Blogger')
    return render_template('bloggers.html', bloggers=bloggers)

#each blog
@app.route('/dashboard/bloggers/blogger/<string:id>')
@is_logged_in
def blogger(id):
    blogger = db.execute('SELECT * FROM users WHERE id = ?', id)[0]
    articles = db.execute('SELECT * FROM articles WHERE author = ? ORDER BY create_date DESC', blogger['username'])
    subscription = db.execute('SELECT COUNT(*) as count FROM subscriptions WHERE blogger_id = ?', session['id'])[0]['count']
    return render_template('blogger.html', blogger=blogger, articles=articles, subscription=subscription)
    

#subscription
@app.route('/dashboard/my_subscriptions')
@is_logged_in
def my_subscriptions():
    user_id = session['id']

    subscriptions = db.execute('SELECT users.blogname, subscriptions.blogger_id FROM subscriptions JOIN users ON subscriptions.blogger_id = users.id WHERE subscriptions.user_id = ? ORDER BY created_at DESC', user_id)
    return render_template('subscriptions.html', subscriptions=subscriptions)

def send_notifications(id, title):
    subscribers = db.execute('SELECT user_id FROM subscriptions WHERE blogger_id = ?', id)

    for subscriber in subscribers:
        message = f"New Article Published: {title}"
        db.execute('INSERT INTO notifications (user_id, message) VALUES(?, ?)', subscriber['user_id'], message)


#add article
@app.route('/dashboard/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db.execute('SELECT * FROM users WHERE username = ? ', session['username'])[0]
        if user['type'] == 'Blogger':

            title = form.title.data
            body = form.body.data
            alias = form.alias.data
            type = form.type.data
            image = request.files['image']
            if image:
                filename = str(uuid.uuid1())+os.path.splitext(image.filename)[1]
                image.save(os.path.join("static/uploads", filename))
            else:
                filename = None

            db.execute("INSERT INTO articles (title, body, filename, alias, author, type) VALUES(?, ?, ?, ?, ?, ?)", title, body, filename, alias, session['username'], type)
            send_notifications(session['id'], title)
            flash('Article Created and Notifications Sent', 'success')

            return redirect(url_for('dashboard'))
        else:
            flash('Unauthorized!', 'danger')
            return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)

#edit article
@app.route('/dashboard/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    #get article by id
    article = db.execute('SELECT * FROM articles WHERE id = ?', id)[0]

    form = ArticleForm(request.form)

    #populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']
    form.alias.data = article['alias']
    form.type.data = article['type']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        alias = request.form['alias']
        if title == article['title']:
            pass
        elif body == article['body']:
            pass
        db.execute('UPDATE articles SET title = ?, alias = ?, body = ? WHERE id = ?', title, alias, body, id)
        
        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)

#delete Article
@app.route('/dashboard/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):

    if session['username']:
        db.execute('DELETE FROM articles WHERE id = ?', id)
        flash('Article Deleted', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Not Authorized!', 'danger')
        return redirect(url_for('dashboard'))
    
#delete Article
@app.route('/admindashboard/delete_article/<string:id>', methods=['POST'])
@is_admin
def del_article(id):

    db.execute('DELETE FROM articles WHERE id = ?', id)
    flash('Article Deleted', 'success')
    return redirect(url_for('admindashboard'))

@app.route('/admindashboard/article/del_comment/<string:id>', methods=['POST'])
@is_admin
def del_comment(id):

    db.execute('DELETE FROM comments WHERE id = ?', id)
    flash('Comment Deleted', 'success')
    return redirect(url_for('admindashboard'))

#add comment
@app.route('/dashboard/add_comment', methods=['POST'])
@is_logged_in
def add_comment():
    text = request.form.get('text')
    article_id = request.form.get('article_id')
    username = session['username']
    if not text:
        flash('Please Enter a text', 'danger')
        return redirect(url_for('article', id=article_id))
    db.execute('INSERT INTO comments (article_id, username, text) VALUES (?, ?, ?)', article_id, username, text)
    flash('Comment Added Successfully', 'success')
    return redirect(url_for('article', id=article_id))

#like Article
@app.route('/dashboard/like_article/<string:id>', methods=['POST'])
@is_logged_in
def like_article(id):

    #execute
    likes = db.execute('SELECT likes FROM articles WHERE id = ?', id)[0]['likes']
    likes += 1
    db.execute('UPDATE articles SET likes = ? WHERE id = ?', likes, id)
    flash('Article Liked', 'success')

    return redirect(url_for('article', id=id))

#unlike Article
@app.route('/dashboard/unlike_article/<string:id>', methods=['POST'])
@is_logged_in
def unlike_article(id):

    #execute
    likes = db.execute('SELECT likes FROM articles WHERE id = ?', id)[0]['likes']
    if likes > 0:
        likes -= 1
    else:
        likes = likes
    db.execute('UPDATE articles SET likes = ? WHERE id = ?', likes, id)
    flash('Article Unliked', 'success')

    return redirect(url_for('article', id=id))
    

#notification route
@app.route('/dashboard/notifications')
@is_logged_in
def notifications():
    notifications = db.execute('SELECT id, message, created_at, is_read FROM notifications WHERE user_id = ? ORDER BY created_at DESC', (session['id'],))
    db.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', session['id'])

    return render_template('notifications.html', notifications=notifications)

@app.route('/dashboard/connect')
@is_logged_in
def connect():
    users = db.execute('SELECT * FROM users WHERE id != ?', session['id'])
    return render_template('connect.html', users=users)

@app.route('/dashboard/message/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def message(id):
    recipient = db.execute('SELECT * FROM users WHERE id = ?', id)[0]
    messages = db.execute('SELECT * FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)', session['id'], recipient['id'], recipient['id'], session['id'])

    if request.method == 'POST':
        message = request.form.get('message')
        db.execute('INSERT INTO messages(sender_id, receiver_id, message) VALUES (?, ?, ?)', session['id'], recipient['id'], message)

        #fetch conversation btn logged in user and the recipient
        messages = db.execute('SELECT * FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)', session['id'], recipient['id'], recipient['id'], session['id'])

        return render_template('message.html', recipient=recipient, messages=messages)
    if messages:
        return render_template('message.html', recipient=recipient, messages=messages)
    else:
        return render_template('message.html', recipient=recipient)
    
@app.route('/dashboard/connections')
@is_logged_in
def connections():
    connected_users = db.execute('SELECT DISTINCT u.id, u.username FROM users u JOIN messages m ON u.id = m.receiver_id WHERE m.sender_id = ?', session['id'])

    requests = db.execute('SELECT DISTINCT u.id, u.username FROM users u JOIN messages m ON u.id = m.sender_id WHERE m.receiver_id = ?', session['id'])
    return render_template('connections.html', connected_users=connected_users, requests=requests)


if __name__ == "__main__":
    app.secret_key= 'abdulhameedkhattab07'
    app.run(debug=True)