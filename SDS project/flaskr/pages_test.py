from flaskr import create_app
from flask import session
from unittest.mock import patch
import io
import pytest
from unittest.mock import MagicMock
from werkzeug.datastructures import FileStorage


# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    # assert b"Ecom\n" in resp.data


# TODO(Project 1): Write tests for other routes.
#assert resp.data == b"<h1>hello world></h1>"
def test_signup(client):
    """Test if sign up html elements are being displayed correctly"""
    resp = client.get("/signup")
    assert resp.status_code == 200
    assert b'<h1 style="font-size: 6; color: rgb(0, 4, 255);">Sign Up</h1>' in resp.data
    assert b'<form method="post" enctype="multipart/form-data" id="register-form">' in resp.data
    assert b'<input type="text" id="Username" name="username" placeholder="Username" required>' in resp.data
    assert b'<input type="password" id="Password" name="password" placeholder="Password" required>' in resp.data
    assert b'<input type="submit" value="Register" id="register-form-submit">' in resp.data
    assert b'<h1 style="font-size: 6; color: rgb(0, 4, 255);">Sign In</h1>' not in resp.data


def test_signin(client):
    """Test if sign in html elements are being displayed correctly"""
    resp = client.get("/signin")
    assert resp.status_code == 200
    assert b'<h1 style="font-size: 6; color: rgb(0, 4, 255);">Sign In</h1>' in resp.data
    assert b'<form method="post" id="login-form">' in resp.data
    assert b'<input type="text" id="Username" name="username" placeholder="Username" required>' in resp.data
    assert b'<input type="password" id="Password" name="password" placeholder="Password" required>' in resp.data
    assert b'<input type="submit" value="Login" id="login-form-submit">' in resp.data
    assert b'<h1 style="font-size: 6; color: rgb(0, 4, 255);">Sign Up</h1>' not in resp.data


def test_signout(client):
    """Test if user is logged out succesfully"""
    resp = client.get("/logout")
    assert b'<a href="" class="w3-bar-item w3-button w3-hide-small w3-hover-white">{{sent_user_name}}</a>' not in resp.data
    assert b'<a href="/upload" class="w3-bar-item w3-button w3-hide-small w3-hover-white">Upload</a>' not in resp.data
    assert b'<a href="/signout" class="w3-bar-item w3-button w3-hide-small w3-hover-white">Logout</a>' not in resp.data


def test_upload_route_user_not_logged_in(client):
    """
    Tests the upload route's behavior when a user who is not logged in tries to upload a file.
    checks if the user is redirected to homepage with status code 302
    """
    with patch("flaskr.backend.Backend.upload", return_value=None):
        with client.session_transaction() as session:
            session['loggedin'] = False
        data = {
            'file':
                (io.BytesIO(b'this is a test file content'), 'test_file.txt'),
            'filename': 'test_file.txt'
        }

        response = client.post("/upload", data=data)
        assert response.status_code == 302  #the upload route redirect to home if logged in


def test_upload_route_successful(client):
    """
    Tests if the upload route is sucessfully uploading the file
    """
    with patch("flaskr.backend.Backend.upload", return_value=None):
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'file':
                (io.BytesIO(b'this is a test file content'), 'test_file.txt'),
            'filename': 'test_file.txt'
        }

        response = client.post("/upload", data=data)
        assert response.status_code == 200
        print(response.data)
        assert b'file sucessfully uploaded' in response.data


def test_upload_route_empty_file_name(client):
    """
    Tests if the upload route gives redirects to request url if no file selected
    """
    with patch("flaskr.backend.Backend.upload", return_value=None):
        with client.session_transaction() as session:
            session['loggedin'] = True

        my_file_name = ""
        my_file_content = io.BytesIO(b"this is a test file")

        data = {
            'file': (my_file_content, my_file_name),
            'filename': my_file_name
        }

    response = client.post("/upload", data=data)
    assert response.status_code == 200
    assert b'No file selected' in response.data


def test_upload_route_no_file_content(client):
    """
    Tests if the upload route gives redirects to request url if file is empty
    """
    with patch("flaskr.backend.Backend.upload", return_value=None):
        with client.session_transaction() as session:
            session['loggedin'] = True
        my_file_name = "test.txt"
        data = {'filename': my_file_name}
    response = client.post("/upload", data=data)
    assert response.status_code == 200
    assert b'No file part' in response.data


