from flaskr.backend import Backend
from unittest.mock import MagicMock
import hashlib
import pytest
# TODO(Project 1): Write tests for Backend methods.


@pytest.fixture
def backend():
    """
    Creates a backend instance and mocks the content and user bucket
    """
    backend = Backend()
    backend.content_bucket = MagicMock()
    backend.user_bucket = MagicMock()
    return backend


def test_get_wiki_page_old_if_page_found(backend):
    """
    Checks if the get_wiki_page method returns correct text for an existing specified txt file
    """

    mock_page_name = "testing_page.txt"
    mock_page_content = "this is a test content"

    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    backend.content_bucket.blob.return_value = mock_blob

    curr_page_blob = backend.content_bucket.blob(mock_page_name)
    curr_page_blob.upload_from_string(mock_page_content)

    recieved_text = backend.get_wiki_page_old(mock_page_name)
    assert recieved_text == curr_page_blob.download_as_text()


def test_get_wiki_page(backend):
    """Check if the function get the text and the link in two separated variables in a tuple"""
    # Set up mock objects
    backend.content_bucket = MagicMock()
    mock_blob = MagicMock()
    backend.content_bucket.blob.return_value = mock_blob

    # Set up mock blob to return test content
    mock_page_name = "test_page.txt"
    mock_page_content = "Test content Link: Testlink.com"
    mock_blob.download_as_text.return_value = mock_page_content

    assert backend.get_wiki_page(mock_page_name) == (" Test content",
                                                     "Testlink.com")


def test_get_wiki_page_old_if_page_not_found(backend):
    """
    Checks if the get_wiki_page method returns error for a specific txt file not present in the bucket
    """

    unavilable_page = "page_not_found.txt"
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    backend.content_bucket.blob.return_value = mock_blob
    expected_error = f"Erorr: The page {unavilable_page} does not exists in the bucket."
    recieved_error = backend.get_wiki_page_old(unavilable_page)
    assert expected_error == recieved_error


def test_get_all_page_names(backend):
    """
    checks if the get_all_page_names method returns the list of the names in the content bucket
    """
    blob1 = MagicMock()
    blob1.name = "test_page1.txt"

    blob2 = MagicMock()
    blob2.name = "test_page2.txt"
    backend.content_bucket.list_blobs.return_value = [blob1, blob2]

    expected_page_list = ['test_page1', 'test_page2']
    recieved_list = backend.get_all_page_names()
    assert recieved_list == expected_page_list


def test_get_all_page_names_excluding_invalid_page_extension(backend):
    """
    checks if get_all_page_names ignores other file that does not end with .txt
    """
    blob1 = MagicMock()
    blob1.name = "test_page1.txt"

    blob2 = MagicMock()
    blob2.name = "test_page2.txt"

    blob3 = MagicMock()
    blob3.name = "test_page3.html"

    blob4 = MagicMock()
    blob4.name = "test_page_img.jpeg"

    blob5 = MagicMock()
    blob5.name = "test_page5.txt"

    backend.content_bucket.list_blobs.return_value = [
        blob1, blob2, blob3, blob4, blob5
    ]

    expected_page_list = ['test_page1', 'test_page2', 'test_page5']
    recieved_list = backend.get_all_page_names()
    assert recieved_list == expected_page_list


def test_get_all_page_names_if_no_pages_found(backend):
    """
    checks if the get_all_page_names method returns empty list if no pages with extension .txt are found in the content bucket
    """
    blob1 = MagicMock()
    blob1.name = "test_page1"

    blob2 = MagicMock()
    blob2.name = "test_page2"
    backend.content_bucket.list_blobs.return_value = [blob1, blob2]
    expected_page_list = []
    recieved_list = backend.get_all_page_names()
    assert recieved_list == expected_page_list


def test_upload_html_files(backend):
    """
    tests if the upload method works for the .html files
    """
    mock_file_name = "mock_file.html"
    curr_mock_file_content = "<html><head></head><body><This is testing content page</h1></body></html>"
    curr_mock_blob = MagicMock()
    backend.content_bucket.blob.return_value = curr_mock_blob
    backend.upload(mock_file_name, curr_mock_file_content)
    curr_mock_blob = backend.content_bucket.blob(mock_file_name)
    curr_mock_blob.download_as_text.return_value = curr_mock_file_content

    curr_mock_blob.upload_from_file.assert_called_once_with(
        curr_mock_file_content)
    recieved_mock_content = curr_mock_blob.download_as_text()
    assert recieved_mock_content == curr_mock_file_content


