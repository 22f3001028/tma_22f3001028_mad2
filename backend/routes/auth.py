from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from flask_jwt_extended import create_access_token


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ============================================================
# REGISTER
# POST /api/auth/register
# ============================================================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Step 1 — Check required fields are present
    required = ['full_name', 'email', 'password']

    for field in required:
        if not data.get(field):
            return jsonify({
                'error': f'{field} is required'
            }), 400

    # Step 2 — Check email is not already taken
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'An account with this email already exists'
        }), 409

    # Step 3 — Create the new user
    user = User(
        full_name=data['full_name'],
        email=data['email'],
        contact_number=data.get('contact_number'),
        role='user',
        status='active'
    )

    # Hash the password before saving it
    user.set_password(data['password'])

    # Step 4 — Save user to database
    db.session.add(user)
    db.session.commit()

    # Step 5 — Return successful response
    return jsonify({
        'message': 'Account created successfully. Please log in.',
        'user': user.to_dict()
    }), 201


# ============================================================
# LOGIN
# POST /api/auth/login
# ============================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Step 1 — Check required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({
            'error': 'Email and password are required'
        }), 400

    # Step 2 — Find the user by email
    user = User.query.filter_by(
        email=data['email']
    ).first()

    if not user:
        return jsonify({
            'error': 'Invalid email or password'
        }), 401

    # Step 3 — Check the password
    if not user.check_password(data['password']):
        return jsonify({
            'error': 'Invalid email or password'
        }), 401

    # Step 4 — Check account status
    if user.status == 'blacklisted':
        return jsonify({
            'error': 'Your account has been suspended. Please contact the administrator.'
        }), 403

    if user.status == 'inactive':
        return jsonify({
            'error': 'Your account is inactive. Please contact the administrator.'
        }), 403

    # Step 5 — Create JWT token
    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'role': user.role
        }
    )

    # Step 6 — Return token and user information
    return jsonify({
        'message': f'Welcome back, {user.full_name}!',
        'token': token,
        'user': user.to_dict()
    }), 200