from flask import Flask, request, render_template, redirect,jsonify, session
import boto3
import pymysql
from io import BytesIO
import os
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "super secret key"

# folder_path = os.path.abspath(os.path.dirname(__file__))

# obsolute_path = os.path.join(folder_path, 'user.db')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + obsolute_path

# db = SQLAlchemy(app)

temp_user = 'AKIASRT2Z46JTMGIYPQA'
temp_secret = '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'

Access_Key = 'AKIARTSJQ400KOIRFZXL'
Secret_Key = 'eGOHIH9PBUjKKzFOjs3aYOsIhee5K8indZz6JPfP'
Region = 'us-east-1'

user_Access_Key = 'AKIASRT2Z46JVIFDRNB5'
user_Secret_Key = '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'

DB_Name = "defaultdb"
DB_user = "admin"
Password = "multiweekdb"
DB_PORT = "3306"
db_Endpoint = "multiweekdb.clnopyq3sfwe.us-east-1.rds.amazonaws.com"

class NameofFile():
    filename = []

c_object = NameofFile()

sns_resource= boto3.client ("sns",
    aws_access_key_id=temp_user ,
    aws_secret_access_key=temp_secret,
    region_name=Region)

# class UserDetailsModel(db.Model):
#     users_firstName = db.Column(db.String(100))
#     users_lastName = db.Column(db.String(100))
#     users_Emailid = db.Column(db.String(100), primary_key=True)
#     given_Password = db.Column(db.String(100))
#     check_Password = db.Column(db.String(100))

#     def __str__(self):
#         return self.users_firstName

@app.route('/')
def home():
    return render_template("home.html")

def method_name():
    pass

def load_email_from_db():
    emails_in_db = []
    try:
        connection = pymysql.connect(host=db_Endpoint, user=DB_user, password=Password, database=DB_Name)
        cursor = connection.cursor()
        result = cursor.execute("SELECT users_Emailid from usersignupAkhil")
        emails = cursor.fetchall()
        for email in emails:
            emails_in_db.append(email)
    except Exception as e:
        return("Cannot get emails from the db")
    
    return emails_in_db

def load_email_and_password():
    emails_nd_password = {}
    try:
        connection = pymysql.connect(host=db_Endpoint, user=DB_user, password=Password, database=DB_Name)
        cursor = connection.cursor()
        result = cursor.execute("SELECT users_Emailid, given_Password from usersignupAkhil")
        emails = cursor.fetchall()
        for email in emails:
            emails_nd_password[email[0]] = email[1]
    except Exception as e:
        return("Cannot get emails from the db")
    
    return emails_nd_password

def email_subscribe(topic_Arn, protocol, endpoint):
    subscription = sns_resource.subscribe(TopicArn = topic_Arn, Protocol=protocol, Endpoint=endpoint, ReturnSubscriptionArn=True)

    return subscription['SubscriptionArn']
    
def billing_files(filename, user):
    try:
        connection = pymysql.connect(host=db_Endpoint, user=DB_user, password=Password, database=DB_Name)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO filestorageAkhil(filename, users_Emailid) VALUES(%s, %s);",(filename, user) 
        )
        connection.commit()
        print("Inserted to billings table")
        return 1
    except:
        return 0
    
def billed_files():
    user_and_files = {}
    try:
        connection = pymysql.connect(host=db_Endpoint, user=DB_user, password=Password, database=DB_Name)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM filestorageAkhil"
        )
        result = cursor.fetchall()
        for i in result:
            user_and_files[i[0]] = i[1]
        return user_and_files
    except:
        return 0
    

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user_details = {}
        user_details['user_firstname'] = request.form['firstname']
        user_details['user_lastname'] = request.form['lastname']
        user_details['user_emailid'] = request.form['emailid']
        user_details['user_password'] = request.form['password']
        user_details['user_checkpassword'] = request.form['confirmpassword']

        emails = load_email_from_db()

        
        if user_details['user_password'] != user_details['user_checkpassword']:
            return render_template("signup.html", error = "Check the passwords, they should be identical !")
        elif user_details['user_emailid'] in emails:
            return render_template("signup.html", error = "Email id already present")
        else:
            try: 
                connection = pymysql.connect(host=db_Endpoint, user=DB_user, password=Password, database=DB_Name)
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO usersignupAkhil(users_firstname, users_lastname, users_Emailid, given_Password) VALUES (%s, %s, %s, %s);",
                    (user_details['user_firstname'], user_details['user_lastname'], user_details['user_emailid'], user_details['user_password'])
                )
                print("Details Added Successfully")
                connection.commit()
                return render_template("thankyou.html", user = user_details['user_firstname'])

                # user_info = UserDetailsModel(users_firstName=user_details['user_firstname'],
                #                              users_lastName=user_details['user_lastname'],
                #                              users_Emailid=user_details['user_emailid'],
                #                              given_Password=user_details['user_password'],
                #                              check_Password=user_details['user_checkpassword'])
                # db.session.add(user_info)
                # db.session.commit()
                # return render_template("thankyou.html", user = user_details['user_firstname'])
            except Exception as error:
                return render_template("signup.html", error=error)
    else:
        return render_template("signup.html")
            