def test_upload_txt_file(backend):
    """
    tests if the upload method works for the .txt files
    """
    mock_file_name = "mock_text_file.txt"
    curr_mock_file_content = "This is testing file for a txt file"
    curr_mock_blob = MagicMock()
    backend.content_bucket.blob.return_value = curr_mock_blob
    backend.upload(mock_file_name, curr_mock_file_content)
    curr_mock_blob = backend.content_bucket.blob(mock_file_name)
    curr_mock_blob.download_as_text.return_value = curr_mock_file_content

    curr_mock_blob.upload_from_file.assert_called_once_with(
        curr_mock_file_content)
    recieved_mock_content = curr_mock_blob.download_as_text()
    assert recieved_mock_content == curr_mock_file_content


def test_upload_img_files(backend):
    """
    tests if the upload method works for the image files
    """
    curr_mock_file_name = "mock_img_file.jpeg"
    curr_mock_file_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
    curr_mock_blob = MagicMock()
    backend.content_bucket.blob.return_value = curr_mock_blob
    backend.upload(curr_mock_file_name, curr_mock_file_content)
    curr_mock_blob = backend.content_bucket.blob(curr_mock_file_name)
    curr_mock_blob.download_as_bytes.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'

    curr_mock_blob.upload_from_file.assert_called_once_with(
        curr_mock_file_content)
    recieved_mock_bytes = curr_mock_blob.download_as_bytes()
    expected_mock_bytes = curr_mock_file_content
    assert recieved_mock_bytes == expected_mock_bytes


def test_signup_new_user(backend):
    """
    checks if the user is successfully registered
    """
    username = "sajan"
    password = "testing_password_sajan"
    curr_mock_blob = MagicMock()
    curr_mock_blob.exists.return_value = False  #so it wont directly go to user already exists.
    backend.user_bucket.blob.return_value = curr_mock_blob
    recieved_confirmation = backend.sign_up(username, password)
    assert recieved_confirmation == True


def test_signup_user_already_exists(backend):
    """
    checks if the signup returns false if the current user is already registered
    """
    username = "sajan"
    password = "testing_password_sajan"
    curr_mock_blob = MagicMock()
    curr_mock_blob.exists.return_value = True
    backend.user_bucket.blob.return_value = curr_mock_blob
    recieved_confirmation = backend.sign_up(username, password)
    assert recieved_confirmation == False


def test_sign_in_user_succesfully_signs_in(backend):
    """
    checks if the user with the correct password can sucessfully sign in
    """
    username = "sajan"
    password = "testing_password_sajan"

    site_secret = "brainiacs_password"
    password_with_salt = f"{username}{site_secret}{password}"
    hashed_password = hashlib.blake2b(password_with_salt.encode()).hexdigest()

    curr_user_details = username + ":" + hashed_password

    curr_mock_blob = MagicMock()
    curr_mock_blob.download_as_text.return_value = curr_user_details  #downloaod as text will return value like line 77 "sajan:testing_password_sajan"

    backend.user_bucket.blob.return_value = curr_mock_blob

    recieved_confirmation = backend.sign_in(username, password)
    assert recieved_confirmation == True


def test_sign_in_user_inputs_wrong_password(backend):
    """
    checks if the user with the wrong password cannot signin
    """
    username = "sajan"
    curr_wrong_password = "testing_wrong_password_sajan"
    stored_original_password = "corrent_testing_sajan"
    site_secret = "brainiacs_password"

    password_with_salt = f"{username}{site_secret}{stored_original_password}"
    hashed_password = hashlib.blake2b(password_with_salt.encode()).hexdigest()
    curr_user_details = username + ":" + hashed_password

    curr_mock_blob = MagicMock()
    curr_mock_blob.download_as_text.return_value = curr_user_details  #downloaod as text will return value like line 77 "sajan:testing_password_sajan"
    backend.user_bucket.blob.return_value = curr_mock_blob
    recieved_confirmation = backend.sign_in(username, curr_wrong_password)
    assert recieved_confirmation == False


def test_sign_in_user_not_found(backend):
    """
    checks if the user is not present in the user bucket and returns false
    """
    username = "midnight_user"
    password = "testing_password_sajan"
    curr_mock_blob = MagicMock()
    curr_mock_blob.exists.return_value = False  #means user not present
    backend.user_bucket.blob.return_value = curr_mock_blob
    recieved_confirmation = backend.sign_in(username, password)
    assert recieved_confirmation == False


def test_get_image_returns_bytes(backend):
    """
    checks if the get_image method returns the bytes of an image
    """
    image_name = "image1.jpeg"
    curr_mock_blob = MagicMock()
    curr_mock_blob.exists.return_value = True

    image_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
    curr_mock_blob.download_as_bytes.return_value = image_bytes
    backend.content_bucket.blob.return_value = curr_mock_blob

    received_image_bytes = backend.get_image(image_name)
    backend.content_bucket.blob.assert_called_once_with(image_name)
    assert isinstance(received_image_bytes, bytes)


