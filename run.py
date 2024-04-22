from flask import Flask

app = Flask(__name__)

with app.app_context():
    from app import setup_application
    setup_application(app)
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 * 1024  # 10 GB

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
