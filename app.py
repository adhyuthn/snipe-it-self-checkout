from flask import Flask, redirect, request, session, url_for, render_template
import requests

app = Flask(__name__)
app.secret_key = 'asfn32ewowiif'

CLIENT_ID = '3'
CLIENT_SECRET = 'vDlOuqrvODeKNgnE0CYwsZKYIr33uX81h29fYL20'
RIGBRO_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZGY1Yzc4MWUwMDA0MmE4MGNjNjBhZWFmOWU5MjAzZGJkOGI1NjI2NTcxMDVjNzIyZmE5ZWI2NDc2MGU5NWU4ZGJjNGU4YzdlOWUzNjlmNjIiLCJpYXQiOjE3MTY5ODgzNDYuNDAyMDIsIm5iZiI6MTcxNjk4ODM0Ni40MDIwMjIsImV4cCI6MjE5MDI4NzU0Ni4zOTY2LCJzdWIiOiIxMiIsInNjb3BlcyI6W119.2uUIYmCBLVSXq7ur9S1Fd6RDOipk33QfhNensSoT_O-1Zl72YLHnAD3HTaha8F4gU5U7Z_W0UKZw5Z9zFigqFoIF3tAYscYBrGm0fZPXd4KSO80PREjjWf9Ah2yyUIKeePFbirud038Mg_bW0ds0QXZNjZCByIwD5zo0LQaAw6aDQ9jQI7Rxx0oAdWKiJAadOx6DyopeKPlaJRDfTU1CpbT0vpBdAzY-6rPOeSkgq_IFPUrkltKHoS1yHwWTPN12tZpJuumlW1kQLgqM1t24gYFttHnnYzKXBih2-1Vcf6_TXjuLCpWKpbRAr6EQTwvuFjGiOpqyMy-49zRXifoOXjyQv8FC-SkFYk08rDXYr1cewDLNig-U42O462cex2oS4IWQZY-jA2R_mO2Rf_ZhMniava6GgP3k7NBW49Rv7L-ceoCsc186mSq109cSiGgc-03tOAlRqPT2cZRLZ2SV1Uh26cOBUiJpjUMDdlzHHwbVFHUkvdC5w_gCXCdMzhIZxWGpgEOW_TYQPPEZMN4u7zF_xrTkNFeTA5ovB5q8fFYjmR911RiwBWvdwpjQrJCIDuSjgPOKdsNm7tDSmyFdHVuaPxPvMC3WQF6196_VcwW6OG_qPN685cozwfNMb1kKv7WORVmXPtOJ86TPrWYXeOIdcyYdSbbxLsYmW0OqR3c'
AUTHORIZATION_BASE_URL = 'http://testsnipe.eastus.cloudapp.azure.com/oauth/authorize'
TOKEN_URL = 'http://testsnipe.eastus.cloudapp.azure.com/oauth/token'
REDIRECT_URL = 'http://localhost:5000/self-checkout/callback' # NOTE: OAuth url in snipe should match, else it is fucked.
API_BASE_URL = 'http://testsnipe.eastus.cloudapp.azure.com/api/v1'
BASE_URL = 'http://testsnipe.eastus.cloudapp.azure.com'


@app.route('/self-checkout')
def index():
    return render_template('index.jinja')

@app.route('/self-checkout/login')   
def home():
    return render_template('login.jinja')

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
    print("ENTHA", asset_data)
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
    return render_template('checkout-main.jinja',
                           asset_data=asset_data, user_data=user_data,
                           asset_url=f'{BASE_URL}/hardware/{asset_id}')

@app.route('/self-checkout/assets/<tag>')
def get_assets(tag):
    global asset_tag
    asset_tag = tag
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))
    return redirect(url_for('callback'))

@app.route('/self-checkout/confirm')
def confirm():
    global asset_id, user_id, asset_tag
    headers = {
                "accept": "application/json",
                "Authorization": f'Bearer {RIGBRO_KEY}',
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
    return render_template('confirmation.jinja', 
                           checkout_data=checkout_data, 
                           asset_tag=asset_tag)

if __name__ == '__main__':
    app.run(debug=True)