from database import db


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    followers = db.Column(
        db.Integer,
        default=0
    )

    following = db.Column(
        db.Integer,
        default=0
    )

    verified = db.Column(
        db.Boolean,
        default=False
    )

    reports = db.Column(
        db.Integer,
        default=0
    )

    blocked = db.Column(
        db.Boolean,
        default=False
    )

    profile_image = db.Column(
        db.String(255),
        default="default.png"
    )



class Post(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    image = db.Column(
        db.String(255)
    )

    caption = db.Column(
        db.Text
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    author = db.relationship(
        "User",
        backref="posts"
    )


    likes = db.relationship(
        "Like",
        backref="post",
        cascade="all, delete"
    )


    interests = db.relationship(
        "Interest",
        backref="post",
        cascade="all, delete"
    )


    comments = db.relationship(
        "Comment",
        backref="post",
        cascade="all, delete"
    )



class Follow(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    following_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )



class Like(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("post.id")
    )



class Interest(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("post.id")
    )



class Comment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    text = db.Column(
        db.Text,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("post.id")
    )



class Message(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    text = db.Column(
        db.Text,
        nullable=False
    )