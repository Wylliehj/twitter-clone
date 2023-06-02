import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):

    def setUp(self):
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)

        u1id = 6000
        u1.id = u1id

        db.session.commit()

        self.u1 = User.query.get(u1id)

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        message = Message(text='text', user_id=self.u1.id)

        db.session.add(message)
        db.session.commit()

        self.assertIsNotNone(message)
        self.assertEqual(self.u1.messages[0].text, 'text')

    def test_message_likes(self):
        m1 = Message(text='test', user_id=self.u1.id)
        m2 = Message(text='testtest2', user_id=self.u1.id)

        u2 = User.signup('test2', 'test2@test.com', 'password', None)
        u2id = 111
        u2.id = 111

        db.session.add_all([m1, m2, u2])
        db.session.commit()

        u2.likes.append(m1)
        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == u2id).all()

        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, m1.id)
    

