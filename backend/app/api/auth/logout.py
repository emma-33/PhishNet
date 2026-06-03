from flask import jsonify
from flask_jwt_extended import unset_jwt_cookies
from . import bp

@bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'message': 'Logged out'})
    unset_jwt_cookies(response)
    return response, 200
