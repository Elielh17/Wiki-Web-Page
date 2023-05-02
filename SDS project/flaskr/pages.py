from flask import Flask, flash, request, redirect, url_for, render_template, session
from flaskr.backend import Backend
from flask import session


def make_endpoints(app):

    my_backend = Backend()
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        greetings = "Welcome To Brainiacs"
        return render_template("main.html", greetings=greetings)

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        """
        This route handles GET and POST requests for uploading files to a content bucket.
        It checks if the user is logged in using session variables, 
        checks that the uploaded file has a valid extension, and uploads the file to the content bucket if it is valid. 
        If the file is uploaded successfully, it renders a success message. If not, it renders an error message
        """
        if not session.get('loggedin', False):
            return redirect(url_for('home'))

        ALLOWED_EXTENSIONS = {
            'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'html', 'htm'
        }

        def allowed_file(filename):
            return '.' in filename and filename.rsplit(
                '.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return render_template('upload.html', message="No file part")

            file = request.files['file']
            if file.filename == '':
                flash('No file selected')
                return render_template('upload.html',
                                       message="No file selected")

            if file and allowed_file(file.filename):
                my_backend.upload(f'{file.filename}', file)
                # flash("file sucessfully uploaded")
                return render_template('upload.html',
                                       message="file sucessfully uploaded")
            else:
                return render_template('upload.html',
                                       message="wrong format file")
        return render_template("upload.html")

    @app.route('/signin', methods=['GET', 'POST'])
    def signin():
        """Gets the user input and checks with the backend if the username with password matches"""
        if session.get('loggedin', False):
            return redirect(url_for('home'))
        message = None
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']

            if my_backend.sign_in(username,
                                  password):  # True if sign up is successful
                session['loggedin'] = True
                session['username'] = username

                if "page_to_redirect" in session:
                    redirect_page = session.pop("page_to_redirect")
                    return redirect(redirect_page)
                return render_template("main.html",
                                       sent_user_name=username,
                                       signed_in=True)
            else:
                message = "Incorrect username or password"
        return render_template("signin.html", message=message)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if session.get('loggedin', False):
            return redirect(url_for('home'))

        message = None
        if request.method == 'POST':
            print("function calleeddd")
            username = request.form['username']
            password = request.form['password']
            if my_backend.sign_up(username, password):
                session['loggedin'] = True
                session['username'] = username
                # return render_template("login_succesfull.html")
                return render_template("main.html",
                                       sent_user_name=username,
                                       signed_in=True)
            else:
                message = "Username already present"
        return render_template("signup.html", message=message)

    @app.route('/about')
    def about():
        # first_image_bytes = my.get_image("cameron.jpeg")
        # with Image.open(io.BytesIO(first_image_bytes)) as img:
        #     img.save("downloaded_img_file.jpeg")
        # saves the image file into the current directory.
        return render_template("about.html")

    @app.route('/pages/<page_name>', methods=["GET", "POST"])
    def page(page_name):
        """
        This route handles GET and POST requests for wiki pages.
        it retrieves wiki page content and stored reviews from a backend, 
        and uploads reviews to the backend with the file name if the user is logged in. 
        It also handles session variables and redirects to the last visited page if succesfully logged in
        """
        #adding sessions to prevent from logging out without logout
        if request.method == "POST":
            if "loggedin" not in session:
                if request.form.get(
                        "review") and not request.form.get("review").isspace():
                    session["page_to_redirect"] = url_for('page',
                                                          page_name=page_name)
                    session["review_text"] = request.form.get("review")
                return redirect("/signin")
            else:
                review_data = request.form.get("review")
                username = session.get("username")
                if review_data and not review_data.isspace():
                    my_backend.upload_reviews(page_name, review_data, username)
                else:
                    flash(f'ERROR: Empty review.')
                    return redirect(url_for('page', page_name=page_name))
                return redirect(url_for('page', page_name=page_name))
        else:
            final_page_name = page_name + ".txt"
            image = my_backend.get_wiki_page_image(page_name)
            curr_page_content = my_backend.get_wiki_page(final_page_name)
            stored_reviews = my_backend.get_reviews(page_name)
            if "review_text" in session:
                old_review_text = session.pop("review_text")
            else:
                old_review_text = ""
            return render_template(
                "wiki_page.html",
                page_name=page_name,
                image_url = image,
                reviews=stored_reviews,
                review_text=old_review_text,
                page_content=curr_page_content[0],
                page_link=curr_page_content[1],
                Variable_to_store_the_financial_experience='$1200')
        #changed parameters to get page content from tuple

    @app.route('/pages', methods=['GET', 'POST'])
    def pages():
        """
        gets the page names from bucket and passes it to
        """
        all_page_names = my_backend.get_all_page_names()
        return render_template("pages.html", all_page_names=all_page_names)

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        """
        This route handles the logout of the user.
        If the user is not logged in, it redirects to the home page. 
        If the user is logged in, it removes the 'loggedin' and 'username' keys from the session
        and then redirects to the home page.
        """
        if not session.get('loggedin', False):
            return redirect(url_for('home'))

        session.pop('loggedin', None)
        session.pop('username', None)
        return redirect(url_for("home"))

    @app.route("/finances", methods=['GET', 'POST'])
    def finances():
        if request.method == 'POST':
            page_name = request.form['page_name']
            answers = request.form['answers']
            # with open("text_file.txt", "w") as file:
            #     file.write(f'{username}, {password} this is the returned register details')
            if my_backend.store_finances_answers(page_name, answers, True):
                return render_template("finances.html")
        return render_template("finances.html")

    # @app.route("/loginsuccesful", methods=['GET', 'POST'])
    # def submit_login():
    #     #if Backend determines it can login <--------------------------------------------------------------------Important
    #     if request.method == 'POST':
    #         username = request.form['Username']
    #         password = hash = hashlib.blake2b(
    #             request.form['Password'].encode()).hexdigest()
    #     return render_template("Succesful.html", LogorSing='Login')

    # @app.route("/Singsuccesful", methods=['GET', 'POST'])
    # def submit_sing():
    #     #if Backend determines it can login <--------------------------------------------------------------------Important
    #     if request.method == 'POST':
    #         username = request.form['Username']
    #         password = hash = hashlib.blake2b(
    #             request.form['Password'].encode()).hexdigest()
    #     return render_template("Succesful.html", LogorSing='Sing Up')
