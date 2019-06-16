from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, Test, Question, db
import uuid
import random
import string
from create_questions import create_db

app = Flask(__name__)
# db.drop_all()
# db.create_all()

# filling DB with questions
create_db()

@app.route('/generate', methods=['GET'])
def generate():
    key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
    # create new User - TODO: check for existing string in db
    user = User(key=key)
    db.add(user)
    db.commit()
    return render_template("index.html", key=key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assessment/<test_name>', methods=['GET'])
def test(test_name):
    test = db.query(Test).filter_by(title=test_name).first()
    # print('Found iD: ', test.id)
    questions = db.query(Question).filter_by(test_id=test.id).all()
    count = len(questions)
    # print('Found Questions: ', questions)
    response = make_response(render_template("test.html", test=test_name, count=count, question_number=0))
    return response

@app.route('/assessment/<test_name>/<question_number>', methods=['GET'])
def question(test_name, question_number):
    test = db.query(Test).filter_by(title=test_name).first()
    # print('Found iD: ', test.id)
    questions = db.query(Question).filter_by(test_id=test.id).all()
    count = len(questions)
    # print('Found Questions: ', questions)
    question = questions[int(question_number)]
    # checking if this is the last question

    if count == int(question_number)+1:
        response = make_response(render_template("question.html", test=test_name, question_title=question.title, question_number=int(question_number), last=True))
    else:
        response = make_response(render_template("question.html", test=test_name, question_title=question.title, question_number=int(question_number)))

    return response

@app.route('/assessments', methods=['POST', 'GET'])
def assessments():
    if request.method == 'GET':
        session = request.cookies.get('session')
        # if user is logged in, get key from db
        if session:
            user_object = db.query(User).filter_by(session_token=session).first()
            key = user_object.key

            # positive, so get assessments
            tests = db.query(Test).all()
            def just_title(obj):
                return obj.title
            test_names = map(just_title, tests)
            # send response with key and list
            response = make_response(render_template("overview.html", key=key, assessments=list(test_names)))
        else:
            return render_template('index.html')
    elif request.method == 'POST':
        key = request.form.get("id")
        user_object = db.query(User).filter_by(key=key).first()
        # check if key is stored
        if user_object:
            # generate token for session
            session_token = str(uuid.uuid4())

            # save session token to the database
            user_object.session_token = session_token
            db.add(user_object)
            db.commit()

            # positive, so get assessments
            tests = db.query(Test).all()
            def just_title(obj):
                return obj.title
            test_names = map(just_title, tests)

            # print('Try out ', test_names)

            # print('Got Tests: ', list)

            # create response with cookie and login information
            response = make_response(render_template("overview.html", key=key, assessments=list(test_names)))
            response.set_cookie("session", session_token)
            print('Existed and sending back')
        else:
            print('Key does not exist')
            response = make_response(render_template("index.html", error="Key was not found. If you lost it, get a new one..."))
    return response


if __name__ == '__main__':
    app.run()