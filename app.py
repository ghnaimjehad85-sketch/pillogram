from flask import Flask, session, redirect, render_template, request
from sqlalchemy import or_
from database import db
from models import User, Post, Follow, Like, Interest, Comment, Message
from auth import auth

import os
from werkzeug.utils import secure_filename


app = Flask(__name__)


app.config["SECRET_KEY"] = "social_app_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///social.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

app.register_blueprint(auth)


with app.app_context():
    db.create_all()



@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")


    posts = Post.query.order_by(Post.id.desc()).all()


    return render_template(
        "home.html",
        username=session["username"],
        posts=posts
    )



@app.route("/create_post", methods=["GET", "POST"])
def create_post():

    if "user_id" not in session:
        return redirect("/login")


    if request.method == "POST":

        image = request.files["image"]
        caption = request.form["caption"]

        filename = secure_filename(image.filename)


        upload_folder = os.path.join(
            "static",
            "uploads"
        )


        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)


        image.save(
            os.path.join(
                upload_folder,
                filename
            )
        )


        post = Post(
            image=filename,
            caption=caption,
            user_id=session["user_id"]
        )


        db.session.add(post)
        db.session.commit()


        return redirect("/")


    return render_template("create_post.html")



@app.route("/search", methods=["GET", "POST"])
def search():

    if "user_id" not in session:
        return redirect("/login")


    users = []


    if request.method == "POST":

        search_text = request.form["search"]


        users = User.query.filter(
            User.username.contains(search_text)
        ).all()


    return render_template(
        "search.html",
        users=users,
        Follow=Follow,
        current_user=session["user_id"]
    )



@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")


    user = User.query.get(
        session["user_id"]
    )


    return render_template(
        "profile.html",
        user=user
    )



@app.route("/check_verification")
def check_verification():

    if "user_id" not in session:
        return redirect("/login")


    user = User.query.get(
        session["user_id"]
    )


    special_username = "حهممخلقشة"


    if user.username != special_username:

        if user.followers >= 10000:

            user.verified = True

            db.session.commit()


    return redirect("/profile")



@app.route("/follow/<int:user_id>")
def follow(user_id):

    if "user_id" not in session:
        return redirect("/login")


    follower_id = session["user_id"]


    existing_follow = Follow.query.filter_by(
        follower_id=follower_id,
        following_id=user_id
    ).first()


    if not existing_follow and follower_id != user_id:

        new_follow = Follow(
            follower_id=follower_id,
            following_id=user_id
        )


        db.session.add(new_follow)


        user = User.query.get(user_id)
        user.followers += 1


        current_user = User.query.get(follower_id)
        current_user.following += 1


        db.session.commit()


    return redirect("/search")



@app.route("/unfollow/<int:user_id>")
def unfollow(user_id):

    if "user_id" not in session:
        return redirect("/login")


    follower_id = session["user_id"]


    follow = Follow.query.filter_by(
        follower_id=follower_id,
        following_id=user_id
    ).first()


    if follow:

        db.session.delete(follow)


        user = User.query.get(user_id)

        user.followers -= 1


        current_user = User.query.get(follower_id)

        current_user.following -= 1


        db.session.commit()


    return redirect("/search")

@app.route("/like/<int:post_id>")
def like(post_id):

    if "user_id" not in session:
        return redirect("/login")


    user_id = session["user_id"]


    existing_like = Like.query.filter_by(
        user_id=user_id,
        post_id=post_id
    ).first()


    if not existing_like:

        new_like = Like(
            user_id=user_id,
            post_id=post_id
        )

        db.session.add(new_like)

        db.session.commit()


    return redirect("/")


@app.route("/interest/<int:post_id>")
def interest(post_id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    existing_interest = Interest.query.filter_by(
        user_id=user_id,
        post_id=post_id
    ).first()

    if not existing_interest:

        new_interest = Interest(
            user_id=user_id,
            post_id=post_id
        )

        db.session.add(new_interest)
        db.session.commit()

    return redirect("/")


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):

    if "user_id" not in session:
        return redirect("/login")

    text = request.form["comment"]

    new_comment = Comment(
        text=text,
        user_id=session["user_id"],
        post_id=post_id
    )

    db.session.add(new_comment)
    db.session.commit()

    return redirect("/")


@app.route("/messages/<int:user_id>", methods=["GET", "POST"])
def messages(user_id):

    if "user_id" not in session:
        return redirect("/login")

    current_user = session["user_id"]

    if request.method == "POST":

        text = request.form["message"]

        new_message = Message(
            sender_id=current_user,
            receiver_id=user_id,
            text=text
        )

        db.session.add(new_message)
        db.session.commit()

    messages = Message.query.filter(
        (
            (Message.sender_id == current_user) &
            (Message.receiver_id == user_id)
        ) |
        (
            (Message.sender_id == user_id) &
            (Message.receiver_id == current_user)
        )
    ).all()

    return render_template(
        "messages.html",
        messages=messages,
        user_id=user_id
    )

@app.route("/upload_profile", methods=["POST"])
def upload_profile():

    if "user_id" not in session:
        return redirect("/login")

    image = request.files["image"]

    if image.filename == "":
        return redirect("/profile")

    filename = secure_filename(image.filename)

    upload_folder = os.path.join("static", "profiles")

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    image.save(os.path.join(upload_folder, filename))

    user = User.query.get(session["user_id"])
    user.profile_image = filename

    db.session.commit()

    return redirect("/profile")

@app.route("/chat_list")
def chat_list():

    if "user_id" not in session:
        return redirect("/login")

    current_user = session["user_id"]

    sent = Message.query.filter_by(
        sender_id=current_user
    ).all()

    received = Message.query.filter_by(
        receiver_id=current_user
    ).all()

    users = []

    for message in sent:

        user = User.query.get(message.receiver_id)

        if user not in users:
            users.append(user)

    for message in received:

        user = User.query.get(message.sender_id)

        if user not in users:
            users.append(user)

    return render_template(
        "chat_list.html",
        users=users
    )


if __name__ == "__main__":
    app.run(debug=True)