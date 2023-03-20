import React from 'react';

// const DeleteComment = (props) => {
//     return (
//         <div className="delete_comment">
//             <button type="button" onClick={ props.submit }>delete</button>
//         </div>
//     );
// }
// export default DeleteComment;

class DeleteComment extends React.Component {
    /* Display one comment for specified post*/
    constructor(props) {
        // Initialize mutable state
        super(props);
        this.handleClick = this.handleClick.bind(this);
        //console.log("in comment ctor");
    }

    handleClick() {
        this.props.submit(this.props.postid, this.props.commentid);
        // this.props.onCommentCreate(event.target.value);
    }

    render() {
        return (
            // <div className="delete_comment">
            <button className="delete-comment-button" onClick={ this.handleClick }>
                delete
            </button>
            // </div>
        );
    }
}
export default DeleteComment;

