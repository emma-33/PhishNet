"""
Tests for database functionality
"""
import pytest
import os
import tempfile
from utils.database import Database, get_db
from models.tracking import PageVisit, FormSubmission


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp()
    db = Database(path)
    db.init_schema()
    yield db
    db.close()
    os.close(fd)
    os.unlink(path)


def test_database_initialization():
    """Test database can be initialized"""
    db = Database(':memory:')
    db.init_schema()
    conn = db.connect()
    assert conn is not None
    db.close()


def test_database_schema_creation(temp_db):
    """Test that database schema is created correctly"""
    # Check that tables exist
    cursor = temp_db.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('page_visits', 'form_submissions')
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    assert 'page_visits' in tables
    assert 'form_submissions' in tables


def test_page_visit_creation(temp_db):
    """Test creating a page visit record"""
    visit_id = PageVisit.create(
        temp_db,
        campaign_id='test_campaign',
        user_identifier='user123',
        ip_address='127.0.0.1',
        user_agent='Test Agent',
        page_url='http://test.com/landing'
    )
    
    assert visit_id is not None
    assert visit_id > 0


def test_page_visit_retrieval(temp_db):
    """Test retrieving page visits by campaign"""
    # Create two visits for same campaign
    PageVisit.create(
        temp_db,
        campaign_id='campaign1',
        user_identifier='user1',
        ip_address='127.0.0.1',
        user_agent='Agent1',
        page_url='http://test.com/page1'
    )
    
    PageVisit.create(
        temp_db,
        campaign_id='campaign1',
        user_identifier='user2',
        ip_address='127.0.0.2',
        user_agent='Agent2',
        page_url='http://test.com/page2'
    )
    
    # Retrieve visits
    visits = PageVisit.get_by_campaign(temp_db, 'campaign1')
    assert len(visits) == 2


def test_form_submission_creation(temp_db):
    """Test creating a form submission record"""
    submission_id = FormSubmission.create(
        temp_db,
        campaign_id='test_campaign',
        user_identifier='user123',
        ip_address='127.0.0.1',
        user_agent='Test Agent',
        page_url='http://test.com/landing',
        username='testuser',
        password='testpass123',
        additional_data='{"field": "value"}'
    )
    
    assert submission_id is not None
    assert submission_id > 0


def test_form_submission_retrieval(temp_db):
    """Test retrieving form submissions by campaign"""
    # Create submissions
    FormSubmission.create(
        temp_db,
        campaign_id='campaign1',
        user_identifier='user1',
        ip_address='127.0.0.1',
        user_agent='Agent1',
        page_url='http://test.com/page1',
        username='user1',
        password='pass1'
    )
    
    FormSubmission.create(
        temp_db,
        campaign_id='campaign1',
        user_identifier='user2',
        ip_address='127.0.0.2',
        user_agent='Agent2',
        page_url='http://test.com/page2',
        username='user2',
        password='pass2'
    )
    
    # Retrieve submissions
    submissions = FormSubmission.get_by_campaign(temp_db, 'campaign1')
    assert len(submissions) == 2


def test_get_db_function():
    """Test get_db helper function"""
    db = get_db(':memory:')
    assert db is not None
    
    # get_db should return same instance for same path
    db2 = get_db(':memory:')
    assert db2 is db
    
    db.close()
