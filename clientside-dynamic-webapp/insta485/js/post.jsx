import React from 'react';
import PropTypes from 'prop-types';
import CommentInput from './create_comment';
import LikesButton from './likes';
import DeleteComment from './delete_comment';
import moment from 'moment';


class Post extends React.Component {
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { comments: [], created: '', imgUrl: '', likes: [], owner: '', ownerImgUrl: '', ownerShowUrl: '', postShowUrl: '', postid: 0, url: '' };
    this.addNewComment = this.addNewComment.bind(this);
    this.like_unlike = this.like_unlike.bind(this);
    this.deleteComment = this.deleteComment.bind(this);
  }

  componentDidMount() {
    const { url } = this.props;

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // console.log(data)
        this.setState({
          comments: data.comments,
          created: data.created,
          imgUrl: data.imgUrl,
          likes: data.likes,
          owner: data.owner,
          ownerImgUrl: data.ownerImgUrl,
          ownerShowUrl: data.ownerShowUrl,
          postShowUrl: data.postShowUrl,
          postid: data.postid,
          url: data.url
        });
      })
      .catch((error) => console.log(error));
  }

  like_unlike() {
    // if liking
    if (this.state.likes.lognameLikesThis == false) {
      const like = {
        lognameLikesThis: true,
        numLikes: this.state.likes.numLikes + 1,
        url: ""
      }
      
      fetch(`/api/v1/likes/?postid=${this.state.postid}`, { credentials: 'same-origin', method: 'POST', })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          like.url = data.url;
          this.setState({ likes: like });
          console.log("liked image", this.state.likes);
        })
        .catch((error) => console.log(error));
    }
    // if unliking
    else {
      const like = {
        lognameLikesThis: false,
        numLikes: this.state.likes.numLikes - 1,
        url: null
      }
      const url_str = this.state.likes.url;
      const likeid = url_str[url_str.length - 2];

      fetch(`/api/v1/likes/${likeid}/`, { credentials: 'same-origin', method: 'DELETE', })
        .then((response) => {
          console.log(response)
          if (!response.ok) throw Error(response.statusText);
          return response.text(); // return response.json();
        })
        .then((data) => {
          this.setState({ likes: like });
          console.log("unliked image", this.state.likes);
        })
        .catch((error) => console.log(error));
    }
    
  }

  addNewComment(value) {
    let comment = { text: value }

    fetch(`/api/v1/comments/?postid=${this.state.postid}`, { credentials: 'same-origin', method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(comment), })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        //console.log(data)
        this.setState({ comments: [...this.state.comments, data ] });
      })
      .catch((error) => console.log(error));
  }

  // when delete button is clicked 
  deleteComment(postid, commentid) {
    //fetch make api call to delete comment
    console.log(postid, commentid);
    fetch(`/api/v1/comments/${commentid}/`, { credentials: 'same-origin', method: 'DELETE', })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText);
      return response.text();
    })
    .then((data) => {
        console.log(data)
        const newComments = this.state.comments.filter(comment => comment.commentid != commentid);
        this.setState({ comments: newComments });
    })
    .catch((error) => console.log(error));
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    // console.log("render", this.state);
    const { comments, created, imgUrl, likes, owner, ownerImgUrl, ownerShowUrl, postShowUrl, postid, url } = this.state;
    // console.log(likes)
    let numLikes = this.state.likes.numLikes
    let likes_str = ""
    numLikes == 1 ? likes_str = "like": likes_str = "likes"
    // let create = Post.moment().startOf(created).fromNow()
    return (
      
      <div className="post">
        <a href={`/users/${owner}/`}> {owner}</a>
        {/* </div><a href = {moment().startOf(created).fromNow()}</p> */}
        <a href={`/posts/${postid}/`}> {moment().startOf(created).fromNow()}</a>
        <img src={ownerImgUrl} alt="Profile Image" width="30" height="30" />

        <img src={imgUrl} alt="Post Image" width="500"/>

        <p>{numLikes} {likes_str}</p>
        <LikesButton submit={this.like_unlike} likes_data={likes} />
        {/* <LikesButton /> */}
        
        {
          comments.map((comment) => (
            <p key={comment.commentid}>
              <a href={`/users/${comment.owner}/`}> {comment.owner}</a>
              {comment.text}
              
              {/* {comment.lognameOwnsThis &&  <button type="button" onClick={this.deleteComment}>delete</button>}  */}
              { comment.lognameOwnsThis && <DeleteComment submit={this.deleteComment} postid={postid} commentid={comment.commentid}/> }
            </p>
          ))
        }
        <CommentInput submit={this.addNewComment} />
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
export default Post;
