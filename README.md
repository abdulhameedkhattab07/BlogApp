# Blog App
#### Video Demo:  <[URL HERE](https://www.canva.com/design/DAGS_5mejiE/HJt-iY1HZAxbOWjaOomNYg/edit?utm_content=DAGS_5mejiE&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)>
#### Description: This is My Final Project For My CS50X.
My Name is Khattab Abdulhameed. I'm From Nigeria.

# Blog Application - Final Project for CS50x
This is the final project for CS50x, a blog platform built with Flask and SQLite, where users
can post articles, like, comment, subscribe to blogs, and receive notifications.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [License](#license)

## Overview

This web application is a fully functioning blog platform where bloggers can write posts, and
users can interact with posts through comments, likes, and subscriptions. The app also
allows real-time notifications, ensuring users stay up-to-date with the
latest activities on their subscriptions.
Non-logged-in visitors can view About Us, And Also View Posts With Greater Likes, They can also subscribe to newsletter.

## Features
### For Bloggers:
- Post articles on various topics (e.g. education, coding, etc.).
- Can add an image to a post.
- View and manage subscribers to their blog.
- View analytics, such as the number of likes and comments on their articles.
### For Users:
- View posts and filter them based on categories (education, coding, etc.)
- Like and comment on articles
- Subscribe to specific blogs
- Message other users privately
### For Admin:
- Manage users from the admin dashboard (delete users, moderates posts etc.)
### General:
- Like functionality with real-time updates
- WebSocket integration for real-time notifications

## Technologies Used
- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: HTML, CSS, JavaScript

## Usage
1. Open the application in your browser:
    Run `py app.py` or `python app.py` in your terminal
2. Register as a blogger or a user:
- Bloggers can create and manage articles.
- Users can view, like, comment, and subscribe to blogs.
3. Admins can log in to the admin dashboard to manage and moderate the use of the platform.


## Database Schema
The application uses an SQLite database, and the main tables include:
- **users**: Contains user information, including roles (blogger, user, admin).
- **articles**: Stores articles created by bloggers.
- **comments**: Stores comments added to articles.
- **notifications**: Stores notifications when a blogger create a post.
- **subscriptions**: Links users to the blogs they've subscribed to.


## Contributing
Contributions are welcome! Feel free to submit issues or pull requests.
You can Still Reach Out to me for suggestions. Thanks!


## License
This project is licensed under the MIT License.