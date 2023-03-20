"""
Insta485 index (login) view.

URLs include:
/accounts
"""
import uuid
import pathlib
import os
import hashlib
import flask
import insta485


def encrypting_old_pass(right_pass, old_passw):
    """Fxn."""
    # password hashing stuff
    passw = right_pass
    words = passw.split('$')
    # getting the passwords
    algorithm = 'sha512'
    # salt = uuid.uuid4().hex
    salt = words[1]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + old_passw
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


@insta485.app.route('/uploads/<path:filename>')
def download_prof_edit(filename):
    """Fxn."""
    if 'username' not in flask.session:
        flask.abort(403)
    # username = flask.session['username']
    # # query photo from uploads
    # connection = insta485.model.get_db()
    # cur_photo = connection.execute(
    #     "SELECT filename "
    #     "FROM users "
    #     "WHERE username = ? ",
    #     (username, )
    # )
    # photo = cur_photo.fetchone()

    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename)


@insta485.app.route('/accounts/login/', methods=['GET'])
def authenticate():
    """Fxn."""
    # check if user is in database
    # if flask.request.method == 'POST':
    return flask.render_template('login.html')


@insta485.app.route("/accounts/logout/", methods=['POST'])
def logout():
    """Fxn."""
    if 'username' in flask.session:
        flask.session.clear()
        return flask.redirect("/accounts/login/")
    return flask.redirect("/accounts/login/")


@insta485.app.route("/accounts/create/", methods=['GET'])
def create():
    """Fxn."""
    return flask.render_template('create.html')


@insta485.app.route("/accounts/delete/", methods=['GET'])
def delete():
    """Fxn."""
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    username = flask.session['username']
    context = {"username": username}
    return flask.render_template('delete.html', **context)


@insta485.app.route("/accounts/password/")
def password1():
    """Fxn."""
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    username = flask.session['username']
    context = {"username": username}
    return flask.render_template('password.html', **context)


@insta485.app.route("/accounts/edit/", methods=['GET'])
def edit():
    """Fxn."""
    if 'username' not in flask.session:
        flask.redirect('/accounts/login/')
    username = flask.session['username']
    connection = insta485.model.get_db()
    # print('%s', username)
    cur_edit = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users "
        "WHERE username = ? ",
        (username, )
    )
    users = cur_edit.fetchone()
    download_prof_edit(users['filename'])
    context = {"users": users}
    return flask.render_template("edit.html", **context)


def helper_create():
    """Fxn."""
    if 'username' in flask.session:
        user = flask.session['username']
        return flask.redirect("/accounts/edit/")

    # Unpack flask object
    fileobj = flask.request.files["file"]
    file_photo = fileobj.filename
    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and
    # ensure that the name is compatible with the
    # filesystem.
    uuid_basename = "{stem}{suffix}".format(
        stem=uuid.uuid4().hex,
        suffix=pathlib.Path(file_photo).suffix
    )

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    if flask.request.form['operation'] == "create":
        # file_photo = flask.request.form['file']
        fullname = flask.request.form['fullname']
        username = flask.request.form['username']
        email = flask.request.form['email']
        password = flask.request.form['password']
        # check if fields are empty
        if uuid_basename == "" or uuid_basename is None:
            flask.abort(400)
        if fullname == "" or fullname is None:
            flask.abort(400)
        if username == "" or username is None:
            flask.abort(400)
        if email == "" or email is None:
            flask.abort(400)

        if password == "" or password is None:
            flask.abort(400)

        # check if username already exists
        users = insta485.model.get_db().execute(
            "SELECT username "
            "FROM users "
        ).fetchall()

        for user in users:
            if user['username'] == username:
                flask.abort(409)

        # hash password
        hash_obj = hashlib.new('sha512')
        password_salted = uuid.uuid4().hex + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join(['sha512', uuid.uuid4().hex,
                                      password_hash])
        insta485.model.get_db().execute(
            "INSERT INTO users(fullname, email, filename, password, username) "
            "VALUES(?, ?, ?, ?, ?) ",
            (fullname, email, uuid_basename, password_db_string, username)
        )
        flask.session["username"] = username
    target_url = flask.request.args.get("target")
    if target_url is None or target_url == "":
        target_url = "/"
    return flask.redirect(target_url)


