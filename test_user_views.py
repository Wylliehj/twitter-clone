import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):

    def setUp(self):
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.test_user = User.signup('testuser', 'testuser@test.com', 'password', None)
        self.uid = 777
        self.test_user.id = self.uid

        db.session.commit()
    
    def tearDown(self):
        db.session.rollback()

    def test_users(self):
        with self.client as client:
            response = client.get('/users')

            self.assertIn('@testuser', str(response.data))

    def test_search(self):
        with self.client as client:
            response = client.get('/users?q=test')

            self.assertIn('@testuser', str(response.data))

    def test_show_user(self):
        with self.client as client:
            response = client.get(f'/users/{self.test_user.id}')

            self.assertIn('@testuser', str(response.data))
            self.assertEqual(response.status_code, 200)

    def test_add_like(self):
        m = Message(id=222, text="test", user_id=self.uid)
        user = User.signup('test2', 'test2@test.com', 'password', None)
        user.id = 333
        db.session.add_all([m, user])
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = user.id

            response = client.post("/users/add_like/222", follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==222).all()
            self.assertEqual(len(likes), 1)
            
