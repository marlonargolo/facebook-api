# config.py
"""para iniciar o servidor:
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
"""
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///conversion.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
#    FACEBOOK_PIXEL_ID = '1632706371009041'  # Altere para o valor do seu Pixel
#    FACEBOOK_ACCESS_TOKEN = 'EAAOJtAC3MksBO4ZACTh9BL6uo1sxuZC92GZBDPGfYzuNZCDWcHe21wx84StBpfkAzA7kg7ih9DvkNAAl3vapCcbW5NKdWd1L4aWgJDRIoBEoOGhpGo670pI9LseZCZCYMJJTZCdvhhoRgsjIvJyiJo4DjiV6epbrnzZCmfKr8fP3vOG0cmYVKn5zwzlUJX4DElDZCkgZDZD'  # Insira aqui seu token de acesso válido
