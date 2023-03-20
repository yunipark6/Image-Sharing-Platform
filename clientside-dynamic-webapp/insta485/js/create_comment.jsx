import React from 'react';
import PropTypes from 'prop-types';

// creating a comment
class CommentInput extends React.Component {
    /* Display one comment for specified post*/
    constructor(props) {
        // Initialize mutable state
        super(props);
        this.state = { value: '' };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        //console.log("in comment ctor");
    }

    handleChange(event) {
        this.setState({value: event.target.value});
        // this.props.onCommentCreate(event.target.value);
    }

    handleSubmit(event) { // add comment to comment array, and post to database
        if (event.key == 'Enter'){
            event.preventDefault();
            //this.props.submit(this.state.value);
            this.props.submit(event.target.value);
            this.state.value = ''; // clear comment bar
        }
    }

    render() {
        return (
            <div className="comment">
                <form className="comment-form" onKeyPress= {this.handleSubmit}>
                    <input type="text" value={this.state.value} onChange= {this.handleChange}/>
                </form>
            </div>
        );
        // const comments = this.props.comments;
        // return (
        //     <fieldset>
        //         <input value={}
        //             onChange={this.handleChange} />
        //     </fieldset>
        // );
    }
}
export default CommentInput;

        

