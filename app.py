from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from dg_asr import TranscriptionService


app = Flask(__name__)
CORS(app)
ts=TranscriptionService()

@app.route('/send_audio_data', methods=['POST'])
def call():
    data = request.form["data"]
    value = str(ts.streaming_data(data))
    if len(value)>0:
        return jsonify({"output":value})
    else:
        return jsonify({"output":"_____"})
