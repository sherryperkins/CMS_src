# -*- coding:utf-8 -*-
from flask import Flask, render_template
import config

app = Flask(__name__)
app.config.from_object(config)


@app.route('/')
def index():
    return render_template('neilian.html')

if __name__ == '__main__':
    app.run()