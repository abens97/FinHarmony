# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 14:59:35 2021

@author: Rapha
"""

from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("converter.html", message= "test")

if __name__ == "__main__":
    app.run()