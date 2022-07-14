from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime


"""flask flask_bootstrap flask_sqlalchemy flask_wtf wtforms flask_ckeditor"""
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()],description="eg. John Doe")
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

db.create_all()


@app.route('/')
def get_all_posts():
    all_posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=all_posts)
    # return render_template("base.html")


@app.route("/post/<int:index>", methods=["GET", "POST"])
def show_post(index):
    post = db.session.query(BlogPost).filter_by(id=index).first()
    if post:
        return render_template("post.html", post=post)


@app.route("/edit-post/<int:blog_id>", methods=["GET", "POST","PATCH"])
def edit_blog(blog_id):
    update_post = db.session.query(BlogPost).filter_by(id=blog_id).first()
    edit_form = CreatePostForm(title=update_post.title,
                               subtitle=update_post.subtitle,
                               img_url=update_post.img_url,
                               author=update_post.author,
                               body=update_post.body
                               )
    if edit_form.validate_on_submit() and update_post:
        update_post.title = edit_form.title.data
        update_post.subtitle =  edit_form.subtitle.data
        update_post.author =  (edit_form.author.data).title()
        update_post.img_url = edit_form.img_url.data
        update_post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post',index=blog_id))

    return render_template("edit.html", edit_form=edit_form)


@app.route("/about/<author>", methods=["GET", "POST"])
def about(author):
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["GET", "POST"])
def create_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_blog_post = BlogPost(title=request.form["title"],
                                 subtitle=request.form["subtitle"],
                                 author=request.form["author"],
                                 img_url=request.form["img_url"],
                                 body=request.form["body"],
                                 date = datetime.datetime.now().strftime("%B %d, %Y")
                                 )
        db.session.add(new_blog_post)
        db.session.commit()

    return render_template("make-post.html", form=form)


@app.route("/delete_blog/<blog_id>", methods=["GET", "DELETE"])
def delete_blog(blog_id):
    blog_to_delete = BlogPost.query.filter_by(id=blog_id).first()
    db.session.delete(blog_to_delete)
    db.session.commit()
    return render_template('post.html', message="The blog has been deleted", post="empty")


if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)
