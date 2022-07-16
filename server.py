import requests
from flask import Flask, jsonify, request, url_for, abort, send_from_directory
from backend import compute
import os
from flask_cors import CORS
import time

server = Flask(__name__, static_url_path=None, static_folder=None)
CORS(server)

# environment variable
if 'SEARCH_WIDTH' in os.environ:
    SEARCH_WIDTH = int(os.environ['SEARCH_WIDTH'])
else:
    SEARCH_WIDTH = None


def check_param(params, keys):
    for key in keys:
        if key not in params:
            return False, key
    return True, None


@server.errorhandler(404)
def error404(error):
    server.logger.warning(f"URLError:{request.url}")
    return jsonify({"status": 404, "error": "Not found."}), 404


@server.errorhandler(405)
def error405(error):
    server.logger.warning(f"URLError:{request.url}")
    return jsonify({"status": 405, "error": "Method not allowed."}), 405


@server.route("/<path:route>", methods=['GET'])
def getStatic(route):
    return send_from_directory("frontend/build", route)


@server.route("/", methods=['GET'])
def getIndex():
    return send_from_directory("frontend/build", "index.html")


@server.route("/api/candidate", methods=['GET'])
def get_andidate():
    start=time.time()
    params = request.args
    # The codes below are for testing when the backend is not ready. It uses google's API.
    # if "text" not in params:
    #     return jsonify({"status": 400, "error": "Missing parameter: text."}), 400
    # if "num" not in params:
    #     return jsonify({"status": 400, "error": "Missing parameter: num."}), 400
    # text, num = params["text"], int(params["num"])
    # r = requests.get(
    #     f"https://inputtools.google.com/request?itc=zh-t-i0-pinyin&text={text}&num={num}&cp=0&cs=1&ie=utf-8&oe=utf-8&app=demopage",
    # )
    # if r.status_code != 200:
    #     return jsonify({"status": r.status_code, "error": "Failed to connect to inputtools."}), r.status_code
    # return jsonify(r.json())
    b, key = check_param(params, ["text", "start", "size", "fix", "partical"])
    if not b:
        return jsonify({"status": 400, "error": f"Missing parameter: {key}."}), 400
    result = compute(params["text"], SEARCH_WIDTH if SEARCH_WIDTH else 3 * int(params["size"]), params["fix"] == "true", params["partical"] == "true")
    res = {"status": 200, "data": [], "totalSize": len(result), "computeTime": 0}
    for i in range(int(params["size"])):
        if int(params["start"]) + i < len(result):
            res["data"].append(result[int(params["start"]) + i])
        else:
            break
    res["computeTime"] = (time.time() - start)*1000
    return jsonify(res)


if __name__ == "__main__":
    server.run(debug=True)
