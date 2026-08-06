from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from extensions import db, jwt, init_redis, mail

def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    # Initialize Redis
    init_redis(app)

    # Register route blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.staff import staff_bp
    from routes.user import user_bp
    from routes.bookings import bookings_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    with app.app_context():
        # Import models HERE, before create_all, so SQLAlchemy knows about the tables
        from models.user import User
        from models.trek import Trek
        from models.booking import Booking
        db.create_all()
        seed_admin(app)

    return app

def seed_admin(app):
    """
    Create the one and only Admin account if it doesn't already exist.
    This runs automatically when the app starts for the first time.
    """
    from models.user import User  # import here to avoid circular imports

    existing_admin = User.query.filter_by(role='admin').first()
    if not existing_admin:
        admin = User(
            full_name='Admin',
            email='admin@tma.com',
            role='admin',
            status='active'
        )
        admin.set_password('admin123')  # You will implement set_password in your User model
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin account created: admin@tma.com / admin123")
    else:
        print("ℹ️  Admin already exists, skipping seed.")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)