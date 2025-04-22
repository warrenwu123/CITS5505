from flask import Blueprint

# Create the auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import routes at the bottom to avoid circular imports
from app.auth import routes  # noqa: F401