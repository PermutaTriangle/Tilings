from random import randint
from flask import Flask
from flask import abort, jsonify, redirect, url_for, render_template
from flask_pymongo import PyMongo
from jinja2 import Environment
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'permsdb'
app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = '27017'
app.config['MONGO_USERNAME'] = 'webapp'
app.config['MONGO_PASSWORD'] = 'c73f12a3'
mongo = PyMongo(app)

def render_our(*args, **kwargs):
    return render_template(args[0], **kwargs, int=int, enumerate=enumerate)

def av_list_to_url(v):
    return '_'.join([''.join(x.split(', ')) for x in v[5:-3].split('], [')])

def av_list_to_str(v):
    return "Av(" + ', '.join([''.join(x.split(', ')) for x in v[5:-3].split('], [')]) + ")"

@app.route("/")
def index():
    return redirect(url_for("permsroot"))

@app.route("/perms/")
def permsroot():
    return render_our('index.html')

@app.route("/perms/random/")
def randav():
    sz = mongo.db.perm.count()
    n = randint(0,sz-1)
    return redirect(url_for("avget", patterns=mongo.db.perm.find().limit(-1).skip(n).next()["avoid"]))

@app.route("/perms/av/")
def avroot():
    return redirect(url_for('permsroot'))

@app.route("/perms/av/<patterns>/")
def avget(patterns):
    val = mongo.db.perm.find_one_or_404({"avoid":patterns})
    parsed_tilings = []
    maxi = []
    maxj = []
    for tiling in val['tile']:
        obj = {}
        for tile in tiling:
            i, j = map(int, tile['point'])
            obj[(i, j)] = tile['val']
        maxi.append(max( [ i for i, _ in obj ] ) + 1 if obj else 1)
        maxj.append(max( [ j for _, j in obj ] ) + 1 if obj else 1)
        parsed_tilings.append(obj)
    val['tile'] = parsed_tilings

    return render_our('pattern.html', val=val, maxi=maxi, maxj=maxj)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
# set custom filters
app.jinja_env.filters['av_list_to_url'] = av_list_to_url
app.jinja_env.filters['av_list_to_str'] = av_list_to_str


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080, debug=True)
