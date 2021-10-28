from flask import Blueprint, render_template, request, redirect, abort
import werkzeug.wrappers
from typing import Union, List
from flask_login import current_user

from ..common import adminrequired, with_session, json_output, TRUE_STR
from ..database import db
from ..objects import BlogPost


def get_all_announcement_posts() -> List[BlogPost]:
    return BlogPost.query.filter(
        BlogPost.announcement, BlogPost.draft != True
    ).order_by(BlogPost.created.desc()).all()


def get_non_member_announcement_posts() -> List[BlogPost]:
    return BlogPost.query.filter(
        BlogPost.announcement, BlogPost.draft != True, BlogPost.members_only != True
    ).order_by(BlogPost.created.desc()).all()


blog = Blueprint('blog', __name__)


@blog.route("/blog")
def index() -> str:
    return render_template("blog_index.html", posts=(
        BlogPost.query.filter(BlogPost.members_only != True, BlogPost.draft != True)
        if not current_user
        else BlogPost.query.filter(BlogPost.draft != True)
        if not current_user.admin
        else BlogPost.query
    ).order_by(BlogPost.created.desc()).all())


@blog.route("/blog/<id>")
def view_blog(id: str) -> str:
    post = BlogPost.query.get(id)
    if not post:
        abort(404)
    if post.draft:
        if not current_user or not current_user.admin:
            abort(401)
    if post.members_only:
        if not current_user:
            abort(401)
    return render_template("blog.html", post=post)


@blog.route("/blog/post", methods=['POST'])
@adminrequired
@with_session
def post_blog() -> werkzeug.wrappers.Response:
    post = BlogPost()
    post.title = request.form.get('post-title')
    post.text = request.form.get('post-body')
    post.announcement = (request.form.get('announcement', '') in TRUE_STR)
    post.members_only = (request.form.get('members_only', '') in TRUE_STR)
    post.draft = (request.form.get('draft', '') in TRUE_STR)
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
        post.draft = (request.form.get('draft', '') in TRUE_STR)
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
