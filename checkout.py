from flask import Flask, render_template
import csv

CSV_PATH = "data/sample-users.csv"

app = Flask(__name__)

def generate_pairs(csv_path):
    with open(csv_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = [{'username':r['User name'], 'company':r['Company'], 'email':r["email"]} for r in csv_reader]
        return data

@app.route('/self-checkout')
def main_app():
    users_data = generate_pairs(CSV_PATH)
    return render_template('checkout-main.html', users=users_data)

@app.route('/self-checkout/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True) 