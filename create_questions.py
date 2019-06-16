from models import User, Test, Question, db
import json

def create_db():
    with open("questions.json", "r") as read_file:
        data = json.load(read_file)
        for entry in data:
            # print('Looking: ', entry['test'])
            test_object = db.query(Test).filter_by(title=entry['test']).first()
            # print('Found: ', test_object)
            if test_object == None:
                test = Test(title=entry['test'])
                db.add(test)
                test_object = test
            question_object = db.query(Question).filter_by(title=entry['title']).first()
            # print('Found: ', question_object)
            if question_object == None:
                question = Question(title=entry['title'], a1=entry['a1'], a2=entry['a2'], a3=entry['a3'], correct=entry['correct'], test_id=test_object.id)
                db.add(question)
                db.commit()

if __name__ == '__main__':
    main()