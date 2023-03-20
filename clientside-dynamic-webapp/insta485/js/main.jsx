import React from 'react';
import ReactDOM from 'react-dom';
import Feed from './feed';
//import Post from './post';

// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM
  // <Post url="/api/v1/posts/1/" />,
  <Feed url = "/api/v1/posts/" />,
  
  document.getElementById('reactEntry'),
);
