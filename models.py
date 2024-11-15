# models.py

from database import db
from datetime import datetime

class ClickData(db.Model):
    __tablename__ = 'click_data'
    
    id = db.Column(db.Integer, primary_key=True)
    fbclid = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pixel_id = db.Column(db.String(255), nullable=True)  # Temporarily allow NULL / Adicionando o campo pixel_id
    # Outros dados dos cliques (utm_source, utm_campaign, etc.)
    
class PurchaseData(db.Model):
    __tablename__ = 'purchase_data'
    
    id = db.Column(db.Integer, primary_key=True)
    fbclid = db.Column(db.String(255), nullable=False)
    purchase_value = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class FacebookConfig(db.Model):
    __tablename__ = 'facebook_config'
    
    id = db.Column(db.Integer, primary_key=True)
    pixel_id = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    campaign_name = db.Column(db.String(255), nullable=True)  # Nome da campanha para identificação
