import coverage

COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/static/*'
    ]
)
COV.start()

from flask.cli import FlaskGroup
import click

from project import app, db
from project.models.user import User
from project.models.user import UserRole
from project.models.group import Group
from project.models.user_group_association import UserGroupAssociation

import unittest
cli = FlaskGroup(app)


@cli.command("recreate_db")
def recreate_db():
    """
    Recreates the database
    """
    db.reflect()
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("create_db")
def create_db():
    """
    Create the database
    """
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    """
    Seed the database
    """
    group = Group(name="Group Name")
    db.session.add(group)
    user1 = User(username='admin', name="Admin", email='admin@arsal.me', password="password", role=UserRole.ADMIN)
    user2 = User(username='user', name="User", email='teamleader@arsal.me', password="password")
    db.session.add(user1)
    db.session.add(user2)
    user_group_association1 = UserGroupAssociation(user=user1, group=group)
    db.session.add(user_group_association1)
    user_group_association2 = UserGroupAssociation(user=user2, group=group)
    db.session.add(user_group_association2)
    db.session.commit()

@cli.command()
@click.argument('file', required=False)
def test(file):
    """
    Run the tests without code coverage
    """
    pattern = 'test_*.py' if file is None else file
    tests = unittest.TestLoader().discover('tests', pattern=pattern)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@cli.command()
def cov():
    """
    Run the unit tests with coverage
    """
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


if __name__ == "__main__":
    cli()
