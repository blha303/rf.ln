#!/usr/local/bin/python3

from flask import Flask, render_template, request, jsonify, Response, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import re

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app)
urlcheck = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1000))
    customid = db.Column(db.String(10))

    def __init__(self, url=None, customid=None):
        self.id = (db.session.query(db.func.max(URL.id)).scalar() or 0) + 1
        self.url = url
        self.customid = customid
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=['POST'])
@app.route("/create/<id>", methods=['POST'])
def create(id=None):
    if id and id.isdigit():
        return jsonify({"error": "Can't be just digits"})
    url = request.form.get("url", None)
    if url and urlcheck.match(url):
        urlobj = URL(url=url, customid=id if id else None)
        db.session.add(urlobj)
        db.session.commit()
        return jsonify({"message": "Success", "result": urlobj.as_dict()})
    else:
        return jsonify({"error": "Invalid url provided"})

@app.route("/<id>")
def goto(id):
    if id.isdigit():
        url = URL.query.filter_by(id=id).first()
    else:
        url = URL.query.filter_by(customid=id).first()
    if url is None:
        return Response(render_template("404.html"), 404)
    return redirect(url.url)