def test_get_image_returns_correct_image_bytes(backend):
    """
    checks if the get_image method returns the bytes of an image
    """
    image_name = "image1.jpeg"
    curr_mock_blob = MagicMock()
    curr_mock_blob.exists.return_value = True

    image_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
    curr_mock_blob.download_as_bytes.return_value = image_bytes
    backend.content_bucket.blob.return_value = curr_mock_blob
    received_image_bytes = backend.get_image(image_name)
    backend.content_bucket.blob.assert_called_once_with(image_name)
    expected_image_bytes = image_bytes
    assert received_image_bytes == expected_image_bytes


def test_get_image_if_image_not_found(backend):
    """
    checks if the get_image method returns error if the image is not found in the bucket
    """
    image_name = "unavilable_img.jpeg"
    curr_mock_blob = MagicMock()
    curr_mock_blob.exists.return_value = False
    backend.content_bucket.blob.return_value = curr_mock_blob

    received_image_error = backend.get_image(image_name)
    backend.content_bucket.blob.assert_called_once_with(image_name)
    expected_image_error = f"Error: Image {image_name} does not exists in the bucket."
    assert received_image_error == expected_image_error


#for review sections tests
def test_upload_reviews_if_old_reviews_present(backend):
    """
    Tests that the upload_reviews method uploads the fresh review to the paage's reviews file along with other existing reviews
    """
    mock_page_name = "test_page"
    mock_username = "sajan"
    new_mock_review = "I really like this place. It was really fun to visit it."
    unique_review_connector = "&%!*Project#brainacs_sajan_acharya_@techx2023forSDS826%^&^%$%^&^%$%"
    old_mock_reviews = f'first_review{unique_review_connector}second_review{unique_review_connector}third_review{unique_review_connector}fourth_review'
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    mock_blob.download_as_text.return_value = old_mock_reviews
    backend.content_bucket.blob.return_value = mock_blob

    backend.upload_reviews(mock_page_name, new_mock_review, mock_username)
    expected_reviews = [
        "first_review", "second_review", "third_review", "fourth_review",
        f'{mock_username}: {new_mock_review}'
    ]
    review_stored_file = f"review_{mock_page_name}.txt"
    connector_added_review = unique_review_connector.join(expected_reviews)
    mock_blob.upload_from_string.assert_called_once_with(connector_added_review)
    backend.content_bucket.blob.assert_called_once_with(review_stored_file)
    current_uploaded_string = mock_blob.upload_from_string.call_args[0][
        0]  # call args is a tuple of tuple
    returned_reviews = current_uploaded_string.split(unique_review_connector)
    assert expected_reviews == returned_reviews


def test_upload_reviews_if_old_reviews_not_present(backend):
    """
    Tests that the upload_reviews method creates a new file to uploads the fresh review to the paage if previous reviews does not exist.
    """
    mock_page_name = "test_page"
    mock_username = "test_user"
    new_mock_review = "I really like this place. It was really fun to visit it"

    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    backend.content_bucket.blob.return_value = mock_blob
    backend.upload_reviews(mock_page_name, new_mock_review, mock_username)

    review_stored_file = f"review_{mock_page_name}.txt"
    expected_reviews = f"{mock_username}: {new_mock_review}"
    mock_blob.upload_from_string.assert_called_once_with(expected_reviews)
    backend.content_bucket.blob.assert_called_once_with(review_stored_file)

    current_uploaded_string = mock_blob.upload_from_string.call_args[0][
        0]  # call args is a tuple of tuple
    returned_reviews = current_uploaded_string  #should not split as just one review do not have the connector
    assert expected_reviews == returned_reviews


def test_get_reviews_if_no_old_reviews(backend):
    """
    Tests that the get_reviews method returns the empty list when there are no reviews in for the specified page in the content bucket
    """
    mock_page_name = "test_page"
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    backend.content_bucket.blob.return_value = mock_blob
    expected_result = []
    recieved_review_from_buckets = backend.get_reviews(mock_page_name)
    assert recieved_review_from_buckets == expected_result


def test_get_reviews_if_old_reviews_present(backend):
    """
    Tests that the get_reviews method returns the list of exisiting reviews for the specified page in the content bucket
    """
    mock_page_name = "test_page"
    unique_review_connector = "&%!*Project#brainacs_sajan_acharya_@techx2023forSDS826%^&^%$%^&^%$%"
    mock_reviews = f'first_review{unique_review_connector}second_review{unique_review_connector}third_review{unique_review_connector}fourth_review'
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    mock_blob.download_as_text.return_value = mock_reviews
    backend.content_bucket.blob.return_value = mock_blob
    expected_reviews = [
        "first_review", "second_review", "third_review", "fourth_review"
    ]
    recieved_review_from_buckets = backend.get_reviews(mock_page_name)
    assert recieved_review_from_buckets == expected_reviews