def helper_edit():
    """Fxn."""
    if 'username' not in flask.session:
        flask.abort(403)
    username = flask.session['username']
    if flask.request.form['update'] == "submit":
        fileobj = flask.request.files['file']
        file_photo = fileobj.filename
        fullname = flask.request.form['fullname']
        email = flask.request.form['email']
        # password = flask.request.form['password']
        # check if fields are empty
        connection = insta485.model.get_db()
        if fullname == "" or fullname is None:
            flask.abort(400)
        if email == "" or email is None:
            flask.abort(400)
        # if file photo exits then insert into file
        if file_photo is not None:
            uuid_basename = "{stem}{suffix}".format(
                stem=uuid.uuid4().hex,
                suffix=pathlib.Path(file_photo).suffix
            )

            # Save to disk
            path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
            fileobj.save(path)
            connection.execute(
                "UPDATE users "
                "SET filename = ? "
                "WHERE username = ? ",
                (uuid_basename, username)
            )
        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ? ",
            (fullname, email, username)
        )
    target_url = flask.request.args.get("target")
    if target_url is None or target_url == "":
        target_url = "/users/<user_url_slug>/"
    return flask.redirect(target_url)


def helper_delete():
    """Fxn."""
    # if user is not logged it
    # breakpoint()
    if 'username' not in flask.session:
        flask.abort(403)
    username = flask.session['username']
    # connect to database
    connection = insta485.model.get_db()
    # deleting profile photos
    cur_del = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ? ",
        (username, )
    )
    del_img = cur_del.fetchone()
    os.remove(insta485.app.config['UPLOAD_FOLDER']/del_img['filename'])

    cur_del_posts = connection.execute(
        "SELECT filename "
        "FROM posts "
        "WHERE owner = ? ",
        (username, )
    )
    del_img_post = cur_del_posts.fetchall()
    for i in del_img_post:
        os.remove(insta485.app.config['UPLOAD_FOLDER']/i['filename'])
    # del_img(del_img)
    connection.execute(
        "DELETE FROM users "
        "WHERE username = ? ",
        (username, )
    )
    flask.session.clear()
    # flask.redirect('/accounts/login/')
    target_url = flask.request.args.get("target")
    if target_url is None or target_url == "":
        target_url = "/accounts/create/"
    return flask.redirect(target_url)


def helper_password():
    """Fxn."""
    # breakpoint()
    # if user is not logged it
    if 'username' not in flask.session:
        flask.abort(403)
    # connect to database
    # if any of the fields are empty abort
    old_passw = flask.request.form['password']
    if old_passw == "" or old_passw is None:
        flask.abort(400)
    connection = insta485.model.get_db()
    if flask.request.form['operation'] == "update_password":
        # if flask.request.form['update_password'] == "submit":
        new_passw1 = flask.request.form['new_password1']
        new_passw2 = flask.request.form['new_password2']
        if new_passw1 == "" or new_passw1 is None:
            flask.abort(400)
        if new_passw2 == "" or new_passw2 is None:
            flask.abort(400)
        # check if old password is correct
        username = flask.session['username']
        user_passw = connection.execute(
            "SELECT password "
            "FROM users "
            "WHERE username = ? ",
            (username, )
        ).fetchone()
        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + new_passw2
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])
        old_passw_e = encrypting_old_pass(user_passw['password'], old_passw)
        # checking if old password matches
        if user_passw['password'] != old_passw_e:
            flask.abort(403)
        if user_passw['password'] == old_passw_e:
            if new_passw1 == new_passw2:
                connection.execute(
                    "UPDATE users "
                    "SET password = ? "
                    "WHERE username = ? ",
                    (password_db_string, username)
                )
            else:
                flask.abort(401)
    target_url = flask.request.args.get("target")
    if target_url is None or target_url == "":
        target_url = "/"
    return flask.redirect(target_url)


@insta485.app.route('/accounts/', methods=['POST'])
def handle_accounts():
    """Fxn."""
    # if flask.request.method == 'post':
    operation = flask.request.form['operation']
    # login = flask.request.form['submit']
    if operation == "login":
        # if login == 'login':
        # get the username and password user input
        username = flask.request.form['username']
        password = flask.request.form['password']
        if username is None or username == "":
            flask.abort(400)
        if password is None or password == "":
            flask.abort(400)
        # connect to database
        connection = insta485.model.get_db()
        users = connection.execute(
            "SELECT username, password "
            "FROM users "
            "WHERE username = ?", (username, )
        ).fetchone()

        if users is None or users == "":
            flask.abort(403)
        if username != users['username']:
            flask.abort(403)
        # password hashing stuff
        passw = users['password']
        words = passw.split('$')
        # getting the passwords
        algorithm = 'sha512'
        # salt = uuid.uuid4().hex
        salt = words[1]
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])
        # check if password matches
        if password_db_string != passw:
            flask.abort(403)
        if password_db_string == passw:
            # store username
            flask.session["username"] = flask.request.form.get("username")
            return flask.redirect("/")
    if operation == "edit_account":
        helper_edit()
    if operation == "create":
        helper_create()
    if operation == "delete":
        helper_delete()
    if operation == "update_password":
        helper_password()
    target_url = flask.request.args.get("target")
    if target_url is None or target_url == "":
        target_url = "/"
    return flask.redirect(target_url)
