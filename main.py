from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, Test, Question, db, Score
import uuid
import random
import string
from queries import create_db, save_result, get_results, get_certificate
from os import curdir
from os.path import join as pjoin

app = Flask(__name__)

# database utilities
#db.drop_all()
#db.create_all()

@app.route('/generate', methods=['GET'])
def generate():
    key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
    # create new User - TODO: check for existing string in db
    user = User(key=key)
    db.add(user)
    db.commit()
    return render_template("index.html", key=key)

@app.route('/key-info', methods=['GET'])
def key():
    return render_template('key-info.html')

@app.route('/')
def index():
    session = request.cookies.get('session')
    # if user is logged in, get key from db
    if session:
        return redirect(url_for('assessments'))
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

@app.route('/assessment/<test_name>/<question_number>', methods=['POST', 'GET'])
def question(test_name, question_number):
    question_number = int(question_number)
    session = request.cookies.get('session')
    # initiate last boolean
    last = False

    # GET VALUES

    # get test ID by name
    test = db.query(Test).filter_by(title=test_name).first()
    # get questions based on test ID
    question_list = db.query(Question).filter_by(test_id=test.id).all()
    # count questions in test
    count = len(question_list)
    # last question number
    last_number = count-1
    # get answer to question before the requested one
    last_question_answer = question_list[question_number-1].correct

    # CASE 3: Send Result
    if question_number == count:
        # check last result and change score
        answer = request.form.get('question')
        correct = answer == last_question_answer

        # get score from cookie
        score = request.cookies.get('score')
        calculate = score.split(' ')
        correct_score = int(calculate[0])
        total = int(calculate[1])
        if correct:
            print('Correct')
            calculate[0] = int(correct_score) + 1
        else:
            print('Not Correct')
            calculate[0] = int(correct_score)
        calculate[1] = int(total + 1)
        score_percent = str((calculate[0]/calculate[1])*100)
        # save result to database
        save_result(session, test.id, calculate[1], calculate[0])

        return make_response(render_template("result.html", test_name=test_name, score_percent=score_percent, questions_total=str(calculate[1]), questions_correct=str(calculate[0])))

    # CASE 1: First Question
    if question_number == 0:
        question = question_list[question_number]
        response = make_response(render_template("question.html", test_name=test_name, question_title=question.title, question_number=question_number, a1=question.a1, a2=question.a2, a3=question.a3, last=last))
        response.set_cookie("test", test_name)
        response.set_cookie("score", '0 0')
    # CASE 2: not first question
    else:
        # check if last question
        if last_number == question_number:
            last = True
        question = question_list[question_number]
        response = make_response(render_template("question.html", test_name=test_name, question_title=question.title, question_number=question_number, a1=question.a1, a2=question.a2, a3=question.a3, last=last))

        # check last result and change score
        answer = request.form.get('question')
        correct = answer == last_question_answer

        # get score from cookie
        score = request.cookies.get('score')
        calculate = score.split(' ')
        correct_score = int(calculate[0])
        total = int(calculate[1])
        if correct:
            print('Correct')
            calculate[0] = str(int(correct_score) + 1)
        else:
            print('Not Correct')
            calculate[0] = str(int(correct_score))
        calculate[1] = str(int(total + 1))
        new_score = ' '.join(calculate)
        response.set_cookie("score", new_score)

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

            # get latest results
            count, results = get_results(user_object.id)

            # send response with key and list
            response = make_response(render_template("overview.html", key=key, assessments=list(test_names), results_count=count))
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

            # get latest results
            count, results = get_results(user_object.id)

            # print('Got Tests: ', list)

            # create response with cookie and login information
            response = make_response(render_template("overview.html", key=key, assessments=list(test_names), results_count=count))
            response.set_cookie("session", session_token)
            print('Existed and sending back')
        else:
            print('Key does not exist')
            response = make_response(render_template("index.html", error="Key was not found. If you lost it, get a new one..."))
    return response

@app.route('/scores', methods=['GET'])
def scores():
    session = request.cookies.get('session')
    user_object = db.query(User).filter_by(session_token=session).first()
    # get user results
    count, results = get_results(user_object.id)
    # loop through results and create dict with important info
    result_list = []
    for result in results:
        result_container = {}
        score_percent = str((result.questions_correct / result.questions_total) * 100)
        test_object = db.query(Test).filter_by(id=result.test_id).first()
        # shorten percent if not 100 (more than 2 digits)
        if score_percent != '100.0':
            result_container['score_percent'] = int(score_percent[:2])
        else:
            result_container['score_percent'] = int(score_percent)
        result_container['test_title'] = test_object.title
        result_list.insert(0, result_container)

    response = make_response(render_template("scores.html", result_list=result_list))
    return response

@app.route('/admin/ben', methods=["GET"])
def admin():
    response = make_response(render_template("admin.html"))
    return response

@app.route('/certificate', methods=["POST"])
def certificate():
    name = request.form.get("name")
    assessment = request.form.get("assessment")
    print('Values: ', name, assessment)
    url = get_certificate(name, assessment)
    response = make_response(render_template("download.html", url=url))
    return response

@app.route('/update-db', methods=["POST"])
def update_db():
    # get CSV File and save it to the server system
    file = request.files['csvFile']
    # print(file.filename)

    csv_name = 'assessments.csv'

    store_path = pjoin(curdir, csv_name)

    file.save(store_path)

    # call function to update DB with CSV File Path
    create_db(csv_name)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()