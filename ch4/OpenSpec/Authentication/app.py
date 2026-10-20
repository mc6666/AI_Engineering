from flask import Flask

import config
from auth.oauth import oauth, oauth_bp
from auth.routes import auth_bp
from database import init_db


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config["GOOGLE_CLIENT_ID"] = config.GOOGLE_CLIENT_ID
    app.config["GOOGLE_CLIENT_SECRET"] = config.GOOGLE_CLIENT_SECRET
    oauth.init_app(app)
    init_db()
    app.register_blueprint(auth_bp)
    app.register_blueprint(oauth_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
