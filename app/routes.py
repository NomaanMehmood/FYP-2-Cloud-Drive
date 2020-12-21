import math
import os
import pathlib
import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from imp import reload

import boto3
import requests
from flask import render_template, url_for, flash, redirect, request, abort, send_file
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from app.models import User, Post, Package
from app.forms import RegistrationForm, LoginForm, PostForm, AdminLoginForm, PackageForm, UpdateMyProfiletForm
from app import app, db, bcrypt
from app.s3Functions import list_files, download_file, upload_file, create_presigned_url
from app.bucketConfig import create_bucket, deletefile



@app.route('/createAdmin', methods=['GET', 'POST'])
def createAdmin():
    if request.method == 'POST':
        new_user = User(email=request.form['email'], password=request.form['password'], is_admin=True)
        db.session.add(new_user)
        db.session.commit()
        return "you have Created Admin Account"

    return render_template('admin/signupAdmin.html')


@app.route('/newReg', methods=['GET', 'POST'])
def newRegister():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        bucket = create_bucket(form.username.data, s3_connection=boto3.resource("s3",
                                                                                endpoint_url='https://s3.wasabisys.com',
                                                                                aws_access_key_id='E33PV586BD2CIMX6WPRE',
                                                                                aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', ))

        user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                    bucket_name=bucket)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in..', 'success')
        return redirect(url_for('old_login'))
    return render_template("newRegister.html ", title="SignUp Page", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in..', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register Page", form=form)


@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if current_user.is_authenticated and current_user.is_admin == True:
        return render_template('admin/index.html')
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash("incorrect credentials, please enter valid email and password", 'danger')

    return render_template('admin/signupAdmin.html', title="Admin login Page", form=form)


@app.route('/dashboard')
def home():
    return render_template('Client/dashboard.html', page='Dashboard', title="My title")





@app.route('/index')
def index():
    return render_template("admin/index.html ", title="Admin Home Page")


@app.route('/base')
def basetemplate():
    return render_template('baseTemplate.html', title="chart Page")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('old_login'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def UpdateMyProfile():
    form = UpdateMyProfiletForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.fullname = form.fullname.data
        current_user.email = form.email.data
        current_user.region = form.region.data
        current_user.country = form.country.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Your Account has been updated!', 'success')
        return redirect(url_for('UpdateMyProfile'))
    elif request.method == 'GET':
        form.fullname.data = current_user.fullname
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.region.data = current_user.region
        form.country.data = current_user.country
        form.address.data = current_user.address


    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("Client/profile_page.html", title="My Profile Page", image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('post created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/subscribe")
def subscribe():
    User.package = "Free Trial"
    db.session.commit()
    msg =" subscribed"

    return redirect('/package')

@app.route('/', methods=['GET', 'POST'])
@app.route('/oldlogin', methods=['GET', 'POST'])
def old_login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("incorrect credentials, please enter valid email and password", 'danger')
            msg = 'Invalid email or Password.!'

    return render_template('oldLogin.html', title="login Page", form=form)


@app.route('/profile')
def profile():
    return render_template('Client/profile_page.html', page='My Profile')





@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('Client/dashboard.html', page='Dashboard')


@app.route('/demo-video')
def demoVideo():
    return render_template('Client/demoVideo.html', page='Video Demonstration')


@app.route('/package')
def package():
    package = Package.query.all()

    return render_template('Client/package.html', page='Package' , package=package)


@app.route('/sync')
def sync():
    return render_template('Client/sync.html', page='Synchronization')


@app.route('/trash')
def trash():
    return render_template('Client/trash.html', page='Trash')


def ListFiles(s3):
    """List files in specific S3 URL"""
    response = s3.list_objects(Bucket='mynewbucket123')
    for content in response.get('Contents', []):
        yield content.get('Key')


'''
@app.route('/restore')
def restore():

    s3 = boto3.client("s3",
                      endpoint_url='https://s3.wasabisys.com',
                      aws_access_key_id='E33PV586BD2CIMX6WPRE',
                      aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )


    list_keys = []
    file_list = ListFiles(s3)
    for file in file_list:
        list_keys.append(file)
    return render_template('Client/restore.html',  title="My title", list_keys=list_keys)
'''


@app.route('/cloud-drive-software')
def software():
    return render_template('Client/software.html', page='Cloud Drive Application')


@app.route('/bucketname')
def getBucketname():
    name = current_user.bucket_name
    return name


UPLOAD_FOLDER = "uploads"


@app.route("/restore")
def storage():
    bucketname = current_user.bucket_name
    # contents = list_files("mynewbucket123")
    # return render_template('Client/restore.html', contents=contents)
    list_keys, listJpeg, listFolders, listRar, listTxt, listDocx, listPdf, listOthers = listBucketFiles(bucketname)
    rarLen = len(listRar)
    docsLen = len(listDocx)
    txtLen = len(listTxt)
    imagesLen = len(listJpeg)
    Pdflen=len(listPdf)
    return render_template('Client/restore.html', page='Restore', title="My title",
                           list_keys=list_keys, listJpeg=listJpeg, listFolders=listFolders,Pdflen=Pdflen,
                           listRar=listRar, listTxt=listTxt, listDocx=listDocx,
                           listPdf=listPdf, listOthers=listOthers,
                           rarLen=rarLen, docsLen=docsLen, txtLen=txtLen, imagesLen=imagesLen)

@app.route('/backup')
def backup():
    return render_template('Client/backup.html', page='Backup')

@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        Buckets= current_user.bucket_name
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))
        upload_file(f"uploads/{f.filename}", Buckets)
        flash('file uploaded successfully')

    return redirect("/backup")

@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        Bucket = current_user.bucket_name
        output = download_file(filename, Bucket)
        return send_file(output, as_attachment=True)


@app.route("/sharefile/<filename>", methods=['GET'])
def sharefile(filename):
    if request.method == 'GET':
        Bucket = current_user.bucket_name
        url = create_presigned_url(Bucket, filename)
        if url is not None:
            return render_template('Client/shareURL.html', url=url)

        # return requests.get(url)
        msg = "Copy Url to share"
        return redirect("/restore")


@app.route("/delete/<filename>", methods=['GET'])
def deleteFile(filename):
    if request.method == 'GET':
        Bucket = current_user.bucket_name
        delete = deletefile(Bucket, filename)

    return redirect('/restore')


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def listBucketFiles(bucketname):
    list = []
    listJpeg = []
    listFolders = []
    listRar = []
    listTxt = []
    listDocx = []
    listPdf = []
    listOthers = []

    s3 = boto3.client("s3",
                      endpoint_url='https://s3.wasabisys.com',
                      aws_access_key_id='E33PV586BD2CIMX6WPRE',
                      aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )

    for key in s3.list_objects(Bucket=bucketname)['Contents']:
        col = [key['Key'], convert_size(key['Size']), key['LastModified']]
        list.append(col)

    for obj in list:
        # print(obj[0])
        if pathlib.Path(obj[0]).suffix == '.txt':
            listTxt.append(obj)
        elif pathlib.Path(obj[0]).suffix == '.zip':
            listRar.append(obj)
        elif pathlib.Path(obj[0]).suffix == '.rar':
            # print(obj)
            listRar.append(obj)
        elif pathlib.Path(obj[0]).suffix == '.docx':
            listDocx.append(obj)
        elif pathlib.Path(obj[0]).suffix == '.jpeg':
            listJpeg.append(obj)
        elif pathlib.Path(obj[0]).suffix == '.png':
            listJpeg.append(obj)
        elif pathlib.Path(obj[0]).suffix == '.bmp':
            listJpeg.append(obj)
        elif pathlib.Path(obj[0]).suffix == '.jpg':
            listJpeg.append(obj)
        elif pathlib.Path(obj[0]).suffix == '':
            listFolders.append(obj)
        elif pathlib.Path(obj[0]).suffix == '.pdf':
            listPdf.append(obj)
        else:
            listOthers.append(obj)

    return list, listJpeg, listFolders, listRar, listTxt, listDocx, listPdf, listOthers


# ---------------- ADMIN PANEL STARTS HERE-------------------------------------


@app.route('/admin/dashboard')
def adminDashboard():
    users = User.query.all()
    return render_template('Admin/adminDashboard.html', page='Dashboard', users=users)


@app.route('/admin/analytics')
def adminAnalytics():
    return render_template('Admin/adminAnalytics.html', page=' System Analytics')


@app.route('/admin/packages')
def adminPackages():
    package = Package.query.all()
    return render_template('Admin/adminPackage.html', page='Packages', package=package)


@app.route('/admin/reports')
def adminReports():
    return render_template('Admin/adminReports.html', page='Reports')


@app.route('/admin/email')
def adminEmails():
    return render_template('Admin/adminEmail.html', page='Emails')


@app.route('/admin/invoice')
def billingEmails():
    return render_template('admin/billingEmail.html', page='Billing')


@app.route('/send_message', methods=['POST', 'GET'])
def send_message():
    if request.method == "POST":
        email = request.form['email']
        # subject = request.form['subject']
        msg = request.form['message']
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login("clouddriveteam@gmail.com", "sannanumernoman")
        server.sendmail("clouddriveteam@gmail.com", email, msg)
        server.quit()
        flash('Email sent!')

    return render_template('admin/adminEmail.html', flash=flash('email sent successfully!', 'success'))


# ---------- Package CRUD----------
@app.route("/packages/new", methods=['GET', 'POST'])
@login_required
def newPackage():
    form = PackageForm()
    if form.validate_on_submit():
        pkg = Package(title=form.title.data, price=form.content.data, )
        db.session.add(pkg)
        db.session.commit()
        flash('Package created!', 'success')
        return redirect(url_for('adminPackages'))
    return render_template('admin/createPackage.html', title='New Package', form=form, legend='New Package')


@app.route('/sendInvoice', methods=['POST', 'GET'])
def sendHtmlEmail():
    if request.method == "POST":
        email = request.form['email']
        subject = request.form['subject']
        msg = request.form['message']
    # Create message container - the correct MIME type is multipart/alternative.
    me = 'clouddriveteam@gmail.com'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = email

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = """\
    <html>
      <head></head>
      <body>
        <div class="w-50 m-auto">
        <!-- email template -->
        <table class="body-wrap"
               style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; width: 100%; background-color: #eaf0f7; margin: 0;"
               bgcolor="#eaf0f7">
            <tbody>
            <tr>
                <td valign="top"></td>
                <td class="container" width="600"
                    style="display: block !important; max-width: 600px !important; clear: both !important;"
                    valign="top">
                    <div class="content" style="padding: 50px 0">
                        <table class="main" width="100%" cellpadding="0" cellspacing="0"
                               style="border: 1px dashed #4d79f6;">
                            <tbody>
                            <tr>
                                <td class="content-wrap aligncenter" style="padding: 20px; background-color: #fff;"
                                    align="center" valign="top">
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tbody>
                                        <tr>
                                            <td style="padding-bottom: 20px; "><a href="#"><img
                                                    src="*"
                                                    alt="image"
                                                    style="height: 30px; margin-left: auto; margin-right: auto; display:block;"></a>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td class="content-block" style="padding: 0 0 20px;" valign="top">
                                                <h2 class="aligncenter"
                                                    style="font-family: 'Helvetica Neue',Helvetica,Arial,'Lucida Grande',sans-serif;font-size: 24px; color:black; line-height: 1.2em; font-weight: 600; text-align: center;"
                                                    align="center">Thanks for using <span
                                                        style="color: #004deb; font-weight: 700;">Cloud Drive</span>.
                                                </h2>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td class="content-block aligncenter" style="padding: 0 0 20px;"
                                                align="center" valign="top">
                                                <table class="invoice" style="width: 80%;">
                                                    <tbody>
                                                    <tr>
                                                        <td style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; padding: 5px 0;"
                                                            valign="top">Records<br>Invoice #12345<br>01 Sep
                                                            2018
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 5px 0;" valign="top">
                                                            <table class="invoice-items" cellpadding="0" cellspacing="0"
                                                                   style="width: 100%;">
                                                                <tbody>
                                                                <tr>
                                                                    <td style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; border-top-width: 1px; border-top-color: #eee; border-top-style: solid; margin: 0; padding: 10px 0;"
                                                                        valign="top">Premium Package
                                                                    </td>
                                                                    <td class="alignright"
                                                                        style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; text-align: right; border-top-width: 1px; border-top-color: #eee; border-top-style: solid; margin: 0; padding: 10px 0;"
                                                                        align="right" valign="top">$  21.99
                                                                    </td>
                                                                </tr>

                                                                <tr>
                                                                    <td style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; border-top-width: 1px; border-top-color: #eee; border-top-style: solid; margin: 0; padding: 10px 0;"
                                                                        valign="top">Tax
                                                                    </td>
                                                                    <td class="alignright"
                                                                        style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; text-align: right; border-top-width: 1px; border-top-color: #eee; border-top-style: solid; margin: 0; padding: 10px 0;"
                                                                        align="right" valign="top">$ 2.00
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; border-top-width: 1px; border-top-color: #eee; border-top-style: solid; margin: 0; padding: 10px 0;"
                                                                        valign="top">Extras
                                                                    </td>
                                                                    <td class="alignright"
                                                                        style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; text-align: right; border-top-width: 1px; border-top-color: #eee; border-top-style: solid; margin: 0; padding: 10px 0;"
                                                                        align="right" valign="top">$ 0.00
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td class="alignright" width="80%"
                                                                        style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; text-align: right; border-top-width: 2px; border-top-color: #50649c; border-top-style: solid; border-bottom-color: #50649c; border-bottom-width: 2px; border-bottom-style: solid; font-weight: 700; margin: 0; padding: 10px 0;"
                                                                        align="right" valign="top">Total
                                                                    </td>
                                                                    <td class="alignright"
                                                                        style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; text-align: right; border-top-width: 2px; border-top-color: #50649c; border-top-style: solid; border-bottom-color: #50649c; border-bottom-width: 2px; border-bottom-style: solid; font-weight: 700; margin: 0; padding: 10px 0;"
                                                                        align="right" valign="top">$ 23.99
                                                                    </td>
                                                                </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                    </tbody>
                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td class="content-block aligncenter"
                                                style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; text-align: center; margin: 0; padding: 0 0 20px;"
                                                align="center" valign="top"><a href="/"
                                                                               style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; color: #4d79f6; text-decoration: underline; margin: 0;">View
                                                in browser</a></td>
                                        </tr>
                                        <tr>
                                            <td class="content-block aligncenter"
                                                style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; text-align: center; margin: 0; padding: 0 0 20px;"
                                                align="center" valign="top"> Team Cloud Drive

                                            </td>
                                        </tr>
                                        <tr>
                                            <td class="content-block aligncenter"
                                                style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; font-size: 14px; vertical-align: top; text-align: center; margin: 0; padding: 0 0 20px;"
                                                align="center" valign="top">Comsats University, Islamabad

                                            </td>
                                        </tr>
                                        </tbody>
                                    </table>
                                    <!--end table-->
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                </td>
            </tr>
            </tbody>
        </table>
        <!-- ./ email template -->
    </div>
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login('clouddriveteam@gmail.com', 'sannanumernoman')
    mail.sendmail(me, email, msg.as_string())
    mail.quit()

    return render_template('admin/billingEmail.html', success='Invoice Email has been sent successfully!',
                           title='Billing ')


# ----------------------Buckets Config------------------
@app.route('/currentUser')
def currentUser():
    if current_user.is_authenticated:
        user = current_user.username
        print(user)
    return user


if __name__ == '__main__':
    app.run(debug=True)
