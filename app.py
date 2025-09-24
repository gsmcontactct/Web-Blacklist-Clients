from flask import Flask, redirect, url_for, session, request
from flask_session import Session
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ID-ul clientului din Google Cloud
GOOGLE_CLIENT_ID = "719346996126-21usai8levnb6fisrd8m42j30fhj6ecl.apps.googleusercontent.com"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # doar pentru dezvoltare locală

# setup Flow
flow = Flow.from_client_secrets_file(
    "client_secrets.json",  # <-- asigură-te că fișierul are fix acest nume
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://blacklist-flask.onrender.com/callback"  # ajustează cu domeniul tău Render
)

@app.route("/")
def index():
    if "google_id" in session:
        return f"Bine ai venit, {session['name']}!"
    return '<a href="/login">Login cu Google</a>'

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        return "State mismatch", 400

    credentials = flow.credentials
    request_session = requests.Request()
    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=request_session,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
