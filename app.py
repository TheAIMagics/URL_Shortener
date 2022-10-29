import os,sys, string, random
from flask import Flask, render_template,request,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from src.exception import URLShortnerException
from src.logger import logging

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///urls.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Urls(db.Model):
    id_ = db.Column("id_", db.Integer,primary_key= True)
    long = db.Column("long",db.String())
    short = db.Column("short", db.String(3))
    path = db.Column("path",db.String())
    def __init__(self, long, short, path) -> None:
        self.long = long
        self.short = short
        self.path =path

@app.before_first_request
def create_tables():
    try:
        db.create_all()
    except Exception as e:
        raise URLShortnerException(e,sys)
    

def shorten_url():
    try:
        # Sum of all lower case letters + upper_case letters
        # This way we get broader range of values form which we can pick values
        letters = string.ascii_lowercase + string.ascii_uppercase
        while True:
            # pick choices from letters we created
            rand_letters = random.choices(letters, k=3)
            rand_letters = "".join(rand_letters)
            short_url = Urls.query.filter_by(short=rand_letters).first()
            if not short_url:
                return rand_letters
    
    except Exception as e:
        raise URLShortnerException(e,sys)
    

@app.route('/', methods=["GET","POST"])
def home():
    try:
        if request.method == "POST":
            url_received = request.form['name']
            # Check if url_received already exists in db.
            found_url = Urls.query.filter_by(long= url_received).first()
            if found_url:
                # return short_url if found
                logging.info("Url already present in DB ")
                return redirect(url_for("display_short_url",url=found_url.short))
            else:
                # create short_url
                short_url = shorten_url()
                generated_path = "https://ineuronurl.herokuapp.com/"+short_url
                new_url = Urls(url_received, short_url,path=generated_path)
                db.session.add(new_url)
                db.session.commit()
                logging.info("Store URL in database")
                return redirect(url_for("display_short_url",url=short_url))
        else:
            return render_template("home.html")
    except Exception as e:
        raise URLShortnerException(e,sys)

@app.route('/<short_url>')
def redirection(short_url):
    try:
        long_url = Urls.query.filter_by(short= short_url).first()
        if long_url:
            logging.info("Send user to long_url")
            return redirect(long_url.long)
        else:
            logging.info("URL does not exists")
            return "<h1>This URL Doesnt exists</h1>"
    except Exception as e:
        raise URLShortnerException(e,sys)
    
@app.route('/display/<url>')
def display_short_url(url):
    try:
        return render_template("short_url.html",short_url_display=url,vals=Urls.query.all())
    except Exception as e:
        raise URLShortnerException(e,sys)


if __name__ == "__main__":
    app.run(port=5000,debug=True)
