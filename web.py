import flask
from flask import Flask, request, jsonify
from flask import send_from_directory
from flask import render_template
import time
import tmf as tmfService

app = Flask(__name__, template_folder='webresources/templates',
            static_folder='webresources/public')


@app.route('/public/<path:path>', methods=['GET', 'POST'])
def public(path):
    return send_from_directory('webresources/public', path)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

# api


mapStorage = []
mapStorageLastUpdate = 0
scoresStorage = {}
scoresStorageLastUpdate = 0


@app.route('/api/get_maps', methods=['GET'])
def get_maps():
    global mapStorage, mapStorageLastUpdate
    if len(mapStorage) == 0:
        mapStorage = tmfService.get_maps()

    # if used for the first time or last update was more than 60 seconds ago
    if mapStorageLastUpdate == 0 or time.time() - mapStorageLastUpdate > 60:
        mapStorage = tmfService.get_maps()
        mapStorageLastUpdate = time.time()
    # if last update was less than 60 seconds ago
    elif time.time() - mapStorageLastUpdate < 60:
        return jsonify(mapStorage)

    return jsonify(mapStorage)


@app.route('/api/get_scores', methods=['GET'])
def get_scores():
    global scoresStorage, scoresStorageLastUpdate

    if len(mapStorage) == 0:
        return jsonify({
            "error": "Get maps first"
        })

    if scoresStorageLastUpdate == 0 or time.time() - scoresStorageLastUpdate > 60:
        scoresStorage = tmfService.get_scores(tmfService.ids, mapStorage)
        scoresStorageLastUpdate = time.time()
    elif time.time() - scoresStorageLastUpdate < 60:
        return jsonify(scoresStorage)

    return jsonify(scoresStorage)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
