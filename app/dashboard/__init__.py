from flask import Blueprint

# Create the dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Import routes at the bottom to avoid circular imports
from app.dashboard import routes  # noqa: F401