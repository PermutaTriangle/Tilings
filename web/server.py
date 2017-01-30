from flask import Flask
from flask import abort, jsonify, redirect, url_for
from flask_pymongo import PyMongo
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'permsdb'
app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = '27017'
app.config['MONGO_USERNAME'] = 'webapp'
app.config['MONGO_PASSWORD'] = 'c73f12a3'
mongo = PyMongo(app)

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

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)