#test for cameron's r2 feature.
def test_store_finances_answers_if_user_verified(backend):
    """tests if the store finances method returns 'Successfully Uploaded' if the user has been verified"""
    mock_page_name = "test_page"
    mock_answer = "flight:200, housing: 300"
    mock_verified = True
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    backend.content_bucket.blob.return_value = mock_blob
    result = backend.store_finances_answers(mock_page_name, mock_answer,
                                            mock_verified)
    assert result == "Successfully Uploaded"


def test_store_finances_answers_if_user_not_verified(backend):
    """tests if the store finances method returns 'Please log in' if the user has been verified"""
    mock_page_name = "test_page"
    mock_answer = "flight:200, housing: 300"
    mock_verified = False
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    backend.content_bucket.blob.return_value = mock_blob
    result = backend.store_finances_answers(mock_page_name, mock_answer,
                                            mock_verified)
    assert result == "Please log in"


def test_store_finances_answers_if_old_answers_not_present(backend):
    """tests if the store finances method uploads the answers to new file finances_page_name if old answers are not present in the bucket"""
    mock_page_name = "test_page"
    mock_answer = "flight:200, housing: 300"
    mock_verified = True
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    backend.content_bucket.blob.return_value = mock_blob
    backend.store_finances_answers(mock_page_name, mock_answer, mock_verified)

    old_finances_stored_file = f"finances_{mock_page_name}.txt"
    expected_answers = mock_answer
    mock_blob.upload_from_string.assert_called_once_with(expected_answers)
    backend.content_bucket.blob.assert_called_once_with(
        old_finances_stored_file)
    curr_stored_reviews = mock_blob.upload_from_string.call_args[0][
        0]  # call args is a tuple of tuple
    returned_answers = curr_stored_reviews
    assert expected_answers == returned_answers


def test_store_finances_answers_if_old_answers_present(backend):
    """tests if the store finances method uploads the current answers to old file by combining the old answers with the current answer to the finances_pagename file"""
    mock_page_name = "test_page"
    mock_answer = "flight:200, housing: 300"
    mock_verified = True
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True

    unique_finance_answers_connector = "$3&%!*roadmapr3#brainacs_sajan@techx2023forSDS826%^&^%$%^&^%$%"
    old_mock_reviews = f'answer1{unique_finance_answers_connector}answer2{unique_finance_answers_connector}answer3{unique_finance_answers_connector}answer4'

    mock_blob.download_as_text.return_value = old_mock_reviews
    backend.content_bucket.blob.return_value = mock_blob

    backend.store_finances_answers(mock_page_name, mock_answer, mock_verified)
    expected_answers = ["answer1", "answer2", "answer3", "answer4", mock_answer]

    old_finances_stored_file = f"finances_{mock_page_name}.txt"
    connector_added_answer = unique_finance_answers_connector.join(
        expected_answers)
    mock_blob.upload_from_string.assert_called_once_with(connector_added_answer)
    backend.content_bucket.blob.assert_called_once_with(
        old_finances_stored_file)
    current_uploaded_string = mock_blob.upload_from_string.call_args[0][
        0]  # call args is a tuple of tuple
    returned_answers = current_uploaded_string.split(
        unique_finance_answers_connector)
    assert expected_answers == returned_answers


#testing the identify wiki page content method
def test_identify_wiki_page_content_if_page_found(backend):
    """Checks if the identify_wiki_page_content method returns correct list of words for an existing specified txt file"""

    mock_page_name = "testing_page.txt"
    mock_page_content = "this is a test file"

    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    backend.content_bucket.blob.return_value = mock_blob

    curr_page_blob = backend.content_bucket.blob(mock_page_name)
    curr_page_blob.upload_from_string(mock_page_content)
    recieved_text = backend.identify_wiki_page_content(mock_page_name)
    assert recieved_text == curr_page_blob.download_as_text().split()


def test_identify_wiki_page_content_not_found(backend):
    """Checks if the identify_wiki_page_content method returns error for a specific txt file not present in the bucket"""
    unavilable_page = "page_not_found.txt"
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    backend.content_bucket.blob.return_value = mock_blob

    expected_error = f"Erorr: The page {unavilable_page} does not exists in the bucket."
    recieved_error = backend.identify_wiki_page_content(unavilable_page)
    assert expected_error == recieved_error
