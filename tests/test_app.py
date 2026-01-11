
import pytest
from app import app
import os
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Base, app
import app as application_module

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Setup in-memory database
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Patch the application session
    original_session = application_module.SessionLocal
    application_module.SessionLocal = TestingSessionLocal
    
    with app.test_client() as client:
        yield client
        
    # Teardown
    application_module.SessionLocal = original_session
    Base.metadata.drop_all(bind=engine)

def test_home(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Cafe Connect" in rv.data

def test_about(client):
    rv = client.get('/about')
    assert rv.status_code == 200
    assert b"About" in rv.data

def test_contact_get(client):
    rv = client.get('/contact')
    assert rv.status_code == 200
    assert b"Get in Touch" in rv.data

def test_contact_post(client):
    rv = client.post('/contact', data=dict(
        name='Test User',
        email='test@example.com',
        subject='Test Subject',
        message='Test Message'
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b"Success" in rv.data or b"success" in rv.data  # Check for success message based on template logic

def test_search_redirect(client):
    rv = client.post('/search', data=dict(location=''), follow_redirects=True)
    assert rv.status_code == 200
    # Should redirect to home if location is empty
    assert b"Find your perfect cafe" in rv.data

