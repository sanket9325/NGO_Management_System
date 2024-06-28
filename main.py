from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb
from urllib.parse import urlencode
import json
import os
import math
import random
import string
from datetime import date

app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = os.urandom(24).hex()
app.tran_id = os.urandom(7).hex()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ngomanagementsystem'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'static/upload'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def generate_id(col, table):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT " + col + " FROM " + table + " ORDER BY " + col + " DESC")
    id_data = cursor.fetchone()
    if id_data is None or id_data[col] is None:
        return "1"
    else:
        id = int(id_data[col]) + 1
        return str(id)



@app.route("/")
def index():
    return render_template('index.html')

@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['txtname']
        email = request.form['txtemail']
        mobile = request.form['txtmobile']
        address = request.form['txtaddress']
        dob = request.form['txtdob']
        gender = request.form['gender']
        username = request.form['txtusername']
        password = request.form['txtpassword']
        photo = request.files['fuimage']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM registration WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        if user_data:
            alert_script = """
                <script>
                    function showAlert() {
                        Swal.fire({
                            title: 'Oops...',
                            text: 'Username already exists!',
                            icon: 'error'
                        });
                    }
                    showAlert();
                </script>
                """
            return render_template('registration.html', alert_script=alert_script)
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "INSERT INTO registration(id,name,email,mobile,address,dob,gender,username,password,photo) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (generate_id("id","registration"), name, email, mobile, address, dob, gender, username, password, photo.filename)
            )
            mysql.connection.commit()
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
            photo.save(image_path)
            alert_script = """
                            <script>
                                function showAlert() {
                                    Swal.fire({
                                        title: 'Thank You For Registration!',
                                        text: 'Click ok to Continue',
                                        icon: 'success'
                                    });
                                }
                                showAlert();
                            </script>
                            """
            return render_template('registration.html', alert_script=alert_script)

    return render_template('registration.html')

@app.route("/user_login", methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['txtusername']
        password = request.form['txtpassword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM registration WHERE username = %s AND password = %s", (username, password))
        user_data = cursor.fetchone()

        if user_data is not None and user_data['username'] == username and user_data['password'] == password:
            session['username'] = username
            session['id'] = user_data['id']
            session['user_loggedin'] = True
            return redirect(url_for('user_home'))
        else:
            alert_script = """
                <script>
                    function showAlert() {
                        Swal.fire({
                            title: 'Oops...',
                            text: 'Invalid Username or Password!',
                            icon: 'error'
                        });
                    }
                    showAlert();
                </script>
            """
            return render_template('user_login.html', alert_script=alert_script)
    return render_template('user_login.html')

@app.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['txtusername']
        password = request.form['txtpassword']
        if username == "Admin" and password == "Super":
            return redirect(url_for('admin_home'))
        else:
            alert_script = """
                <script>
                    function showAlert() {
                        Swal.fire({
                            title: 'Oops...',
                            text: 'Invalid Username or Password!',
                            icon: 'error'
                        });
                    }
                    showAlert();
                </script>
            """
            return render_template('admin_login.html', alert_script=alert_script)
    return render_template('admin_login.html')

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['txtname']
        email = request.form['txtemail']
        subject = request.form['txtsubject']
        message = request.form['txtmessage']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO contact(cid,name,email,subject,message) VALUES(%s, %s, %s, %s, %s)",
            (generate_id("cid", "contact"), name, email, subject, message)
        )
        mysql.connection.commit()
        alert_script = """
                                    <script>
                                        function showAlert() {
                                            Swal.fire({
                                                title: 'Thank You For Contact!',
                                                text: 'Click ok to Continue',
                                                icon: 'success'
                                            });
                                        }
                                        showAlert();
                                    </script>
                                    """
        return render_template('contact.html', alert_script=alert_script)
    return render_template('contact.html')

############################################## User Side ###################################

@app.route("/user_home")
def user_home():
    id = session["id"]
    return render_template('user_home.html', id=id)

@app.route("/user_mission")
def user_mission():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM mission ORDER BY mid DESC")
    mission = cur.fetchone()
    return render_template('user_mission.html', mission=mission)

@app.route("/user_vision")
def user_vision():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM vision ORDER BY vid DESC")
    vision = cur.fetchone()
    return render_template('user_vision.html', vision=vision)

@app.route("/user_donatenow", methods=['GET', 'POST'])
def user_donatenow():
    if request.method == 'POST':
        id = session["id"]
        account_no = request.form['txtaccno']
        ifsc_code = request.form['txtifsc']
        branch_name = request.form['txtbranch']
        amount = request.form['txtamount']

        today_date = date.today()
        today_date_str = today_date.strftime("%d-%m-%Y")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO donation(did,id,account_number,ifsc_code,branch_name,amount,date) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            (generate_id("did", "donation"), id,account_no,ifsc_code,branch_name,amount,today_date_str)
        )
        mysql.connection.commit()
        alert_script = """
            <script>
                function showAlert() {
                    Swal.fire({
                        title: 'Your Donation Has Been Successful!',
                        text: 'Now You Can Leave The Page',
                        icon: 'success'
                    });
                }
                showAlert();
            </script>
        """
        return render_template('user_donateNow.html', alert_script=alert_script)
    return render_template('user_donateNow.html')

@app.route("/user_viewdonation")
def user_viewdonation():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM donation WHERE id=%s", str(session["id"]))
    donations = cur.fetchall()
    return render_template('user_viewDonation.html', donations=donations)

@app.route("/user_events")
def user_events():
    return render_template('user_events.html')

