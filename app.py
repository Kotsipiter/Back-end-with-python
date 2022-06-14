import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time
from bson.json_util import dumps
from pymongo.collection import ReturnDocument
from pymongo.message import update

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['InfoSys']

# Choose collections
students = db['Students']
users = db['Users']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    return user_uuid in users_sessions

# ΕΡΩΤΗΜΑ 1: Δημιουργία χρήστη
@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    data_username = data["username"]
    data_password = data["password"]
    db_response = users.find_one({"username": data_username})
    
    if (db_response == None ):
        users.insert_one({"username": data_username,"password": data_password})
        # Μήνυμα επιτυχίας
        return Response(data['username']+" was added to the MongoDB",status=200, mimetype='application/json') 
    # Διαφορετικά, αν υπάρχει ήδη κάποιος χρήστης με αυτό το username.
    else:
        # Μήνυμα λάθους (Υπάρχει ήδη κάποιος χρήστης με αυτό το username)
        return Response("A user with the given email already exists",status=400, mimetype='application/json') 
    
# ΕΡΩΤΗΜΑ 2: Login στο σύστημα
@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    # Έλεγχος δεδομένων username / password
    data_username = data["username"]
    data_password = data["password"]
    db_response = users.find_one({"username": data_username,"password": data_password})
    # Αν η αυθεντικοποίηση είναι επιτυχής. 
    # Να συμπληρώσετε το if statement.
    if (db_response != None ): 
        user_uuid = create_session(data_password)
        res = {"uuid": user_uuid, "username": data['username']}
        return Response(json.dumps(res), mimetype='application/json') # ΠΡΟΣΘΗΚΗ STATUS

    # Διαφορετικά, αν η αυθεντικοποίηση είναι ανεπιτυχής.
    else:
        # Μήνυμα λάθους (Λάθος username ή password)
        return Response("Wrong username or password.",mimetype='application/json') # ΠΡΟΣΘΗΚΗ STATUS
@app.route('/getStudent', methods=['GET'])
def get_student():
    # Request JSON data
    data = None 
    student = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    
    uuid = request.headers.get('Authorization')
    if not is_session_valid(uuid):
        return Response("Incorrect uuid",status=401,mimetype='application/json')
    
    student = students.find_one({"email": data["email"]})
    
    if(student!=None):
        return Response(dumps(student), status=200, mimetype='application/json')
    else:
        return Response("Student with given email not found", mimetype='application/json')
    
@app.route('/getStudents/thirties', methods=['GET'])
def get_students_thirty():
    found_students = None
    
    uuid = request.headers.get('Authorization')
    if not is_session_valid(uuid):
        return Response("Incorrect uuid",status=401,mimetype='application/json')
    
    found_students = students.find( { "yearOfBirth": { "$eq": 1991 } } )
    if found_students!=None:
        print(found_students)
        
        # Η παρακάτω εντολή χρησιμοποιείται μόνο σε περίπτωση επιτυχούς αναζήτησης φοιτητών (δηλ. υπάρχουν φοιτητές που είναι 30 ετών).
        return Response(dumps(found_students), status=200, mimetype='application/json')
    else:
        return Response("No such students found",mimetype='application/json')
    
# ΕΡΩΤΗΜΑ 5: Επιστροφή όλων των φοιτητών που είναι τουλάχιστον 30 ετών
@app.route('/getStudents/oldies', methods=['GET'])
def get_students_oldies():
    found_students = None
   
    
    found_students = students.find( { "yearOfBirth": { "$lte": 1991 } } )
    if found_students!=None:
        print(found_students)
        
        # Η παρακάτω εντολή χρησιμοποιείται μόνο σε περίπτωση επιτυχούς αναζήτησης φοιτητών (δηλ. υπάρχουν φοιτητές που είναι 30 ετών).
        return Response(dumps(found_students), status=200, mimetype='application/json')
    else:
        return Response("No such students found",mimetype='application/json')

    # Η παρακάτω εντολή χρησιμοποιείται μόνο σε περίπτωση επιτυχούς αναζήτησης φοιτητών (υπάρχουν φοιτητές που είναι τουλάχιστον 30 ετών).
    return Response(json.dumps(students), status=200, mimetype='application/json')

@app.route('/getStudentAddress', methods=['GET'])
def get_student_address():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    uuid = request.headers.get('Authorization')
    if not is_session_valid(uuid):
        return Response("Incorrect uuid",status=401,mimetype='application/json')
    
    
    student = list(students.find({"email": data["email"]},{"_id": 0, "name": 1,'email': 1, 'address.street': 1, 'address.postcode': 1}))
    if (student != None) & (student['email'] != None):
        return Response(dumps(student), status=200, mimetype='application/json')
    else:
        return Response("No such student found or no address given",mimetype='application/json')
@app.route('/deleteStudent', methods=['DELETE'])
def delete_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    uuid = request.headers.get('Authorization')
    if not is_session_valid(uuid):
        return Response("Incorrect uuid",status=401,mimetype='application/json')
    
    db_response = students.find_one_and_delete({'email': data["email"]})
    if (db_response == None):
        msg = "No such student found"
        return Response(msg,mimetype='application/json')
    else:
        msg = db_response['name'] + " was deleted"
        return Response(msg, status=200, mimetype='application/json')
@app.route('/addCourses', methods=['PATCH'])
def add_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "courses" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    uuid = request.headers.get('Authorization')
    if not is_session_valid(uuid):
        return Response("Incorrect uuid",status=401,mimetype='application/json')
    
    student = students.find_one_and_update({'email': data['email']},{"$set":{"courses": data['courses']}},return_document=ReturnDocument.AFTER)
    
    if student!=None:
        return Response(dumps(student), status=200, mimetype='application/json')
    else:
        return Response("No student with such email found",mimetype='application/json')

@app.route('/getPassedCourses', methods=['GET'])
def get_courses():
    # Request JSON data
    data = None 
    student = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    uuid = request.headers.get('Authorization')
    if not is_session_valid(uuid):
        return Response("Incorrect uuid",status=401,mimetype='application/json')

    db_response = students.find_one({'email': data['email']},{"_id": 0,"courses": 1})
    student = json.loads(dumps(db_response))
    
    if db_response == None:
        return Response("No such student found ")
    
    print (student[1][1])
    for doc in student:
        print(type(student))
        print(student['course.course 1'])
        if(int(student[doc]) >= 5):
            student.update(doc)
        
    if student == None:
        return Response("No courses passed")
            
    # Η παρακάτω εντολή χρησιμοποιείται μόνο σε περίπτωση επιτυχούς αναζήτησης φοιτητή (υπάρχει ο φοιτητής και έχει βαθμολογίες στο όνομά του).
    return Response(dumps(student), status=200, mimetype='application/json')