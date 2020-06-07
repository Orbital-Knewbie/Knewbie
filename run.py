"""
This script runs the application using a development server.
"""


from app import app, db, migrate
from app.models import *

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Question' : Question, 'Answer': Answer, 'Option' : Option, 'Response' : Response}

with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
