# Controllers
from flask import Flask, render_template, redirect, request
from flask import current_app as app

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login", methods= ['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route("/signup", methods= ['GET', 'POST'])
def signup():
    return render_template("user_signup.html")

@app.route("/register", methods= ['GET', 'POST'])
def register():
    return render_template("sp_registration.html")