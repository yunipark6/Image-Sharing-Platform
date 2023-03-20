"""REST API for posts."""
import flask
from flask import jsonify
import insta485
import hashlib
from insta485.api.authentication import login
from insta485.api.likes import numLikes
from insta485.api.invalid_usage import InvalidUsage


@insta485.app.route('/api/v1/')
def get_services():
  """Returns a list of services available, not sure where this goes file-wise lol."""
  context = {
      "comments": "/api/v1/comments/",
      "likes": "/api/v1/likes/",
      "posts": "/api/v1/posts/",
      "url": "/api/v1/"
  }
  return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/')
def get_posts():
  """Returns 10 newest posts."""
  logname = login()

  # Get arguments
  size_N = flask.request.args.get("size", type=int)
  if size_N is None:
    size_N_temp = 10
  else:
    size_N_temp = size_N

  page = flask.request.args.get("page", type=int)
  if page is None:
    page_helper = 0
  else:
    page_helper = page
  
  # Error checking
  if page_helper < 0 or size_N_temp < 0:
    raise InvalidUsage('message...', status_code = 400)

  page_temp = page_helper
  if page_helper > 0:
    page_temp = page_helper*size_N_temp

  # Query 
  connection = insta485.model.get_db()

  follow_query = connection.execute(
    "SELECT username2 "
    "FROM following "
    "WHERE username1 = ? ",
    (logname, )
  )
  following = follow_query.fetchall()

  following_names = []
  for person in following:
    following_names.append(person['username2'])

  post_query_initial = connection.execute(
    "SELECT postid "
    "FROM posts "
    "WHERE (owner IN (SELECT username2 FROM following WHERE username1 = ?) OR owner = ?) "
    "ORDER BY postid Desc ",
    (logname, logname )
  )
  posts_initial = post_query_initial.fetchall()
  # Set postid_lte
  postid_lte = flask.request.args.get("postid_lte", type=int)
  if postid_lte is None:
    postid_lte_helper = default=posts_initial[0]['postid']
  else:
    postid_lte_helper = postid_lte
  # print("%s", postid_lte_helper)
  # else:
  #   postid_lte = flask.request.args.get("postid_lte", default=None, type=int)
  post_query = connection.execute(
    "SELECT postid, filename, owner, created "
    "FROM posts "
    "WHERE (owner IN (SELECT username2 FROM following WHERE username1 = ?) OR owner = ?) "
    "AND (postid <= ?) "
    "ORDER BY postid Desc "
    "LIMIT ? "
    "OFFSET ?", 
    (logname, logname, postid_lte_helper, size_N_temp, page_temp)
  )
  posts = post_query.fetchall()

  comments_query = connection.execute(
    "SELECT commentid, owner, postid, text "
    "FROM comments" 
  )
  comments = comments_query.fetchall()

  likes_query = connection.execute(
    "SELECT owner, postid "
    "FROM likes "
  )
  likes = likes_query.fetchall()

  # Context dictionary
  context = {}

  # print("%s", len(posts))
  # print("%s", page_helper)
  # print("%s", size_N_temp)
  if (len(posts) < size_N_temp):
  # if ((postid_lte_helper-((page_helper +1) * size_N_temp)) < 0):
    context["next"] = ""
  else:
    context["next"] = ("/api/v1/posts/" + "?size=" + str(size_N_temp) + "&page=" + str(page_helper+1) + "&postid_lte=" + str(postid_lte_helper))
  results = []
  for post in posts: 
    if post['owner'] == logname:
      get_post_helper(logname, results, comments, likes, post, connection)
    else:
      for person in following:
        # if following
        if post['owner'] == person['username2']: 
          get_post_helper(logname, results, comments, likes, post, connection)

  context["results"] = results
  context["url"] = "/api/v1/posts/"

  # Add queries to context['url']
  if size_N is not None:
    context["url"] = (context["url"] + "?size=" + str(size_N))
  if page is not None:
    context["url"] = (context["url"] + "&page=" + str(page))
  if postid_lte is not None:
    context["url"] = (context["url"] + "&postid_lte=" + str(postid_lte))

  return flask.jsonify(**context)

