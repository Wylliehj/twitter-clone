"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        u2 = User.signup("test2", "email2@email.com", "password", None)

        u1_id = 1000
        u2_id = 2000
        u1.id = 1000
        u2.id = 2000

        db.session.commit()

        self.u1 = User.query.get(u1_id)
        self.u2 = User.query.get(u2_id)

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_following(self):

        self.u1.following.append(self.u2)
        db.session.commit()

        u1_follow = [user.id for user in self.u1.following]
        u2_follow = [user.id for user in self.u2.followers]

        self.assertIn(self.u2.id, u1_follow)
        self.assertIn(self.u1.id, u2_follow)

    def test_is_followed_by(self):

        self.u2.following.append(self.u1)
        db.session.commit()
        
        u1_followed_by = self.u1.is_followed_by(self.u2)
        u2_followed_by = self.u2.is_followed_by(self.u1)

        self.assertEqual(u1_followed_by, True)
        self.assertEqual(u2_followed_by, False)
        

    def test_is_following(self):
        self.u2.following.append(self.u1)
        db.session.commit()

        u1_following = self.u1.is_following(self.u2)
        u2_following = self.u2.is_following(self.u1)

        self.assertEqual(u1_following, False)
        self.assertEqual(u2_following, True)

    def test_user_create(self):
        user = User.signup('test_user1', 'test_user1@test1.com', 'password1', None)
        uid = 3000
        user.id = uid
        db.session.commit()

        user_test = User.query.get(uid)
        
        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.email, 'test_user1@test1.com')
        self.assertEqual(user_test.username, 'test_user1')
        self.assertNotEqual(user_test.password, 'password1')

        self.assertTrue(user_test.password.startswith('$2b$'))

    def test_invalid_username(self):
        user = User.signup(None, 'test_user2@test2.com', 'password2', None)
        uid = 4000
        user.id = 4000

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email(self):
        invalid = User.signup('test_user3', None, 'password3', None)
        uid = 5000
        invalid.id = 5000

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password(self):
        with self.assertRaises(ValueError) as context:
            invalid = User.signup('test_user4', 'test_user4@test.com', None, None)
        

    def test_authentication(self):
        user = User.authenticate(self.u1.username, 'password')

        self.assertEquals(user.id, self.u1.id)

        

