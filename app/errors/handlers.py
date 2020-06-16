from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/error403.html'), 403

@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/error404.html'), 404

@errors.app_errorhandler(410)
def error_410(error):
    return render_template('errors/error410.html'), 410

@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/error500.html'), 500