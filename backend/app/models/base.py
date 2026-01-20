from app.extensions import db

# Use Flask-SQLAlchemy's base model for proper migration support
Base = db.Model
