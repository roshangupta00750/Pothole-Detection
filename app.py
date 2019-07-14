from flask import Flask, render_template, send_from_directory
from pymongo import MongoClient
import json
import os

static_folder = os.path.join(os.path.abspath(__file__), "static")
app = Flask(__name__, static_url_path=static_folder)


client = None


def set_up_mongo():
    global client
    client = MongoClient()


@app.route('/')
def hello_world():
    index_data = {}
    index_data["title"] = "Detect Potholes"
    return render_template('index.html')

@app.route('/js/<path:path>/')
def send_js(path):
    print(path)
    return send_from_directory('static', path)

@app.route('/populate/')
def popuate():
    return render_template('populate.html')

@app.route("/insert/<lat>/<lng>/<mag>")
def insert(lat, lng, mag):

    db = client['potholes']
    collection = db['markers']
    data = {
        "coordinates": [float(lng), float(lat)],
        "magnitude": mag
    }
    collection.insert_one(data)
    print(data)
    del(data["_id"])
    return json.dumps(data)

@app.route('/simulate/')
def simulate():
    return render_template('simulate.html')

@app.route('/fetch/<lat>/<lng>/')
def fetch(lat, lng):

    query = {
        "coordinates": {
            "$near": {
            "$geometry": {
                "type": "Point" ,
                "coordinates": [ float(lng) , float(lat) ]
            },
            "$maxDistance": 1500,
            "$minDistance": 0
                }
            }
        }
    db = client['potholes']
    collection = db['markers']
    data = list(collection.find(query, {"_id": 0}))
    print(data)
    return json.dumps(data)

@app.route("/simdata/")
def simdata():
    data = json.load(open('route.json'))
    data = data["features"][0]["geometry"]["coordinates"]
    return json.dumps(data)

if __name__ == '__main__':
    set_up_mongo()
    context = ('cert.pem', 'key.pem')
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host="0.0.0.0", port=port, ssl_context=context)
