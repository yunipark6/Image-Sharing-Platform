import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

//call post render function
class Feed extends React.Component {
    constructor(props) {
      super(props);
      this.state = { next: "", posts: [], url: "", hasMore: true};
      this.infinite_scroll = this.infinite_scroll.bind(this);
      // this.next_boolean=this.next_boolean.bind(this)
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
          //console.log(data)
          this.setState({
            next: data.next,          
            posts: data.results,
            url: data.url
          });
          if (this.state.next === "") {
            this.setState({
              hasMore: false
            });
          }
          //console.log(this.state.posts);
        })
        .catch((error) => console.log(error));
    }

    infinite_scroll(){
      //gets next 10 posts in database
      //fetch the next posts on the page, using the next url we got
      //console.log(this.state.next)
      if (this.state.next === "") {
        this.setState({
          hasMore: false
        });
      }
      fetch(this.state.next, { credentials: 'same-origin', })
      //error checking
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        //console.log(response);
        return response.json();
      })
      //adding the data to the state i hope this works
      .then((data) => {
        console.log(data)
        //const len = data.results.length;
        this.setState({
          next: data.next,
          // posts: [...this.state.posts, data.results],
          url: data.url
        });
        // for (let i = 0; i < len; ++i) {
        //   this.setState({
        //     posts: [...this.state.posts, data.results[i]]
        //   })
        // }
        this.setState(prevState => ({
          posts: prevState.posts.concat(data.results),
        }));
        if (this.state.next === "") {
          this.setState({
            hasMore: false
          });
        }        
        // this.setState({ posts: [...this.state.posts, data ] });
      })
      .catch((error) => console.log(error));
    }

    // next_boolean(){
    //   if (this.state.next === "") {
    //     console.log("no next")
    //     return false;
    //   }
    //   else {
    //     console.log("next")
    //     return true;
    //   }
    // }


  // just pass in data you have, not URL when u call post component
    render() {
      // This line automatically assigns this.state.imgUrl to the const variable imgUrl
      // and this.state.owner to the const variable owner
      // console.log(this.state.posts);
      const { next, url, hasMore } = this.state;
      let post_length = this.state.posts.length;
      
      return (
        <div className="feed">
            {
                <InfiniteScroll
                dataLength={post_length} //This is important field to render the next data
                next={this.infinite_scroll}
                hasMore={hasMore} 
                loader={<h4>Loading...</h4>}
                endMessage={
                  <p style={{ textAlign: 'center' }}>
                    <b>Yay! You have seen it all</b>
                  </p>
                }>

                { 
                this.state.posts.map((post) => (
                  // <p key={post.postid}>
                    <Post url={`/api/v1/posts/${post.postid}/`} key={post.postid} />
                  // </p>
                ))
                }

                </InfiniteScroll>
            }       
        </div>
      );
    }
  }
  
  Feed.propTypes = {
    url: PropTypes.string.isRequired,
  };
  export default Feed;