@app.route('/signin', methods = ['POST', 'GET'])
def signin():
    if request.method == 'POST':
        user_email = request.form['useremailid']
        user_password = request.form['userpassword']
        check =  load_email_and_password()
        print(check)
      
        if user_email not in check.keys():
            return render_template("signin.html", error = "You dont have an account please crate one. ")
        elif user_email in check.keys() and user_password != check[user_email]:
            return render_template("signin.html", error = "plese check your password, it does not match")
        elif user_email in check.keys() and user_password == check[user_email]:
            session['user'] = user_email
            return render_template("secretPage.html", user = user_email)
        else:
            return render_template("signin.html", error = "Something went wrong..")
    else:
        return render_template("signin.html")

@app.route('/s3upload', methods=['POST', 'GET'])
def s3upload():
    if request.method == 'POST' and request.files['formFile']:
        inputfile = request.files['formFile']
        print(inputfile)
        print(type(inputfile))
        temp = inputfile.filename
        print(render_template)
        filename = inputfile.getvalue()
        print(BytesIO(filename))
        s3_bucket_client = boto3.client('s3', aws_access_key_id = temp_user, aws_secret_access_key=temp_secret, region_name='us-east-1')
        
        s3_bucket_client.upload_fileobj(inputfile, "cloudfinalbucket", 'InputFiles/'+temp)
        
        billing_result = billing_files(temp, session['user'])

        provided_emails = {}

        provided_emails['user1'] = request.form['user1']
        provided_emails['user2'] = request.form['user2']
        provided_emails['user3'] = request.form['user3']
        provided_emails['user4'] = request.form['user4']
        provided_emails['user5'] = request.form['user5']

        print(provided_emails)

        s3_object_url = s3_bucket_client.generate_presigned_url('get_object', Params={'Bucket': 'cloudfinalbucket', 'Key':'InputFiles/'+temp}, ExpiresIn=8000)

        print(s3_object_url)
        
        email_topic = sns_resource.create_topic(Name='mylocal1')

        for user_email in provided_emails:
            if len(provided_emails[user_email]) > 5:
                topic_Arn = email_topic['TopicArn']
                protocol = 'email'
                endpoint = provided_emails[user_email]
                response = email_subscribe(topic_Arn, protocol, endpoint)
                sns_resource.publish(TopicArn = topic_Arn, Subject = "Click on the below link to download S3 object file. ", Message = "Click on the link to download file: " + s3_object_url)

        return render_template("secretPage.html", message = "File uploaded Successfully and email has been sent")
        
    else:
        return render_template("secretPage.html")

    # try:
    #     data = inputfile.getvalue()
    #     filename = inputfile.filename.split("\\")[-1]
    #     file_data = BytesIO(data)

    #     s3_client = boto3.client('s3', aws_access_key_id=ACCESS_Key, aws_secret_access_key=SECREAT_key, region_name=region)
    #     s3_client.upload_fileobj(file_data, "cloudfilestores", "files/" + filename)

    #     print("Success")
    #     return "success"
    # except Exception as e:
    #     print(f"Error: {e}")
    #     return "failure"
    return "something"

@app.route('/billing')
def billing_details():
    result = billed_files()
    print(result)
    files = list(result.keys())
    user_name = list(result.values())
    user_file = zip(user_name, files)
    if result == 0:
        return render_template('billing.html', error="No Files has been uploaded")
    if result:
        return render_template('billing.html', result = result)
    
    render_template('billing.html')

    

@app.before_request
def createtable():

    try:
        print("Creating Tables")
        connection = pymysql.connect(host=db_Endpoint, user=DB_user, password=Password, database=DB_Name)
        cursor = connection.cursor()
        cursor.execute("USE defaultdb;")
        cursor.execute("CREATE TABLE usersignupAkhil(users_firstname varchar(50), users_lastname varchar(50), users_Emailid varchar(50) unique, given_Password varchar(50), check_Password varchar(50))")
        cursor.execute("CREATE TABLE filestorageAkhil(filename varchar(50), users_Emailid varchar(50))")
        connection.commit()
        print("Tables created successfully")
    except Exception as e:
        print("Failed to create tables")
        print(e)


if __name__ == "__main__":
    app.run(debug=True)