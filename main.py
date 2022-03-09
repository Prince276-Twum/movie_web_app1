import requests
from flask import Flask, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import *
import os

app = Flask(__name__)
Bootstrap(app)
db = SQLAlchemy(app)
API = "10b1e67f018e6235471c592d2464e33e"
image_add = "https://www.themoviedb.org/t/p/w600_and_h900_bestv2"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///my_movies.db")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")



class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(300), nullable=False)
    year = db.Column(db.String(300), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(300), nullable=False)
    img_url = db.Column(db.String(300), nullable=False)


class FlaskF(FlaskForm):
    your_rating = StringField(label="your rating", validators=[DataRequired()])
    your_review = StringField(label="your review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


class SecondForm(FlaskForm):
    movie_title = StringField()
    movie_submit = SubmitField()


db.create_all()


@app.route("/")
def home_page():
    query = Movie.query.order_by(Movie.rating).all()
    for i in range(len(query)):
        query[i].ranking = len(query) - i
    db.session.commit()
    return render_template("index.html", movie_list=query)


@app.route("/add_movie", methods=["POST", "GET"])
def add_page():
    second_form = SecondForm()
    if request.method == "POST":
        name_movie = second_form.movie_title.data
        response = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={API}&language=en-US&query={name_movie}&page=1&include_adult=false").json()[
            "results"]

        return render_template("select.html", form=second_form, movie_dic=response, state=request.method)
    return render_template("add.html", form=second_form, )


@app.route("/edit/post/<index>", methods=["POST", "GET"])
def edit_page(index):
    my_form = FlaskF()
    if request.method == "POST" and my_form.validate_on_submit():
        editing = Movie.query.get(index)
        editing.rating = float(my_form.your_rating.data)
        editing.review = my_form.your_review.data
        db.session.commit()
        return redirect(url_for('home_page'))
    return render_template("edit.html", form=my_form, index=index)


@app.route("/delete/<index>")
def deleter_page(index):
    to_go = Movie.query.get(index)
    db.session.delete(to_go)
    db.session.commit()
    return redirect(url_for('home_page'))


@app.route("/saving/<id_num>")
def get_details(id_num):
    another_response = requests.get(f"https://api.themoviedb.org/3/movie/{id_num}?api_key={API}&language=en-US").json()
    new_movie = Movie(
        title=another_response["original_title"],
        year=another_response["release_date"],
        description=another_response["overview"],
        rating=0,
        ranking=0,
        review=0,
        img_url=f"{image_add}{another_response['poster_path']}"
    )

    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit_page', index=new_movie.id))


if __name__ == "__main__":
    app.run(debug=True)
