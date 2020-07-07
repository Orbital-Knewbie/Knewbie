"""
This script runs the application using a development server.
"""


from app import create_app, db, migrate
from app.models import *

app = create_app()

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Question' : Question, 
            'Option' : Option, 'Response' : Response,
            'Group' : Group, 'Post' : Post, 'Thread' : Thread, 
            'Proficiency' : Proficiency,
            'Quiz' : Quiz, 'Topic' : Topic}


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
