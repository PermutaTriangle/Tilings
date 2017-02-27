from random import randint
from flask import Flask
from flask import abort, jsonify, redirect, url_for, render_template
from flask_pymongo import PyMongo
from jinja2 import Environment
# For javascript function declarations inside python
from bson.code import Code
app = Flask(__name__)
remote = True
app.config['MONGO_DBNAME'] = 'permsdb'
app.config['MONGO_HOST'] = 'tagl.is' if remote else 'localhost'
app.config['MONGO_PORT'] = '27017'
app.config['MONGO_USERNAME'] = 'webapp'
app.config['MONGO_PASSWORD'] = 'c73f12a3'
app.config['TEMPLATES_AUTO_RELOAD'] = True
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

@app.route("/perms/stats/")
def stats():
    result = mongo.db.perm.aggregate([{
      "$group": {
        "_id": "$rank",
        "count": { "$sum": 1 },
      }
    }])
    ranks = {}
    for item in result:
        rank, count = item["_id"], item["count"]
        ranks[rank] = count

    # How many patterns depend on each pattern
    mapper = Code("""
      function() {
        for (var key in this.depends) {
          // Skip self references
          if (key === "a") continue;
          if (this.depends.hasOwnProperty(key)) {
            emit(this.depends[key], 1);
          }
        }
       }""")
    reducer = Code("function(key, values) { return values.length; }")

    result = mongo.db.perm.map_reduce(mapper, reducer, "dependency_info").find().sort([ ("value", -1), ("_id", 1) ]).limit(100)

    dependencies = { val["_id"]: -int(val["value"]) for val in result }
    print(dependencies)
    return render_our("stats.html", ranks=ranks, dependencies=dependencies)


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

@app.route("/perms/rank/<val>")
def list_by_rank(val):
    try:
        results = mongo.db.perm.find({"rank":int(val)})
        results = [x["avoid"] for x in results]
        return render_our("rank.html", results=results)
    except ValueError:
        abort(404)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# set custom filters
app.jinja_env.filters['av_list_to_url'] = av_list_to_url
app.jinja_env.filters['av_list_to_str'] = av_list_to_str


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080, debug=True)
