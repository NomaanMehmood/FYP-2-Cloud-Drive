import smtplib

import boto3
import math
from flask import Flask, render_template, request

app = Flask(__name__)

s3 = boto3.client("s3",
                  endpoint_url='https://s3.wasabisys.com',
                  aws_access_key_id='E33PV586BD2CIMX6WPRE',
                  aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )

posts = [
    {
        'author': 'umer',
        'title': 'blog 1',
        'content': "first post content",
        'date_posted': '12 Dec 2020',
    },
    {
        'author': 'Hamza',
        'title': 'blog 2',
        'content': "second post content",
        'date_posted': '24 Dec 2020',
    }

]


def ListFiles(s3):
    """List files in specific S3 URL"""
    response = s3.list_objects(Bucket='CheckCreateBucket123')
    for content in response.get('Contents', []):
        yield content.get('Key')


@app.route('/home')
def home():
    s3 = boto3.client("s3",
                      endpoint_url='https://s3.wasabisys.com',
                      aws_access_key_id='E33PV586BD2CIMX6WPRE',
                      aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )

    list_keys = []
    file_list = ListFiles(s3)
    for file in file_list:
        list_keys.append(file)
    return render_template('home.html', posts=posts, title="My title", list_keys=list_keys)

    # file_list = ListFiles(s3)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/base')
def base():
    return render_template('Client/baseTemplate.html', acti=True)


@app.route('/analytics')
def analytics():
    return render_template('Client/analytics.html', page='Analytics', acti=True)


@app.route('/backup', methods=['GET', 'POST'])
def backup():
    s3 = boto3.client("s3",
                      endpoint_url='https://s3.wasabisys.com',
                      aws_access_key_id='E33PV586BD2CIMX6WPRE',
                      aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )
    if request.method == 'POST':
        file = request.files['file']
        s3.upload_file(file.filename, Bucket='mynewbucket123', Key='My New Folder')

    return render_template('Client/backup.html', page='Backup', acti=True)


@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('Client/dashboard.html', page='Dashboard', acti=True)


@app.route('/demo-video')
def demoVideo():
    return render_template('Client/demoVideo.html', page='Video Demonstration', acti=True)


@app.route('/package')
def package():
    return render_template('Client/package.html', page='Package', acti=True)


@app.route('/sync')
def sync():
    return render_template('Client/sync.html', page='Synchronization', acti=True)


@app.route('/trash')
def trash():
    return render_template('Client/trash.html', page='Trash', acti=True)


@app.route('/restore')
def restore():
    list_keys, listJpeg, listFolders, listRar, listTxt, listDocx, listPdf, listOthers = listBucketFiles()
    rarLen = len(listRar)
    docsLen = len(listDocx)
    txtLen = len(listTxt)
    imagesLen = len(listJpeg)
    return render_template('Client/restore.html', page='Restore', posts=posts, title="My title",
                           list_keys=list_keys, listJpeg=listJpeg, listFolders=listFolders,
                           listRar=listRar, listTxt=listTxt, listDocx=listDocx,
                           listPdf=listPdf, listOthers=listOthers,
                           rarLen=rarLen, docsLen=docsLen, txtLen=txtLen, imagesLen=imagesLen)


@app.route('/cloud-drive-software')
def software():
    return render_template('Client/software.html', page='Cloud Drive Application')


@app.route('/login')
def login():
    return render_template('login_page.html', page='Login Page', image='login')


@app.route('/register')
def register():
    return render_template('register_page.html', page='Register Page')


@app.route('/profile')
def profile():
    return render_template('Client/profile_page.html', page='Profile Page')


@app.route('/reports')
def reports():
    return render_template('Client/reports.html', page='Reports')


@app.errorhandler(404)
def error(e):
    return render_template('error_page.html', page='Error Page'), 404


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def listBucketFiles():
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

    for key in s3.list_objects(Bucket='mynewbucket123')['Contents']:
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


# ADMIN PANEL STARTS HERE


@app.route('/admin/dashboard')
def adminDashboard():
    return render_template('Admin/adminDashboard.html', page='Dashboard')


@app.route('/admin/analytics')
def adminAnalytics():
    return render_template('Admin/adminAnalytics.html', page=' System Analytics')


@app.route('/admin/packages')
def adminPackages():
    return render_template('Admin/adminPackage.html', page=' Set Packages')


@app.route('/admin/reports')
def adminReports():
    return render_template('Admin/adminReports.html', page='Reports')


@app.route('/admin/email')
def adminEmails():
    return render_template('Admin/adminEmail.html', page='Emails')


@app.route('/send_message', methods=['POST', 'GET'])
def send_message():
    if request.method == "POST":
        email = request.form['email']
        #subject = request.form['subject']
        msg = request.form['message']
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login("clouddriveteam@gmail.com", "sannanumernoman")
        server.sendmail("clouddriveteam@gmail.com", "omermalik67@hotmail.com", msg)
        server.quit()



    return render_template('result.html', success='success')


if __name__ == '__main__':
    app.run(debug=True)
