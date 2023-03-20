"""
Insta485 index (user) view.

URLs include:
/
"""

import uuid
import pathlib
import os
import flask
import insta485


def get_following(connection, username):
    """Fxn."""
    my_following = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? ",
        (username, )
    ).fetchall()
    return my_following


@insta485.app.route('/uploads/<path:filename>')
def download_preview(filename):
    """Fxn."""
    if 'username' not in flask.session:
        flask.abort(403)
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename)


@insta485.app.route("/users/<user_url_slug>/", methods=['GET'])
def user1(user_url_slug):
    """Fxn."""
    # get logged in user
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    username = flask.session['username']

    # Query database USERS
    cur_users = insta485.model.get_db().execute(
        "SELECT username, fullname "
        "FROM users "
    )
    users = cur_users.fetchall()

    # Error handling
    count = 0
    for user in users:
        if user['username'] == user_url_slug:
            count = count + 1
    if count == 0:
        flask.abort(404)

    # Query table following, fetch following
    cur_following = insta485.model.get_db().execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? ",
        (user_url_slug, )
    )
    following = cur_following.fetchall()
    # Query table following, fetch followers
    cur_followers = insta485.model.get_db().execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2 = ? ",
        (user_url_slug, )
    )
    followers = cur_followers.fetchall()
    # Get who logged in user is following
    my_following = get_following(insta485.model.get_db(), username)

    cur_posts = insta485.model.get_db().execute(
        "SELECT postid, filename "
        "FROM posts "
        "WHERE owner = ? ",
        (user_url_slug, )
    )
    posts = cur_posts.fetchall()
    # Add database info to context
    context = {"user_url_slug": user_url_slug, "username": username,
               "users": users, "following": following, "followers": followers,
               "posts": posts, "my_following": my_following}
    return flask.render_template("user.html", **context)


@insta485.app.route("/posts/", methods=["POST"])
def handle_uploads():
    """Fxn."""
    # Form operation stuff...
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    username = flask.session['username']
    upload_operation = flask.request.form["operation"]
    connection = insta485.model.get_db()
    # if operation = create
    if upload_operation == "create":
        # Unpack flask object
        fileobj = flask.request.files["file"]
        if fileobj is None or fileobj == "":
            flask.abort(400)
        filename = fileobj.filename
        # Compute base name (filename without directory).
        # clashes with existing files,
        # filesystem.
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(filename).suffix
        )
        if uuid_basename is None or uuid_basename == "":
            flask.abort(400)
        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        # Puts the stuff into the database? maybe?
        connection.execute(
            "INSERT INTO posts (filename, owner) "
            "VALUES (?, ?); ",
            (uuid_basename, username)
        )
    # if operation = delete
    if upload_operation == "delete":
        postid = flask.request.form['postid']
        # Query owner of post
        owner_post = connection.execute(
            "SELECT owner "
            "FROM posts "
            "WHERE postid = ? ",
            (postid, )
        )
        owner_of_post = owner_post.fetchone()
        if owner_of_post['owner'] != username:
            flask.abort(403)
        cur_del_post = connection.execute(
            "SELECT filename "
            "FROM posts "
            "WHERE owner = ? ",
            (owner_of_post['owner'], )
        )
        del_post = cur_del_post.fetchone()
        os.remove(insta485.app.config['UPLOAD_FOLDER']/del_post['filename'])
        connection.execute(
            "DELETE FROM posts "
            "WHERE postid = ? ",
            (postid, )
        )
    target_url = flask.request.args.get("target")
    if target_url is None or target_url == "":
        target_url = "/users/" + username + '/'
    return flask.redirect(target_url)
