from flask import Flask, redirect, request, session, url_for, render_template
import requests
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

app.secret_key         = config['KEYS']['FLASK_APP_KEY']
CLIENT_ID              = config['KEYS']['CLIENT_ID']
CLIENT_SECRET          = config['KEYS']['CLIENT_SECRET']
CHECKBOT_KEY           = config['KEYS']['CHECKBOT_KEY']
AUTHORIZATION_BASE_URL = config['URLS']['AUTHORIZATION_BASE_URL']
TOKEN_URL              = config['URLS']['TOKEN_URL']
REDIRECT_URL           = config['URLS']['REDIRECT_URL'] # NOTE: OAuth url in snipe should match, else it is fucked.
API_BASE_URL           = config['URLS']['API_BASE_URL']
BASE_URL               = config['URLS']['BASE_URL']


@app.before_request
def logger():
    print("___________________________")
    print("URL", request.base_url)
    print("Headers:", request.headers)
    # print("Body: ", request.get_data())
    print("---------------------------")

@app.route('/self-checkout')
def index():
    return render_template('index.j2')

@app.route('/self-checkout/login')   
def home():
    print("ACCESS TOKEN = ", session.get('access_token'))
    if not session.get('access_token'):
        return render_template('login.j2', sign_state = 0)
    else:
        return render_template('login.j2', sign_state = 1)

@app.route('/self-checkout/authorize') 
def login():
    authorization_url = f'{AUTHORIZATION_BASE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}'
    return redirect(authorization_url)

@app.route('/self-checkout/callback')
def callback():
    global asset_tag, asset_id, user_id
    code = request.args.get('code')
    token_response = requests.post(TOKEN_URL, data={
        #OAuth Docs specify uri, but that didn't work for me, idk why
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URL,
        'code': code,
    })
    print("Token response = ", token_response)
    print("ASSET TAG = ", asset_tag)
    
    token_json = token_response.json()
    access_token = token_json['access_token']
    session['access_token'] = access_token
    headers = {
                "accept": "application/json",
                'Authorization': f'Bearer {access_token}'
              }
    response_assets = requests.get(f'{API_BASE_URL}/hardware/bytag/{asset_tag}?deleted=false',
                                   headers=headers)
    assets = response_assets.json()
    print("ASSETS = ", assets)
    asset_data = {
        "Name": assets["name"],
        "Asset tag": assets["asset_tag"],
        "Model": assets["model"]["name"],
        "Assigned to": assets["assigned_to"]["name"] if assets["assigned_to"] else "None",
        "Image": assets["image"]
    }
    asset_id = assets["id"]
    response_user = requests.get(f'{API_BASE_URL}/users/me',
                                 headers=headers)
    user = response_user.json()
    user_data = {
                  "Name": user["name"],
                  "username": user["username"],
                  "Email": user["email"]
                  }
    user_id = user["id"]
    print("ASSETS = ", asset_data)
    print("USER = ", user_data)
    return render_template('checkout-main.j2',
                           asset_data=asset_data, user_data=user_data,
                           asset_url=f'{BASE_URL}/hardware/{asset_id}')

@app.route('/self-checkout/assets/<tag>')
def get_assets(tag):
    global asset_tag
    asset_tag = tag
    access_token = session.get('access_token')
    print("ACESSSSSS ===>", access_token)
    if not access_token:
        return redirect(url_for('login'))
    return redirect(url_for('callback'))

@app.route('/self-checkout/confirm')
def confirm():
    global asset_id, user_id, asset_tag
    headers = {
                "accept": "application/json",
                "Authorization": f'Bearer {CHECKBOT_KEY}',
                "content-type": "application/json"
              }
    payload = {
                "checkout_to_type": "user",
                "status_id": 2,
                "assigned_user": user_id
              }
    
    response_checkout = requests.post(f'{API_BASE_URL}/hardware/{asset_id}/checkout', 
                                      json=payload, 
                                      headers=headers)
    checkout_data = response_checkout.json()
    return render_template('confirmation.j2', 
                           checkout_data=checkout_data, 
                           asset_tag=asset_tag)

if __name__ == '__main__':
    app.run(debug=True)