import flask
from flask import jsonify
import insta485
from insta485.api.authentication import login
from insta485.api.posts import lognameOwnsThis
from insta485.api.invalid_usage import InvalidUsage

# class InvalidUsage(Exception):
#   status_code = 400

#   def __init__(self, message, status_code=None, payload=None):
#       Exception.__init__(self)
#       self.message = message
#       if status_code is not None:
#           self.status_code = status_code
#       self.payload = payload

#   def to_dict(self):
#       rv = dict(self.payload or ())
#       rv['message'] = self.message
#       rv['status_code'] = self.status_code
#       return rv

# @insta485.app.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#   response = jsonify(error.to_dict())
#   response.status_code = error.status_code
#   return response

@insta485.app.route('/api/v1/comments/', methods=['POST'])
def create_comment():
  # Authentication
  logname = login()

  # Get args
  postid = flask.request.args.get("postid", default=1, type=int) # default??
  text = flask.request.json['text']
  #text = flask.request.args.get("postid", default=1, type=int) # default??

  connection = insta485.model.get_db()
  context = {}
    
  # Insert comment into comment table
  connection.execute(
    "INSERT INTO comments (owner, postid, text) "
    "VALUES (?, ?, ?);",
    (logname, postid, text)
  )

  get_commentid = connection.execute(
    "SELECT last_insert_rowid() "
    "FROM comments "
  ).fetchone()

  # Get comment
  comment = connection.execute(
    "SELECT commentid, owner, postid, text "
    "FROM comments "
    "WHERE commentid = ? ",
    (get_commentid['last_insert_rowid()'], )
  ).fetchone()

  context["commentid"] = comment['commentid']
  context["lognameOwnsThis"] = lognameOwnsThis(comment, logname)
  context["owner"] = comment['owner']
  context["ownerShowUrl"] = "/users/" + str(comment['owner']) + "/"
  context["text"] = text
  context["url"] = "/api/v1/comments/" + str(comment['commentid'])
  return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
def delete_comment(commentid):
  """Delete comment"""
  # Authentication
  logname = login()

  connection = insta485.model.get_db()

  # Insert like into like table
  connection.execute(
    "DELETE FROM comments "
    "WHERE commentid = ? ",
    (commentid, )
  )
  return '', 204