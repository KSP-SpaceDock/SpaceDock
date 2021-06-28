from flask import Blueprint, render_template, request, redirect, abort
import werkzeug.wrappers
from typing import Union
from flask_login import current_user

from ..common import adminrequired, with_session, json_output, TRUE_STR
from ..database import db
from ..objects import BlogPost

blog = Blueprint('blog', __name__, template_folder='../../templates/blog')


@blog.route("/blog")
def index() -> str:
    posts = (BlogPost.query.order_by(BlogPost.created.desc()).all()
             if current_user
             else BlogPost.query.filter(BlogPost.members_only != True).order_by(BlogPost.created.desc()).all())
    return render_template("blog_index.html", posts=posts)


@blog.route("/blog/post", methods=['POST'])
@adminrequired
@with_session
def post_blog() -> werkzeug.wrappers.Response:
    title = request.form.get('post-title')
    body = request.form.get('post-body')
    announcement = (request.form.get('announcement', '') in TRUE_STR)
    members_only = (request.form.get('members_only', '') in TRUE_STR)
    post = BlogPost()
    post.title = title
    post.text = body
    post.announcement = announcement
    post.members_only = members_only
    db.add(post)
    db.commit()
    return redirect("/blog/" + str(post.id))


@blog.route("/blog/<id>/edit", methods=['GET', 'POST'])
@adminrequired
@with_session
def edit_blog(id: str) -> Union[str, werkzeug.wrappers.Response]:
    post = BlogPost.query.get(id)
    if not post:
        abort(404)
    if request.method == 'GET':
        return render_template("edit_blog.html", post=post)
    else:
        post.title = request.form.get('post-title')
        post.text = request.form.get('post-body')
        post.announcement = (request.form.get('announcement', '') in TRUE_STR)
        post.members_only = (request.form.get('members_only', '') in TRUE_STR)
        return redirect("/blog/" + str(post.id))


@blog.route("/blog/<id>/delete", methods=['POST'])
@adminrequired
@json_output
@with_session
def delete_blog(id: str) -> werkzeug.wrappers.Response:
    post = BlogPost.query.get(id)
    if not post:
        abort(404)
    db.delete(post)
    return redirect("/blog")


@blog.route("/blog/<id>")
def view_blog(id: str) -> str:
    post = BlogPost.query.get(id)
    if not post:
        abort(404)
    return render_template("blog.html", post=post)
