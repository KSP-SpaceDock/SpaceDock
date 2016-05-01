from flask import Blueprint, render_template, abort
from SpaceDock.objects import User, BlogPost
from SpaceDock.database import db
from SpaceDock.common import *
from SpaceDock.config import _cfg

blog = Blueprint('blog', __name__, template_folder='../../templates/blog')

@blog.route("/blog")
def index():
    posts = BlogPost.query.order_by(BlogPost.created.desc()).all()
    return render_template("static/blog_index.html", posts=posts)

@blog.route("/blog/post", methods=['POST'])
@adminrequired
@with_session
def post_blog():
    title = request.form.get('post-title')
    body = request.form.get('post-body')
    post = BlogPost()
    post.title = title
    post.text = body
    db.add(post)
    db.commit()
    return redirect("/blog/" + str(post.id))

@blog.route("/blog/<id>/edit", methods=['GET', 'POST'])
@adminrequired
@with_session
def edit_blog(id):
    post = BlogPost.query.filter(BlogPost.id == id).first()
    if not post:
        abort(404)
    if request.method == 'GET':
        return render_template("edit_blog.html", post=post)
    else:
        title = request.form.get('post-title')
        body = request.form.get('post-body')
        post.title = title
        post.text = body
        return redirect("/blog/" + str(post.id))

@blog.route("/blog/<id>/delete", methods=['POST'])
@adminrequired
@json_output
@with_session
def delete_blog(id):
    post = BlogPost.query.filter(BlogPost.id == id).first()
    if not post:
        abort(404)
    db.delete(post)
    return redirect("/")

@blog.route("/blog/<id>")
def view_blog(id):
    post = BlogPost.query.filter(BlogPost.id == id).first()
    if not post:
        abort(404)
    return render_template("static/blog.html", post=post)
