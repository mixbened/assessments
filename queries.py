from models import User, Test, Question, db, Score
from pdfgeneratorapi import PDFGenerator
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

def get_certificate(name, assessment):
    pdf_client = PDFGenerator(api_key='58491fd517d41c9cf0233acd38f4c900bdaedc8d3622e34ff60925a7d188d2eb', api_secret='426102c7b00afc1f5202fd8280fff25ce8d9349b0c929f7e7f6ec09929b4c188')
    pdf_client.set_workspace('benedikt.mix@startplatz.de')
    new_pdf = pdf_client.create_document(template_id=55970, data={"name": name, "assessment": assessment}, document_format="pdf",response_format="url")
    return new_pdf.response


if __name__ == '__main__':
    main()