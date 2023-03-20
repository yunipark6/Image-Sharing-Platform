"""
Insta485 index (follow) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route("/users/<user_url_slug>/followers/")
def followers1(user_url_slug):
    """Fxn."""
    # Get logged in user
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    username = flask.session['username']
    # Connect to database
    connection = insta485.model.get_db()
    # Query table following, fetch followers (of user_url_slug)
    followers = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2 = ? ",
        (user_url_slug, )
    ).fetchall()

    # Query database USERS
    cur_users = connection.execute(
        "SELECT username, filename "
        "FROM users "
    )
    users = cur_users.fetchall()
    # Who am I following?
    cur_my_following = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? ",
        (username, )
    )
    my_following = cur_my_following.fetchall()
    # Add database info to context
    context = {"user_url_slug": user_url_slug, "users": users,
               "username": username, "followers": followers,
               "my_following": my_following}
    return flask.render_template("followers.html", **context)


@insta485.app.route("/users/<user_url_slug>/following/")
def following(user_url_slug):
    """Fxn."""
    # Get logged in user
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    username = flask.session['username']
    # Connect to database
    connection = insta485.model.get_db()
    # Query table following, fetch followers (of user_url_slug)
    cur_following = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? ",
        (user_url_slug, )
    )
    followings = cur_following.fetchall()
    # Query database USERS
    cur_users = connection.execute(
        "SELECT username, filename "
        "FROM users "
    )
    users = cur_users.fetchall()
    # Who am I following?
    cur_my_following = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? ",
        (username, )
    )
    my_following = cur_my_following.fetchall()
    # Add database info to context
    context = {"user_url_slug": user_url_slug, "users": users,
               "username": username, "followings": followings,
               "my_following": my_following}
    return flask.render_template("following.html", **context)
