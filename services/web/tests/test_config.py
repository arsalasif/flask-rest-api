import unittest
import os
from flask import current_app
from flask_testing import TestCase


class TestDevelopmentConfig(TestCase):
    """
    Test Development Config
    """
    def create_app(self):
        current_app.config.from_object('project.config.DevelopmentConfig')
        return current_app

    def test_app_is_development(self):
        """Ensure development settings work"""
        self.assertIsNotNone(current_app)
        self.assertEqual(current_app.config['SECRET_KEY'], os.environ.get('SECRET_KEY'))
        self.assertTrue(current_app.config['DEBUG'])
        self.assertEqual(current_app.config['SQLALCHEMY_DATABASE_URI'], os.environ.get('DATABASE_URL'))
        self.assertEqual(current_app.config['BCRYPT_LOG_ROUNDS'], 4)
        self.assertEqual(current_app.config['TOKEN_EXPIRATION_DAYS'], 30)
        self.assertEqual(current_app.config['TOKEN_EXPIRATION_SECONDS'], 0)

        self.assertNotEqual(current_app.config['POSTS_PER_PAGE'], None)
        self.assertNotEqual(current_app.config['MAX_PER_PAGE'], None)

        self.assertNotEqual(current_app.config['GITHUB_CLIENT_ID'], None)
        self.assertNotEqual(current_app.config['GITHUB_CLIENT_SECRET'], None)
        self.assertNotEqual(current_app.config['FACEBOOK_CLIENT_ID'], None)
        self.assertNotEqual(current_app.config['FACEBOOK_CLIENT_SECRET'], None)
        self.assertNotEqual(current_app.config['POSTS_PER_PAGE'], None)
        self.assertNotEqual(current_app.config['MAX_PER_PAGE'], None)


class TestTestingConfig(TestCase):
    """
    Test Testing Config
    """
    def create_app(self):
        current_app.config.from_object('project.config.TestingConfig')
        return current_app

    def test_app_is_testing(self):
        """Ensure testing settings work"""
        self.assertEqual(current_app.config['SECRET_KEY'], os.environ.get('SECRET_KEY'))
        self.assertTrue(current_app.config['DEBUG'])
        self.assertTrue(current_app.config['TESTING'])
        self.assertFalse(current_app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertEqual(current_app.config['SQLALCHEMY_DATABASE_URI'], os.environ.get('DATABASE_TEST_URL'))
        self.assertEqual(current_app.config['BCRYPT_LOG_ROUNDS'], 4)
        self.assertEqual(current_app.config['TOKEN_EXPIRATION_DAYS'], 0)
        self.assertEqual(current_app.config['TOKEN_EXPIRATION_SECONDS'], 3)

        self.assertNotEqual(current_app.config['POSTS_PER_PAGE'], None)
        self.assertNotEqual(current_app.config['MAX_PER_PAGE'], None)

        self.assertNotEqual(current_app.config['GITHUB_CLIENT_ID'], None)
        self.assertNotEqual(current_app.config['GITHUB_CLIENT_SECRET'], None)
        self.assertNotEqual(current_app.config['FACEBOOK_CLIENT_ID'], None)
        self.assertNotEqual(current_app.config['FACEBOOK_CLIENT_SECRET'], None)

class TestProductionConfig(TestCase):
    """
    Test Production Config
    """
    def create_app(self):
        current_app.config.from_object('project.config.ProductionConfig')
        return current_app

    def test_app_is_production(self):
        """Ensure production settings work"""
        self.assertEqual(current_app.config['SECRET_KEY'], os.environ.get('SECRET_KEY'))
        self.assertFalse(current_app.config['DEBUG'])
        self.assertFalse(current_app.config['TESTING'])
        self.assertEqual(current_app.config['BCRYPT_LOG_ROUNDS'], 13)
        self.assertEqual(current_app.config['TOKEN_EXPIRATION_DAYS'], 30)
        self.assertEqual(current_app.config['TOKEN_EXPIRATION_SECONDS'], 0)

        self.assertNotEqual(current_app.config['POSTS_PER_PAGE'], None)
        self.assertNotEqual(current_app.config['MAX_PER_PAGE'], None)

        self.assertNotEqual(current_app.config['GITHUB_CLIENT_ID'], None)
        self.assertNotEqual(current_app.config['GITHUB_CLIENT_SECRET'], None)
        self.assertNotEqual(current_app.config['FACEBOOK_CLIENT_ID'], None)
        self.assertNotEqual(current_app.config['FACEBOOK_CLIENT_SECRET'], None)


if __name__ == '__main__':
    unittest.main()