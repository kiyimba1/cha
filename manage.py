#!/usr/bin/env python

import os
from app import create_app, db
from app.models import User, Role, Post, Follow
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
COV= None
if os.environ.get('FLASK_COVERAGE'):
        import coverage
        COV = coverage.coverage(branch=True, include='app/*')

app = create_app(os.getenv('FLASK_CONFIG') )
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Follow=Follow)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False):
    "Run the unit tests"
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summery:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' %covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Starts the application under the code profiler"""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()

@manager.command
def deploy():
    from flask_migrate import upgrade
    from app.models import Role, User

    upgrade()

    Role.insert_roles()

    User.add_self_follows()


if __name__ == '__main__':
    manager.run()

