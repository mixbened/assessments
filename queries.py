from models import User, Test, Question, db, Score
import json
import csv

def create_db(csvFilePath):
    jsonFilePath = 'questions.json'
    data = []
    with open(csvFilePath) as csvFile:
        csvReader = csv.DictReader(csvFile)
        for rows in csvReader:
            data.append(rows)
    with open(jsonFilePath, 'w+') as jsonFile:
        jsonFile.write(json.dumps(data, indent=4))
    with open(jsonFilePath, "r") as read_file:
        data = json.load(read_file)
        for entry in data:
            # print('Looking: ', entry['test'])
            test_object = db.query(Test).filter_by(title=entry['test']).first()
            # print('Found: ', test_object)
            if test_object == None:
                test = Test(title=entry['test'])
                db.add(test)
                test_object = test
            new_question = Question(title=entry['title'], a1=entry['a1'], a2=entry['a2'], a3=entry['a3'], correct=entry['correct'], test_id=test_object.id)
            # case the question exists
            question_object = db.query(Question).filter_by(title=entry['title']).first()
            if question_object != None:
                # print('Found duplicate ', question_object)
                db.delete(question_object)
                db.commit()
                db.add(new_question)
            # case the question does not exists
            else:
                db.add(new_question)
            db.commit()



def save_result(session,test_id,questions_total,questions_correct):
    user_id = db.query(User).filter_by(session_token=session).first().id
    result = Score(user_id=user_id,test_id=test_id,questions_total=questions_total,questions_correct=questions_correct)
    db.add(result)
    db.commit()

def get_results(id):
    scores = db.query(Score).filter_by(user_id=id).all()
    count = len(scores)
    return count, scores

if __name__ == '__main__':
    main()