def get_post_helper(logname, results, comments, likes, post, connection):
  if post is None:
    raise InvalidUsage('Post does not exist', status_code = 404)

  post_dict = {}

  # comments
  comments_list = []
  for comment in comments:
    if post['postid'] == comment['postid']:
      comment_spec = {}
      comment_spec['commentid'] = comment['commentid']
      comment_spec['lognameOwnsThis'] = lognameOwnsThis(comment, logname)
      comment_spec['owner'] = comment['owner']
      comment_spec['ownerShowUrl'] = "/users/" + comment['owner'] + "/"
      comment_spec['text'] = comment['text']
      comment_spec['url'] = "/api/v1/comments/" + str(comment['commentid']) + "/"
      comments_list.append(comment_spec)

  post_dict["comments"] = comments_list
  post_dict["created"] = post['created']
  post_dict["imgUrl"] = "/uploads/" + post['filename']

  # likes
  likes_list = {}
  true_or_false, likeid = lognameLikesThis(post['postid'], post['owner'], logname, connection)
  likes_list["lognameLikesThis"] = true_or_false
  likes_list["numLikes"] = numLikes(post['postid'], connection)
  if likes_list["lognameLikesThis"] == True:
    likes_list["url"] = "/api/v1/likes/" + str(likeid) + "/"
  else:
    likes_list["url"] = None
  post_dict["likes"] = likes_list

  # other stuff
  post_dict["owner"] = post['owner']
  post_dict["ownerImgUrl"] = "/uploads/" + ownerImgUrl(post['owner'], connection)
  post_dict["ownerShowUrl"] = "/users/" + post['owner'] + "/"
  post_dict["postShowUrl"] = "/posts/" + str(post['postid']) + "/"
  post_dict["postid"] = post['postid']
  post_dict["url"] = "/api/v1/posts/" + str(post['postid']) + "/"

  results.append(post_dict)

def ownerImgUrl(owner, connection):
  users_query = connection.execute(
    "SELECT username, filename "
    "FROM users "
    "WHERE username = ? ",
    (owner, )
  ).fetchone()
  return users_query['filename']

def lognameOwnsThis(comment, logname):
  if (comment['owner'] == logname):
    return True
  return False

def lognameLikesThis(postid, owner, logname, connection):
  """Return true if logname likes post"""
  # false = "false"
  # true = "true"
  likes_query = connection.execute(
    "SELECT owner, postid, likeid "
    "FROM likes "
    "WHERE postid = ? "
    "AND owner = ? ",
    (postid, logname )
  ).fetchone()
  if likes_query is None:
    return False, -1
  return True, likes_query['likeid']

# def numLikes(postid, connection):
#   """Return num likes"""
#   likes_count = connection.execute(
#         "SELECT COUNT (postid) "
#         "FROM likes "
#         "WHERE postid = ?",
#         (postid, )
#     ).fetchone()
#   return likes_count['COUNT (postid)']


@insta485.app.route('/api/v1/posts/<int:postid>/')
def get_post(postid):
  """Return post on postid."""
  logname = login()
  connection = insta485.model.get_db()

  post_query = connection.execute(
    "SELECT postid, filename, owner, created "
    "FROM posts "
    "WHERE postid = ? ",
    (postid, )
  )
  post = post_query.fetchone()
  # if post['postid'] is None or post['postid'] == "":
  if post is None:
    raise InvalidUsage("Not Found", status_code = 404)
  comments_query = connection.execute(
    "SELECT commentid, owner, postid, text "
    "FROM comments "
    "WHERE postid = ? ",
    (postid, )
  )
  comments = comments_query.fetchall()

  likes_query = connection.execute(
    "SELECT owner, postid "
    "FROM likes "
    "WHERE postid = ? ",
    (postid, )
  )
  likes = likes_query.fetchall()

  # Context dictionary
  results = []
  context = {}
  get_post_helper(logname, results, comments, likes, post, connection)
  context = results[0]
  
  return flask.jsonify(**context)