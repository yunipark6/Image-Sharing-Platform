"""
Insta485 index (explore) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/uploads/<path:filename>')
def download_pic(filename):
    """Fxn."""
    if 'username' not in flask.session:
        flask.abort(403)
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename)


@insta485.app.route('/explore/')
def explore():
    """Fxn."""
    if 'username' not in flask.session:
        return flask.redirect("/accounts/logout/")
    username = flask.session['username']
    # connect to database
    connection = insta485.model.get_db()
    cur_users = connection.execute(
        "SELECT username, filename "
        "FROM users "
    )
    users = cur_users.fetchall()
    cur_following = connection.execute(
        "SELECT username1, username2 "
        "FROM following "
    )
    following = cur_following.fetchall()
    # Figure out who logged in user is not following
    not_following = []
    for user in users:
        if user['username'] == username:
            continue
        tracker = False
        for pair in following:
            if pair['username1'] == username:
                if pair['username2'] == user['username']:
                    tracker = True
        if tracker is False:
            not_following.append(user)
            # download_pic(user['filename'])
    # Add database info to context
    context = {"username": username, "users": users,
               "not_following": not_following}
    return flask.render_template("explore.html", **context)


@insta485.app.route('/following/', methods=["POST"])
def follow_button():
    """Fxn."""
    # If not logged in, redirect to login page.
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    # Get the username
    username1 = flask.session["username"]
    username2 = flask.request.form['username']
    print("%s", username1)
    print("%s", username2)
    connection = insta485.model.get_db()
    button_operation = flask.request.form['operation']
    # follow button
    if button_operation == "follow":
        connection.execute(
            "INSERT INTO following(username1, username2) "
            "VALUES(?, ?) ",
            (username1, username2)
        )
    if button_operation == "unfollow":
        connection.execute(
            "DELETE FROM following "
            "WHERE username1 = ? "
            "AND username2 = ? ",
            (username1, username2)
        )
    target_url = flask.request.args.get("target")
    if target_url is None or target_url == "":
        target_url = "/"
    return flask.redirect(target_url)