@app.route("/user_eventRegPage", methods=['GET', 'POST'])
def user_eventregpage():
    donation_type = request.args.get("donation_type")
    if request.method == 'POST':
        id = session["id"]
        visit_date = request.form['txtvisitdate']
        visit_time = request.form['txtvisittime']
        total_people = request.form['txtpeoplecount']
        don_type_txt = request.form['txtdonationtype']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO event_registration(eid,id,donation_type,visit_date,visit_time,total_people,cur_date) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            (generate_id("eid", "event_registration"), id, don_type_txt, visit_date, visit_time, total_people, date.today())
        )
        mysql.connection.commit()
        alert_script = """
            <script>
                function showAlert() {
                    Swal.fire({
                        title: 'Your Event Registration Successful!',
                        text: 'Now You Can Leave The Page',
                        icon: 'success'
                    });
                }
                showAlert();
            </script>
        """
        return render_template('user_eventRegPage.html', donation_type=donation_type, alert_script=alert_script)
    return render_template('user_eventRegPage.html', donation_type=donation_type)

@app.route("/user_yourEvents")
def user_yourevents():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM event_registration WHERE id=%s", str(session["id"]))
    eventreg = cur.fetchall()
    return render_template('user_yourEvents.html', eventreg=eventreg)

@app.route("/user_news")
def user_news():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM news")
    news = cur.fetchall()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM news ORDER BY nid DESC LIMIT 1")
    latestnews = cur.fetchone()
    return render_template('user_news.html', news=news, latestnews=latestnews)


@app.route("/user_logout")
def user_logout():
    session.pop('user_loggedin', None)
    return redirect('/user_login')

################################################ Admin Side ##################################

@app.route("/admin_home")
def admin_home():
    return render_template('admin_home.html')

@app.route("/admin_mission", methods=['GET', 'POST'])
def admin_mission():
    if request.method == 'POST':
        title = request.form['txttitle']
        description = request.form['txtdescription']
        file = request.files['txtimage']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO mission(mid,title,description,image) VALUES(%s, %s, %s, %s)",
            (generate_id("mid", "mission"), title, description, file.filename)
        )
        mysql.connection.commit()
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        alert_script = """
            <script>
                function showAlert() {
                    Swal.fire({
                        title: 'Mission Added Successfully!',
                        text: 'Click ok to Continue',
                        icon: 'success'
                    });
                }
                showAlert();
            </script>
        """
        return render_template('admin_vision.html', alert_script=alert_script)

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM mission")
    mission = cur.fetchall()
    return render_template('admin_mission.html', mission=mission)

@app.route("/admin_missionDelete")
def admin_missiondelete():
    mid = request.args.get("mid")
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM mission WHERE mid=%s", mid)
    mysql.connection.commit()
    return redirect('/admin_mission')

@app.route("/admin_vision", methods=['GET', 'POST'])
def admin_vision():
    if request.method == 'POST':
        title = request.form['txttitle']
        description = request.form['txtdescription']
        file = request.files['txtimage']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO vision(vid,title,description,image) VALUES(%s, %s, %s, %s)",
            (generate_id("vid", "vision"), title, description, file.filename)
        )
        mysql.connection.commit()
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        alert_script = """
            <script>
                function showAlert() {
                    Swal.fire({
                        title: 'Vision Added Successfully!',
                        text: 'Click ok to Continue',
                        icon: 'success'
                    });
                }
                showAlert();
            </script>
        """
        return render_template('admin_vision.html', alert_script=alert_script)

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM vision")
    vision = cur.fetchall()
    return render_template('admin_vision.html', vision=vision)

@app.route("/admin_visionDelete")
def admin_visiondelete():
    vid = request.args.get("vid")
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM vision WHERE vid=%s", vid)
    mysql.connection.commit()
    return redirect('/admin_vision')


@app.route("/admin_viewDonation")
def admin_viewdonation():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM donation INNER JOIN registration ON donation.id=registration.id")
    donations = cur.fetchall()
    return render_template('admin_viewDonation.html', donations=donations)

@app.route("/admin_viewEventReg")
def admin_vieweventreg():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM event_registration INNER JOIN registration ON event_registration.id=registration.id")
    eventreg = cur.fetchall()
    return render_template('admin_viewEventReg.html', eventreg=eventreg)

@app.route("/admin_addNews", methods=['GET', 'POST'])
def admin_addnews():
    if request.method == 'POST':
        title = request.form['txttitle']
        city = request.form['txtcity']
        description = request.form['txtdescription']
        file = request.files['txtimage']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO news(nid,title,city,description,image,date) VALUES(%s, %s, %s, %s, %s, %s)",
            (generate_id("nid", "news"), title, city, description, file.filename, date.today())
        )
        mysql.connection.commit()
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        alert_script = """
            <script>
                function showAlert() {
                    Swal.fire({
                        title: 'News Added Successfully!',
                        text: 'Click ok to Continue',
                        icon: 'success'
                    });
                }
                showAlert();
            </script>
        """
        return render_template('admin_addNews.html', alert_script=alert_script)
    return render_template('admin_addNews.html')

@app.route("/admin_viewNews")
def admin_viewnews():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM news")
    news = cur.fetchall()
    return render_template('admin_viewNews.html', news=news)

@app.route("/admin_newsDelete")
def admin_newsdelete():
    nid = request.args.get("nid")
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM news WHERE nid=%s", nid)
    mysql.connection.commit()
    return redirect('/admin_viewNews')

@app.route("/admin_contactView")
def admin_contactView():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM contact")
    contacts = cur.fetchall()
    return render_template('admin_contactView.html', contacts=contacts)

@app.route("/admin_userList")
def admin_userList():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM registration ORDER BY id DESC")
    userlist = cur.fetchall()
    return render_template('admin_userList.html', userlist=userlist)

###############################################################################################


if __name__ == '__main__':
    app.run(debug=True)