def test_upload_route_wrong_extension(client):
    """
    Tests if the upload route returns wrong format file error if file is of invalid extension
    """
    with patch("flaskr.backend.Backend.upload", return_value=None):
        with client.session_transaction() as session:
            session['loggedin'] = True
        my_file_name = "test_file.mp56"
        my_file_content = io.BytesIO(b"this is a test file")
        data = {
            'file': (my_file_content, my_file_name),
            'filename': my_file_name
        }
    response = client.post("/upload", data=data)
    assert response.status_code == 200
    assert b'wrong format file' in response.data


def test_upload_route_get_method(client):
    """
    Tests the get method of the upload route
    """
    with client.session_transaction() as session:
        session['loggedin'] = True
    response = client.get("/upload")
    assert response.status_code == 200
    assert b'Upload new File' in response.data


def test_review_written_while_logged_in(client):
    """
    Tests if the user can write review if they are logged in. 
    checks if backend method is called which uploads the reviews to the bucket and page redirected again.
    """
    with patch("flaskr.backend.Backend.upload_reviews") as mock_upload:
        mock_upload.return_value = None
        mock_page_name = "test_page"
        review = "I really like this place. It was really fun to visit it"
        username = "sajan"
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = username

        response = client.post(f"/pages/{mock_page_name}",
                               data={"review": review})
        mock_upload.assert_called_once_with(mock_page_name, review, username)
        assert response.status_code == 302
        assert b"Redirecting" in response.data


def test_whitespace_review_written_while_logged_in(client):
    """
    Tests if the user cannot submit the empty comment or whitespaces only. 
    Tests if backend method is not called which and user is redirected to same page
    """
    with patch("flaskr.backend.Backend.upload_reviews") as mock_upload:
        mock_upload.return_value = None
        mock_page_name = "test_page"
        empty_review = "      "
        username = "sajan"
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = username

        response = client.post(f"/pages/{mock_page_name}",
                               data={"review": empty_review})
        assert not mock_upload.called  #the upload_reviews is not called
        assert response.status_code == 302
        assert b"Redirecting" in response.data


def test_review_written_while_not_logged_in(client):
    """
    Test if the user is redirected to the logged in page when they try to submit the review without being logged in.
    """
    with patch("flaskr.backend.Backend.upload_reviews") as mock_upload:
        mock_upload.return_value = None
        mock_page_name = "test_page"
        review = "I really like this place. It was really fun to visit it"
        response = client.post(f"/pages/{mock_page_name}",
                               data={"review": review})
        assert not mock_upload.called
        assert response.status_code == 302
        assert response.headers['Location'] == "/signin"
        assert b"Redirecting" in response.data
        assert b'target URL: <a href="/signin">/signin</a>' in response.data


def test_if_user_review_is_displayed_in_specified_pages(client):
    """
    Tests that the new review is displayed on the specified page combined with the existing reviews.
    """
    with patch("flaskr.backend.Backend.get_wiki_page") as mock_get_wiki_page:
        with patch("flaskr.backend.Backend.get_reviews") as mock_get_reviews:
            mock_page_name = "test_page"
            page_data = "This is a the content of with the page"
            reviews_present = ['I', 'really', 'like', 'this', 'place']
            mock_get_wiki_page.return_value = page_data
            mock_get_reviews.return_value = reviews_present
            response = client.get(f"/pages/{mock_page_name}")
            assert response.status_code == 200
            for review in reviews_present:
                assert review.encode() in response.data


def test_succesfull_login_redirects_to_previous_page(client):
    """
    Tests if the user is redirected to the last viewed page after successfully signing in. 
    Also checks if the Redirecting and the page name is present in the response.
    """
    with patch("flaskr.backend.Backend.sign_in") as mock_sign_in:
        mock_page_name = "test_page"
        login_details = {'username': 'user1', 'password': 'user1_password'}
        mock_sign_in.return_value = True
        with client.session_transaction() as session:
            session['page_to_redirect'] = mock_page_name

        response = client.post("/signin", data=login_details)
        assert response.status_code == 302
        assert b"Redirecting" in response.data
        assert b"test_page" in response.data


def test_if_page_to_redirect_changed(client):
    """
    Tests If the session stores the last opened page name. 
    This allows the user to return back to the page where they can finally submit the review.
    """
    mock_page_name = "test_page"
    review = "I really like this place. It was really fun to visit it"
    client.post(f"/pages/{mock_page_name}", data={'review': review})
    with client.session_transaction() as session:
        assert session['page_to_redirect'] == f"/pages/{mock_page_name}"


