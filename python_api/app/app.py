from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

CORS(
  app,
  supports_credentials=True
)

@app.route('/')
def index():
  return jsonify({
    "message": "test message!!!"
  })

if __name__ == '__main__':
  app.run(debug=True)
