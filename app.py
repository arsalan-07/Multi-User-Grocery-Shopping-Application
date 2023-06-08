from flask import Flask,render_template
from flask_session import Session
app = Flask(__name__, static_folder='static')
app.secret_key = 'arsalan'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Import and register blueprints
from user.routes import user_bp
from admin.routes import admin_bp

app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
