import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Testlerden önce veri tabanını oluşturmak ve testlerden sonra temizlemek için kullanılan test düzeneği."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Test sırasında veri tabanı bağlantısı oluşturur ve testten sonra bağlantıyı kapatır."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Veri tabanı ve 'users' tablosunun oluşturulmasını test eder."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "'users' tablosu veri tabanında bulunmalıdır."

def test_add_new_user(setup_database, connection):
    """Yeni bir kullanıcının eklenmesini test eder."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Kullanıcı veri tabanına eklenmiş olmalıdır."


def test_add_existing_user(setup_database):
    """Var olan bir kullanıcı adıyla kullanıcı eklemeye çalışmayı test eder."""
    add_user('duplicate_user', 'dup@example.com', 'password123')
    result = add_user('duplicate_user', 'other@example.com', 'password456')
    assert result is False

def test_authenticate_user_success(setup_database):
    """Başarılı kullanıcı doğrulamasını test eder."""
    add_user('auth_user', 'auth@example.com', 'secret_pass')
    assert authenticate_user('auth_user', 'secret_pass') is True

def test_authenticate_non_existent_user(setup_database):
    """Var olmayan bir kullanıcıyla doğrulama yapmayı test eder."""
    assert authenticate_user('non_existent', 'password') is False

def test_authenticate_wrong_password(setup_database):
    """Yanlış şifreyle doğrulama yapmayı test eder."""
    add_user('wrong_pass_user', 'wrong@example.com', 'correct_pass')
    assert authenticate_user('wrong_pass_user', 'incorrect_pass') is False

def test_display_users(setup_database, capsys):
    """Kullanıcı listesinin doğru şekilde görüntülenmesini test eder."""
    add_user('display_user', 'display@example.com', 'pass')
    display_users()
    captured = capsys.readouterr()
    assert 'display_user' in captured.out
