from flask import Flask
from flask import abort, jsonify, redirect, url_for, render_template
from flask_pymongo import PyMongo
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'permsdb'
app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = '27017'
app.config['MONGO_USERNAME'] = 'webapp'
app.config['MONGO_PASSWORD'] = 'c73f12a3'
mongo = PyMongo(app)

def render_our(*args, **kwargs):
    return render_template(args[0], **kwargs, int=int, enumerate=enumerate)
@app.route("/")
def index():
    return redirect(url_for("permsroot"))

@app.route("/perms/")
def permsroot():
    return "<h1>Welcome to the Online Permutation Attribute Library</h1><br/><h3>Made by: Arnar, Alfur, Sigurjon and Unnar</h3>"

@app.route("/perms/av/")
def avroot():
    return redirect(url_for('permsroot'))

@app.route("/perms/av/<patterns>/")
def avget(patterns):
    val = mongo.db.perm.find_one_or_404({"avoid":patterns})
    return jsonify({'avoid':val['avoid'],'tile':val['tile'],'examples':val['examples'],'recurrence':val['recurrence'],'genf':val['genf'],'solved_genf':val['solved_genf'],'coeffs':val['coeffs']})

@app.route("/perms/avtest")
def testing():
    val = mongo.db.perm.find_one_or_404({"avoid":"o"})
    parsed_tilings = []
    maxi = []
    maxj = []
    for tiling in val['tile']:
        obj = {}
        for tile in tiling:
            i, j = map(int, tile['point'])
            obj[(i, j)] = tile['val']
        maxi.append(max( [ i for i, _ in obj ] ) + 1)
        maxj.append(max( [ j for _, j in obj ] ) + 1)
        parsed_tilings.append(obj)
    val['tile'] = parsed_tilings

    # Test data
    val['tile'].append({(2,3): '1', (0,1): '3', (1,2): '2', (3,0): '4'})
    maxi.append(4)
    maxj.append(4)
    val['examples']['3'] = ['123', '321', '132']
    val['examples']['2'] = ['12']
    return render_our('pattern.html', val=val, maxi=maxi, maxj=maxj)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080, debug=True)
