"""
Insta485 index (post) view.

URLs include:
/
"""
import flask
import arrow
import insta485


@insta485.app.route('/uploads/<path:filename>')
def download_file_post(filename):
    """Fxn."""
    if 'username' not in flask.session:
        flask.abort(403)
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename)


@insta485.app.route('/uploads/<path:filename>')
def download_post_prof(filename):
    """Fxn."""
    if 'username' not in flask.session:
        flask.abort(403)

    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename)


@insta485.app.route('/posts/<postid_url_slug>/')
def post(postid_url_slug):
    """Fxn."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    username = flask.session['username']
    connection = insta485.model.get_db()
    # Query database USERS
    users = connection.execute(
        "SELECT username, fullname, filename "
        "FROM users"
    ).fetchall()

    # Query database POSTS
    posts = connection.execute(
        "SELECT filename, owner, created, postid "
        "FROM posts "
        "WHERE postid = ? ",
        (postid_url_slug, )
    ).fetchone()

    # PROFILE IMAGE
    my_user = []
    for user in users:
        if user['username'] == posts['owner']:
            # download_post_prof(user['filename'])
            my_user = user
        # POST IMAGE
        # download_file_post(posts['filename'])
    time_arrow = arrow.get(posts['created'])
    posts['created'] = time_arrow.humanize()
    # Query databases COMMENTS
    comments = connection.execute(
        "SELECT owner, postid, text, commentid "
        "FROM comments "
        "WHERE postid = ? ",
        (postid_url_slug, )
    ).fetchall()

    # Query database LIKES_LIST
    likes = connection.execute(
        "SELECT owner, postid "
        "FROM likes "
    ).fetchall()

    likes_count = connection.execute(
        "SELECT COUNT (postid) "
        "FROM likes "
        "WHERE postid = ?",
        (postid_url_slug, )
    ).fetchone()

    context = {"postid_url_slug": postid_url_slug, "username": username,
               "my_user": my_user, "posts": posts, "comments": comments,
               "likes_count": likes_count['COUNT (postid)'], "likes": likes}
    return flask.render_template('post.html', **context)
