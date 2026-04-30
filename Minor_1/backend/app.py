import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS

from backend.routes.auth_routes import auth_bp
from backend.routes.data_routes import data_bp
from backend.routes.predict_routes import predict_bp
from backend.routes.hr_routes import hr_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(data_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(hr_bp)

@app.route("/")
def home():
    return "FitIntel Backend Running"

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)