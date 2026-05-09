from flask import Flask

from .auth import auth_bp
from .booking import booking_bp
from .complaint import complaint_bp
from .contract import contract_bp
from .house import house_bp
from .message import message_bp
from .monitor import monitor_bp
from .news import news_bp
from .payment import payment_bp
from .repair import repair_bp
from .report import report_bp
from .search import search_bp
from .user import user_bp


def register_blueprints(app: Flask):
    app.register_blueprint(auth_bp,url_prefix = '/api/auth')
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(house_bp, url_prefix="/api/houses")
    app.register_blueprint(search_bp, url_prefix="/api/search")
    app.register_blueprint(message_bp, url_prefix="/api/messages")
    app.register_blueprint(news_bp, url_prefix="/api/news")
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")
    app.register_blueprint(contract_bp, url_prefix="/api/contracts")
    app.register_blueprint(payment_bp, url_prefix="/api/payments")
    app.register_blueprint(repair_bp, url_prefix="/api/repairs")
    app.register_blueprint(complaint_bp, url_prefix="/api/complaints")
    app.register_blueprint(report_bp, url_prefix="/api/reports")
    app.register_blueprint(monitor_bp, url_prefix="/api/monitor")
