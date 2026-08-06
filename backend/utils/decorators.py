from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(*roles):
    """
    Decorator that protects a route and allows only users with
    one of the specified roles to access it.

    Usage:
        @role_required('admin')
        @role_required('admin', 'staff')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # First verify a valid JWT token is present
            verify_jwt_in_request()

            # Read the role claim we embedded during login
            claims = get_jwt()
            user_role = claims.get('role')

            if user_role not in roles:
                return jsonify({
                    'error': 'Access denied. You do not have permission to perform this action.'
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator