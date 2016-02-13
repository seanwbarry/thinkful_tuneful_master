import os
from tuneful import app

from tuneful.database import session
from tuneful.models import Song, File, Base

from flask.ext.script import Manager

manager = Manager(app)

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)


@manager.command
def seed():
    for i in range(25):
        song = Song()
        file = File(filename='test song {}'.format(i)
            )
        song.file = file
        session.add(song)
    session.commit()

if __name__ == '__main__':
    manager.run()