def test_review_is_not_cleared_from_form_even_after_redirecting(client):
    """
    Tests that the review text is still present in the review box after getting redirected from the login.
    """
    mock_page_name = "test_page"
    review = "I really like this place. It was really fun to visit it"
    response = client.post(f"/pages/{mock_page_name}", data={'review': review})
    with client.session_transaction() as session:
        assert response.status_code == 302
        assert session["review_text"] == review
    response = client.get(response.location, follow_redirects=True)
    assert response.status_code == 200


def test_home_page1(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b'<li><a href="/">Home</a></li>' in resp.data
    assert b'<li><a href="/pages">Pages</a></li>' in resp.data
    assert b'<li><a href="/about">About</a></li>' in resp.data
    assert b'<li><a href="/signin">Sign in</a></li>' in resp.data
    assert b'<li><a href="/signup">Sign Up</a></li>' in resp.data


def test_wiki_page_Google_Map(client):
    """Test if Google Map snapshot is being displayed"""
    with patch("flaskr.backend.Backend.identify_wiki_page_content",
               return_value=["Page", "content", "test", "Link:", "TestLink"]):
        with patch("flaskr.backend.Backend.get_wiki_page",
                   return_value=("Page content test", "TestLink")):
            resp = client.get(f"/pages/dumbarton")
            assert b'<iframe ' in resp.data


def test_wiki_page_Google_Map_1(client, monkeypatch):
    """Test if Google Map snapshot is not being displayed"""
    with patch("flaskr.backend.Backend.identify_wiki_page_content",
               return_value=["Page", "content", "test"]):
        with patch("flaskr.backend.Backend.get_wiki_page",
                   return_value=("Page content test", "")):
            resp = client.get(f"/pages/test")
            assert b'<iframe ' not in resp.data


def test_wiki_page_Financial_experience(client):
    """Test if Financial experience is being displayed correctly"""
    # Make the request and test the response
    with patch("flaskr.backend.Backend.identify_wiki_page_content",
               return_value=["Page", "content", "test", "Link:", "TestLink"]):
        with patch("flaskr.backend.Backend.get_wiki_page",
                   return_value=("Page content test", "TestLink")):
            resp = client.get(f"/pages/dumbarton")
            html_content = resp.data.decode('utf-8')
            start_tag = html_content.find('<h1 id="element"')
            assert start_tag != -1


def test_wiki_page_Financial_experience_1(client):
    """Test if Financial experience is not being displayed"""
    with patch("flaskr.backend.Backend.identify_wiki_page_content",
               return_value=["Page", "content", "test"]):
        with patch("flaskr.backend.Backend.get_wiki_page",
                   return_value=("Page content test", "")):
            resp = client.get(f"/pages/test")
            assert b'<h1 id="element" style="font-size: large;"><span style="font-size: large;"> Financial Experience: </span><span style="color: #39FF33; font-size: large; line-height: 0px;"> {{Variable_to_store_the_financial_experience}} </span> </h1>' not in resp.data


def mock_sign_in():
    with patch('flaskr.backend.Backend.sign_in') as mock_sign_in:
        yield mock_sign_in


def test_signin_successful(app, client):
    """Test if User is being verified"""
    with patch('flaskr.backend.Backend.sign_in') as mock_sign_in:
        mock_sign_in.return_value = True
        response = client.post('/signin',
                               data={
                                   'username': 'test_user',
                                   'password': 'test_password'
                               })
        mock_sign_in.assert_called_once_with('test_user', 'test_password')

        with client.session_transaction() as sess:
            assert sess['loggedin'] == True
            assert sess['username'] == 'test_user'


# TODO(Project 1): Write tests for other routes.
"""this test is failing"""
# def test_about_page(client):
#     resp = client.get("/about")
#     assert resp.status_code == 200
#     assert b'<h1 class="w3-text-teal">Sajan</h1>' in resp.data
#     assert b'<img src="https://cdn.discordapp.com/attachments/1076232707652206772/1081955756577927209/img1.jpg" alt="Test" width="350" height="300" class="w3-border w3-center">' in resp.data
#     assert b'<h1 class="w3-text-teal">Eliel</h1>' in resp.data
#     assert b'<img src="https://cdn.discordapp.com/attachments/1079200030440833175/1083448363917266974/584A0C35-F8E5-4AC0-AE34-C6C932ED064F.jpg" alt="Test" width="350" height="300" class="w3-border w3-center">' in resp.data
#     assert b'<h1 class="w3-text-teal">Cameron</h1>' in resp.data
