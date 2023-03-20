import flask
import insta485
import hashlib
from insta485.api.invalid_usage import InvalidUsage
from insta485.api.invalid_usage import handle_invalid_usage


def login():
    """Login handling. If logged in, returns logname."""
    if "username" not in flask.session and flask.request.authorization is None:
        raise InvalidUsage('Forbidden', status_code = 403)
    # if using a session
    if "username" in flask.session:
        logname = flask.session['username']
    # if using http
    if flask.request.authorization is not None:
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        valid = authenticate_helper(logname, password)
        if valid == False:
        # raise an exception
            raise InvalidUsage('Incorrect username or password', status_code = 403)
    return logname

# do not need abort statements but need to raise an exception
def authenticate_helper(logname, password):
    """Authenticating logname and password for http"""
    if logname is None or logname == "":
        raise InvalidUsage('Username Empty', status_code = 400)
    if password is None or password == "":
        raise InvalidUsage('Password Empty', status_code = 400)

    connection = insta485.model.get_db()

    users = connection.execute(
        "SELECT username, password "
        "FROM users "
        "WHERE username = ?", (logname, )
    ).fetchone()

    if users is None or users == "":
        raise InvalidUsage('not in query', status_code = 403)
    if logname != users['username']:
        raise InvalidUsage('logname is not equal to username in query', status_code = 403)

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
        raise InvalidUsage('Password is incorrect', status_code = 403)
    if password_db_string == passw:
        # everything passes return true
        return True
    return False