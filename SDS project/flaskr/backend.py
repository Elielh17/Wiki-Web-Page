# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib
from flask import send_file
import io
import sys


class Backend:

    def __init__(self):
        """
        Initializes a Backend object with clients for the content and user buckets."""
        self.content_bucket_name = "wiki_content_bucket"
        self.user_bucket_name = "users_passwords_bucket"
        self.client = storage.Client()
        self.content_bucket = self.client.bucket(self.content_bucket_name)
        self.user_bucket = self.client.bucket(self.user_bucket_name)

    def identify_wiki_page_content(self, page_name):
        """Gets the content of a wiki page from the content bucket 
        with the specified name returns Content of the wiki page as a list of words"""
        specified_page = self.content_bucket.blob(page_name)
        if not specified_page.exists():
            return f"Erorr: The page {page_name} does not exists in the bucket."
        return specified_page.download_as_text().split(
        )  #return a list of all the words.

    def get_wiki_page_old(self, page_name):
        """
        Gets the content of a wiki page from the content bucket with the specified name
        returns Content of the wiki page, or None if the page does not exist.
        """
        specified_page = self.content_bucket.blob(page_name)
        if not specified_page.exists():
            return f"Erorr: The page {page_name} does not exists in the bucket."
        return specified_page.download_as_text()

    def get_wiki_page(self, page_name):
        """Get the text description and link of the place in two separated variables and return it as a Tuple"""
        content = self.identify_wiki_page_content(page_name)
        Description = ''
        link = ''
        LINK_PREFIX_LEN = 5
        track = 0
        for word in content:
            if word[0:LINK_PREFIX_LEN] == "Link:":
                if len(word) > LINK_PREFIX_LEN and track + 1 >= len(content):
                    link = word[LINK_PREFIX_LEN:]
                else:
                    link = content[track + 1]
                break
            Description += ' ' + word
            track += 1

        return ("".join(Description), link)

    def get_wiki_page_image(self, image_name):
        # Get the blob with the image name
        blob = self.content_bucket.blob(image_name + '.jpg')
        if not blob:
            return None
        return blob.public_url

    def get_all_page_names(self):
        """
        returns names of all wiki pages or txt files user upload in the content bucket.
        ignores the txt file that start with finances_ and review_
        """
        all_pages_list = []
        REVIEW_PREFIX_LEN = 7
        FINANCE_PREFIX_LEN = 9
        blobs = self.content_bucket.list_blobs(prefix="")
        REVIEW_PREFIX_LEN = 7
        FINANCE_PREFIX_LEN = 9
        for blob in blobs:
            if blob.name.endswith(
                    ".txt"
            ) and blob.name[0:REVIEW_PREFIX_LEN] != "review_" and blob.name[
                    0:
                    FINANCE_PREFIX_LEN] != "finances_":  #just to show the pages instead of reviews
                curr_page_name = blob.name[:len(blob.name) - 4]
                all_pages_list.append(curr_page_name)
        return all_pages_list

    def upload(self, file_name, content):
        """
        Uploads the given file content to the content bucket with the given filename.
        """
        blob = self.content_bucket.blob(file_name)
        blob.upload_from_file(content)

    def sign_up(self, username, password):
        """
        Adds user data if it does not exist along with a hashed password.
        returns True if the user was added successfully, False if the user already exists.
        """
        site_secret = "brainiacs_password"
        blob = self.user_bucket.blob(username)
        if blob.exists():
            return False

        password_with_salt = f"{username}{site_secret}{password}"
        hashed_password = hashlib.blake2b(
            password_with_salt.encode()).hexdigest()
        curr_user_details = username + ":" + hashed_password
        blob.upload_from_string(curr_user_details)
        return True

    def sign_in(self, username, password):
        """
        Checks if a password, when hashed, matches the password in the user bucket.
        returns True if the password matches, False otherwise.
        """
        blob = self.user_bucket.blob(username)
        if not blob.exists():
            return False

        curr_user_details = blob.download_as_text()
        stored_user_password = curr_user_details.split(":")[1]

        site_secret = "brainiacs_password"
        password_with_salt = f"{username}{site_secret}{password}"
        hashed_password = hashlib.blake2b(
            password_with_salt.encode()).hexdigest()
        if hashed_password == stored_user_password:
            return True
        return False

    def get_image(self, image_name):
        """
        Gets an image from the image bucket.
        returns bytes: Binary data of the image, or None if the image does not exist.
        """
        blob = self.content_bucket.blob(image_name)
        if not blob.exists():
            return f"Error: Image {image_name} does not exists in the bucket."
        image_bytes = blob.download_as_bytes()
        return image_bytes

    """ Below methods for uploading and getting reviews"""

    def upload_reviews(self, page_name, curr_user_review, username):
        """
        Uploads a new review to a review_ file in the content bucket, or creates a new review_ file with given filename for the particular page if it doesn't exist
        """
        unique_review_connector = "&%!*Project#brainacs_sajan_acharya_@techx2023forSDS826%^&^%$%^&^%$%"  #this becomes the connector of the review. so we can seperate reviews based on this.
        review_txt_file = f"review_{page_name}.txt"
        blob = self.content_bucket.blob(review_txt_file)
        if blob.exists():
            review_text = blob.download_as_text()
            old_reviews_list = review_text.split(unique_review_connector)
        else:
            old_reviews_list = []
        fresh_review = f"{username}: {curr_user_review}"
        old_reviews_list.append(fresh_review)
        updated_review_data = unique_review_connector.join(
            old_reviews_list
        )  #adds the fresh review to the old list with the unique connecter string added to the end.
        blob.upload_from_string(updated_review_data)

    def get_reviews(self, page_name):
        """
        Retrives the reviews from a text file in the content bucket for a given wiki page.
        """
        unique_review_connector = "&%!*Project#brainacs_sajan_acharya_@techx2023forSDS826%^&^%$%^&^%$%"  #this becomes the connector of the review. so we can seperate reviews based on this.
        review_txt_file = f"review_{page_name}.txt"
        blob = self.content_bucket.blob(review_txt_file)
        if blob.exists():
            review_data = blob.download_as_text()
            review_data_list = review_data.split(unique_review_connector)
            return review_data_list
        else:
            return []

    #this is cameron's r2 implemented by sajan
    def store_finances_answers(self, page_name, answers, verified):
        """uploads the finance answers to bucket and return Successfully Uploaded if user has been verified else returns 'Please log in'"""
        if not verified:
            return "Please log in"

        unique_finance_answers_connector = "$3&%!*roadmapr3#brainacs_sajan@techx2023forSDS826%^&^%$%^&^%$%"  #this becomes the connector of the finances info. so we can seperate finances answers based on this.
        finance_answers_txt_file = f"finances_{page_name}.txt"
        blob = self.content_bucket.blob(finance_answers_txt_file)
        if blob.exists():
            old_finances_text = blob.download_as_text()
            old_finances_answers_list = old_finances_text.split(
                unique_finance_answers_connector)
        else:
            old_finances_answers_list = []
        new_finance_answer = answers
        old_finances_answers_list.append(new_finance_answer)
        updated_finance_answers = unique_finance_answers_connector.join(
            old_finances_answers_list
        )  #adds the new finances information to the old list with the unique connecter string added to the end.
        blob.upload_from_string(updated_finance_answers)
        return "Successfully Uploaded"
