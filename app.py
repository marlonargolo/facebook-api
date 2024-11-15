# Import required libraries and modules
from flask import Flask, request, jsonify, render_template
from config import Config
from flask_migrate import Migrate
from database import db
from models import ClickData, PurchaseData, FacebookConfig
import requests
import time
import logging
import hashlib
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
logging.basicConfig(level=logging.DEBUG)
migrate = Migrate(app, db)

# Initialize database (first run only)
with app.app_context():
    db.create_all()

# Helper function to hash user data
def hash_user_data(user_data):
    return hashlib.sha256(user_data.encode('utf-8')).hexdigest()

# Define endpoint to configure Facebook settings
@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        # Collect data from form
        pixel_id = request.form.get('pixel_id')
        access_token = request.form.get('access_token')
        campaign_name = request.form.get('campaign_name')

        # Save or update settings in the database
        config = FacebookConfig.query.filter_by(campaign_name=campaign_name).first()
        if config is None:
            config = FacebookConfig(pixel_id=pixel_id, access_token=access_token, campaign_name=campaign_name)
            db.session.add(config)
        else:
            config.pixel_id = pixel_id
            config.access_token = access_token

        db.session.commit()
        return jsonify({"message": "Settings updated successfully"}), 200

    configs = FacebookConfig.query.all()
    return render_template('config.html', configs=configs)

# Endpoint to track clicks and store URL parameters
@app.route('/track_click', methods=['GET'])
def track_click():
    fbclid = request.args.get('fbclid')
    campaign_name = request.args.get('utm_campaign')

    if not fbclid or not campaign_name:
        return jsonify({"error": "fbclid and campaign_name are required"}), 400
    
    click_data = ClickData(fbclid=fbclid)
    db.session.add(click_data)
    db.session.commit()
    
    return jsonify({"message": "Click tracked successfully"}), 200

@app.route('/get_clicks', methods=['GET'])
def get_clicks():
    # Obter o pixel_id e URL da requisição (se necessário)
    pixel_id = request.args.get("pixel_id")
    url = request.args.get("url")
    
    # Filtrar os dados de cliques com base no pixel_id e url (caso sejam necessários filtros)
    clicks = ClickData.query.filter_by(pixel_id=pixel_id).all()  # Filtrar por pixel_id
    
    # Formatar os dados de clique em JSON
    click_data = [
        {
            "fbclid": click.fbclid,
            "timestamp": click.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            # Adicione outros campos conforme necessário
        }
        for click in clicks
    ]
    
    return jsonify(click_data)

# Define function to send data to Facebook
def send_to_facebook(data):
    config = FacebookConfig.query.first()
    if not config:
        return {"error": "Facebook configuration not found"}

    pixel_id = config.pixel_id
    access_token = config.access_token
    url = f"https://graph.facebook.com/v21.0/{pixel_id}/events?access_token={access_token}"

    event_data = {
        "data": [{
            "event_name": data.get("event_name", "PageView"),
            "event_time": int(time.time()),
            "event_source_url": data.get("event_source_url"),
            "action_source": data.get("action_source", "website"),
            "user_data": {
                "email": hash_user_data(data.get("client_email", "")),
                "phone": hash_user_data(data.get("client_cel", "")),
            },
            "custom_data": {
                "currency": data.get("currency", "BRL"),
                "value": data.get("trans_value"),
                "content_type": data.get("content_type", "product"),
                # Add any additional custom_data fields as shown in your attribute screenshot
            }
        }]
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=event_data)

    if response.status_code == 200:
        logging.info(f"Facebook Response: {response.json()}")
        return {"message": "Data sent to Facebook", "facebook_response": response.json()}
    else:
        logging.error(f"Error sending data to Facebook: {response.json()}")
        return {"error": "Failed to send data to Facebook", "facebook_response": response.json()}

# Define endpoint to handle purchase webhook and send data to Facebook
@app.route('/purchase_webhook', methods=['POST'])
def purchase_webhook():
    data = request.json
    fbclid = data.get('fbclid')
    campaign_name = data.get('campaign_name')

    if not fbclid or not campaign_name:
        return jsonify({"error": "fbclid and campaign_name are required"}), 400
    
    purchase_data = PurchaseData(
        fbclid=fbclid,
        purchase_value=data.get("trans_value"),
        currency=data.get("currency", "BRL")
    )
    db.session.add(purchase_data)
    db.session.commit()
    
    response = send_to_facebook(data)
    return jsonify({"message": "Purchase tracked and sent to Facebook", "facebook_response": response}), 200

# Endpoint to capture URL and store parameters
@app.route('/capture_url', methods=['POST'])
def capture_url():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL not provided"}), 400

    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    fbclid = params.get('fbclid', [None])[0]
    campaign_name = params.get('utm_campaign', [None])[0]

    if not fbclid or not campaign_name:
        return jsonify({"error": "fbclid or utm_campaign parameters missing"}), 400
    
    click_data = ClickData(fbclid=fbclid)
    db.session.add(click_data)
    db.session.commit()

    facebook_data = {
        "event_name": data.get("event_name", "PageView"),
        "event_source_url": url,
        "client_email": params.get("email", [""])[0],
        "client_cel": params.get("phone", [""])[0],
        "currency": "BRL",
        "trans_value": params.get("value", [0])[0],
        "content_type": data.get("content_type", "product")  # Custom attribute for Facebook events
    }

    response = send_to_facebook(facebook_data)

    return jsonify({
        "message": "Data captured and sent to Facebook",
        "facebook_response": response
    }), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
