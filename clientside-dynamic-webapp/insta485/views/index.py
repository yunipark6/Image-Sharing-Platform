"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import arrow
import insta485


@insta485.app.route('/uploads/<path:filename>')
def download_file(filename):
    """Fxn."""
    if 'username' not in flask.session:
        flask.abort(403)
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename)


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # if 'username' in flask.session:
    #     user = flask.session['username']
    #     return flask.redirect("/")
    # return flask.redirect("/accounts/login/")
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    username = flask.session['username']
    # Connect to database
    connection = insta485.model.get_db()
    # Query database USERS
    cur = connection.execute(
        "SELECT username, fullname, filename "
        "FROM users"
    )
    users = cur.fetchall()
    # Query database POSTS
    cur2 = connection.execute(
        "SELECT postid, filename, owner, created "
        "FROM posts "
        "ORDER BY postid Desc "
    )
    posts = cur2.fetchall()
    for post in posts:
        time_arrow = arrow.get(post['created'])
        post['created'] = time_arrow.humanize()
    # Query database LIKES_LIST
    cur3 = connection.execute(
        "SELECT owner, postid "
        "FROM likes "
    )
    likes = cur3.fetchall()
    # Initialize likes_list with 0's
    likes_list = [0] * len(posts)
    # for i in range(len(posts)):
    #     likes_list.append(0)

    # Update likes_list (likes_list[like-1] = #likes)
    for like in likes:
        likes_list[like['postid'] - 1] += 1

    # Query databases COMMENTS
    comments = connection.execute(
        "SELECT owner, postid, text "
        "FROM comments"
    ).fetchall()

    # Query database FOLLOWING
    following = insta485.views.users.get_following(connection, username)

    following.append({'username2': username})

    # Add database info to context
    context = {"username": username, "users": users, "posts": posts,
               "comments": comments, "likes": likes, "likes_list": likes_list,
               "following": following}
    return flask.render_template("index.html", **context)


@insta485.app.route('/comments/', methods=["POST"])
def handle_comments():
    """Fxn."""
    # If not logged in, redirect to login page.
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    # Get the username
    username = flask.session["username"]
    # Get the data from the form: the postid
    # And the text so we can store the comment text
    comment_operation = flask.request.form["operation"]
    connection = insta485.model.get_db()
    if comment_operation == "create":
        comment_postid = flask.request.form["postid"]
        comment_text = flask.request.form["text"]
        if comment_text == "" or comment_text is None:
            flask.abort(400)
        # Puts the stuff into the database? maybe?
        connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?);",
            (username, comment_postid, comment_text)
        )
    if comment_operation == "delete":
        commentid = flask.request.form["commentid"]
        comment_check = connection.execute(
            "SELECT owner "
            "FROM comments "
            "WHERE commentid = ? ",
            (commentid, )
        )
        valid_delete = comment_check.fetchone()
        if valid_delete['owner'] != username:
            flask.abort(403)
        connection.execute(
            "DELETE FROM comments "
            "WHERE commentid = ? ",
            (commentid, )
        )
    # Redirect the page at the end to the target url
    target_url = flask.request.args.get("target")
    if target_url is None or target_url == "":
        target_url = "/"
    return flask.redirect(target_url)


@insta485.app.route('/likes/', methods=["POST"])
def like_unlike():
    """Fxn."""
    # If not logged in, redirect to login page.
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    # Get the username
    username = flask.session["username"]
    like_postid = flask.request.form["postid"]
    like_operation = flask.request.form["operation"]
    connection = insta485.model.get_db()
    # Adds to the like table if not already there
    if like_operation == "like":
        like = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE postid = ? ",
            (like_postid, )
        )
        check_like = like.fetchall()
        for i in check_like:
            if i['owner'] == username:
                flask.abort(409)
        connection.execute(
            "INSERT INTO likes (owner, postid) "
            "VALUES(?, ?);",
            (username, like_postid)
        )
    # Deletes from the like table if operation is unlike
    if like_operation == "unlike":
        unlike = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE postid = ? ",
            (like_postid, )
        )
        check_unlike = unlike.fetchall()
        count = 0
        for i in check_unlike:
            if i['owner'] == username:
                count = count + 1
            if count == 0:
                flask.abort(409)
        connection.execute(
            "DELETE FROM likes "
            "WHERE owner = ? "
            "AND postid = ? ",
            (username, like_postid)
        )
    target_url = flask.request.args.get("target")
    if target_url is None or target_url == "":
        target_url = "/"
    return flask.redirect(target_url)
