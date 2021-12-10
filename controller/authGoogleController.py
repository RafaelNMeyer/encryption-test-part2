import json, requests, os
from helpers import get_google_provider_cfg
from flask import redirect, request, url_for, Blueprint
from flask_login import login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
from model.user import User
from dotenv import load_dotenv

load_dotenv()

authGoogle = Blueprint('authGoogle', __name__, template_folder='templates', static_folder='static')

@authGoogle.route("/login")
def login():
    client = WebApplicationClient(os.getenv('GOOGLE_CLIENT_ID'))
    # Descobre qual URL deve ser acessada para logar com o google
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    # Usa uma biblioteca para construir um escopo pedindo informações do usário
    # como email e perfil
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@authGoogle.route("/login/callback")
def callback():
    client = WebApplicationClient(os.getenv('GOOGLE_CLIENT_ID'))

    # recupera o código exclusivo que o google enviou
    code = request.args.get("code")

    # Descobre a URL para enviar os tokens para autenticar as informações do usuário
    # Nesse caso só houve o request de informações basicas
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepara a solicitação dos tokens com ajuda do oauthlib
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET')),
    )
    # analisa os tokens com ajuda do oauthlib
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Agora que já temos os tokens, acessamos a URL do google para conseguir 
    # informações básicas de perfil e email do google
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Agora garantimos que o email é verificado pelo google e damos request no id, email e nome do usuário
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

   # Criamos um usuário com essa informação
    user = User(
        id_=unique_id, name=users_name, email=users_email
    )

    # Caso não exista no banco de dados, adicionamos ele
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email)

    # fazemos o usuário ficar logado pelo flask-session
    login_user(user)

    return redirect(url_for("authIndex.index")) 

@authGoogle.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("authIndex.index")) 