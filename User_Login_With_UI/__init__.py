from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt

client = pymongo.MongoClient("mongodb://localhost:27017")

app = Flask(__name__, template_folder='template')
app.secret_key = 'secrestkey'

db = client.get_database('AICompany')
mycol = db["Programmers"]


@app.route('/', methods=['post', 'get'])
def index():
    message = ''

    if 'email' in session:
        return redirect(url_for('loggedin'))

    if request.method == 'POST':
        user = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = mycol.find_one({"name": user})
        email_found = mycol.find_one({"email": email})

        if user_found:
            message = "There already is a user by that name"
            return render_template('signup.html', message=message)
        if email_found:
            message = 'This email is already registered with another user'
            return render_template('signup.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('signup.html', message=message)
        else:
            pwdhash = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': pwdhash}
            mycol.insert_one(user_input)

            user_data = mycol.find_one({"email": email})
            # user_name = mycol.find_one({"name": user})
            new_email = user_data['email']
            # new_user = user_name['name']

            return render_template('loggedin.html', email=new_email)
    return render_template('signup.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = "Please login to your account"

    if 'email' in session:
        return redirect(url_for("loggedin"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = mycol.find_one({"email": email})

        if email_found:
            email_val = email_found['email']
            password_verify = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), password_verify):
                session['email'] = email_val
                return redirect(url_for('loggedin'))
            else:
                if 'email' in session:
                    return redirect(url_for('loggedin'))
                message = 'Wrong Password'
                return render_template('login.html', message=message)
        else:
            message = "Email not Found"
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/loggedin')
def loggedin():
    if "email" in session:
        email = session["email"]
        return render_template('loggedin.html', email=email)
    else:
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True)
