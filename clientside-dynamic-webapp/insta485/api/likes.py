import flask
from flask import jsonify
import insta485
from insta485.api.authentication import login
from insta485.api.invalid_usage import InvalidUsage


def numLikes(postid, connection):
  """Return num likes"""
  likes_count = connection.execute(
        "SELECT COUNT (postid) "
        "FROM likes "
        "WHERE postid = ?",
        (postid, )
    ).fetchone()
  return likes_count['COUNT (postid)']
  

@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
  """Create one “like” post. Return 201 on success. Otherwise return a 409 error."""

  # Authentication
  logname = login()

  # Get args
  postid = flask.request.args.get("postid", default=1, type=int) # default??

  connection = insta485.model.get_db()
  context = {}

  # Check if like exists
  like_exists = connection.execute(
    "SELECT owner, postid "
    "FROM likes "
    "WHERE owner = ? "
    "AND postid = ? ",
    (logname, postid)
  ).fetchone()

  if like_exists is not None:
    raise InvalidUsage('Conflict', status_code = 409)
    
  # Insert like into like table
  connection.execute(
    "INSERT INTO likes (owner, postid) "
    "VALUES (?, ?);",
    (logname, postid)
  )

  # Get likeid
  like = connection.execute(
    "SELECT likeid "
    "FROM likes "
    "WHERE owner = ? "
    "AND postid = ? ",
    (logname, postid)
  ).fetchone()

  if like is not None:
    # [TODO]: Return 201 on success
    #InvalidUsage('test', status_code = 201)
    context['likeid'] = like['likeid']
    context["url"] = "/api/v1/likes/" + str(like['likeid']) + "/"

  return flask.jsonify(**context), 201

@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
def delete_like(likeid):
  """Delete like"""
  # Authentication
  logname = login()

  connection = insta485.model.get_db()

  # Insert like into like table
  connection.execute(
    "DELETE FROM likes "
    "WHERE likeid = ? ",
    (likeid, )
  )
  return '', 204
  # raise InvalidUsage('test', status_code = 204)