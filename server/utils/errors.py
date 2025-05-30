from flask import jsonify, request
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error) or 'The request could not be understood by the server.'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': str(error) or 'Authentication is required to access this resource.'
        }), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            'error': 'Forbidden',
            'message': str(error) or 'You do not have permission to access this resource.'
        }), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Not Found',
            'message': str(error) or 'The requested resource was not found.'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': str(error) or 'The method is not allowed for the requested URL.'
        }), 405
    
    @app.errorhandler(409)
    def conflict_error(error):
        return jsonify({
            'error': 'Conflict',
            'message': str(error) or 'A conflict occurred while processing the request.'
        }), 409
    
    @app.errorhandler(422)
    def unprocessable_entity_error(error):
        return jsonify({
            'error': 'Unprocessable Entity',
            'message': str(error) or 'The request was well-formed but was unable to be followed due to semantic errors.'
        }), 422
    
    @app.errorhandler(429)
    def too_many_requests_error(error):
        return jsonify({
            'error': 'Too Many Requests',
            'message': str(error) or 'Too many requests, please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred on the server.'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        # Log the error
        app.logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
        
        # Handle HTTP exceptions
        if isinstance(error, HTTPException):
            return error
        
        # Default to 500 Internal Server Error for unhandled exceptions
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred on the server.'
        }), 500
    
    @app.before_request
    def log_request_info():
        """Log request information."""
        app.logger.debug(f'Request: {request.method} {request.path}')
        if request.method in ['POST', 'PUT', 'PATCH']:
            app.logger.debug(f'Request Body: {request.get_json(silent=True) or {}}')
    
    @app.after_request
    def log_response_info(response):
        """Log response information."""
        app.logger.debug(f'Response: {response.status}')
        return response
