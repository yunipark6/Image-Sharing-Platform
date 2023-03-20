"""Insta485 REST API."""

import insta485.api
from insta485.api.posts import get_post
from insta485.api.posts import get_posts
from insta485.api.authentication import login
from insta485.api.authentication import authenticate_helper
from insta485.api.comments import create_comment
from insta485.api.comments import delete_comment
from insta485.api.likes import create_like
from insta485.api.likes import delete_like
from insta485.api.invalid_usage import handle_invalid_usage



