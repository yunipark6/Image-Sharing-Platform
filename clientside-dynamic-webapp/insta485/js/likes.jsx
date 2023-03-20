import React from 'react';
import PropTypes from 'prop-types';

// creating a comment
/*
class LikesButton extends React.Component {
    constructor(props) {
        // Initialize mutable state
        super(props);
        this.state = {likes: this.props.likes_data}
        console.log("in constructor", this.props.likes_data);
        this.handleClick = this.handleClick.bind(this)
    }

    // componentDidMount() {
    //     // This line automatically assigns this.props.url to the const variable url
    //     const { url } = this.props;
    //     console.log(url)
    
    //     // Call REST API to get the information?
    //     fetch(url, { credentials: 'same-origin' })
    //       .then((response) => {
    //         if (!response.ok) throw Error(response.statusText);
    //         return response.json();
    //       })
    //       .then((data) => {
    //         this.setState({
    //             likes: data.likes
    //         });
    //         // this.state.likes = data.likes;
    //         if (this.state.likes.lognameLikesThis == true) {
    //             // this.state.value = "unlike";
    //             this.state.isLiked = true;
    //         }
    //         else {
    //             // this.state.value = "like";
    //             this.state.isLiked = false;
    //         }
    //         //console.log(this.state)
    //       })
    //       .catch((error) => console.log(error));
    //   }

    handleClick() {
        console.log("before", this.state.likes)
        const like = {
            lognameLikesThis: this.state.likes.lognameLikesThis,
            numLikes: this.state.likes.numLikes,
            url: this.state.likes.url
        }
        // let lognameLikesThis = !this.state.likes.lognameLikesThis;
        // let numLikes = this.state.likes.numLikes;
        // if (lognameLikesThis == true) {
        //     numLikes = numLikes + 1;
        // }
        // else {
        //     numLikes = numLikes - 1;
        // }
        // this.setState({ likes: like });
        // let updated_likes = {
        //     lognameLikesThis: lognameLikesThis,
        //     numLikes: numLikes,
        //     url: this.state.likes.url
        // }
        this.setState(prevState => ({
            likes: like
        }));
        this.props.submit();
        console.log("after", this.state.likes);
    }

    render() {
        const {likes} = this.state;

        return (
            <div className="like_unlike">
                <button className="like-button" onClick={this.handleClick}>
                    {likes.lognameLikesThis ? 'unlike' : 'like' }
                </button>
            </div>
        );
    }
}
export default LikesButton;*/

const LikesButton = (props) => {
    return (
        // <div className="like_unlike">
        <button className="like-unlike-button" onClick={ props.submit }>
            {props.likes_data.lognameLikesThis ? 'unlike' : 'like' }
        </button>
        // </div>
    );
}
export default LikesButton;