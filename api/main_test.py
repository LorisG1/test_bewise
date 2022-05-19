from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime
import os


ENDPOINT = "https://jservice.io/api/random"
USER = os.environ["PG_USER"]
HOST = os.environ["PG_HOST"]
PASSWORD = os.environ["PG_PASSWORD"]
PG_DB = os.environ["PG_DB"]

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USER}:{PASSWORD}@{HOST}/{PG_DB}'
db = SQLAlchemy(app)


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(250), unique=False, nullable=False)
    answer = db.Column(db.String(250), unique=False, nullable=False)
    date_create = db.Column(db.Date, unique=False, nullable=False)
    date_add = db.Column(db.DateTime, unique=False, nullable=False)

    def __repr__(self):
        return f'Q# {self.id}. {self.question}'


db.create_all()


def check(i):
    check_db = Questions.query.get(i["id"])
    while check_db:
        response_new = requests.get(url=ENDPOINT, params={"count": 1})
        check_db = Questions.query.get(response_new.json()[0]["id"])



@app.route('/')
def home():
    return render_template("index.html")


@app.route('/quiz', methods=["GET", "POST"])
def get_quiz():
    if request.method == "POST":
        questions_num = int(request.form.get("questions_num"))
        response = requests.get(url=ENDPOINT, params={"count": questions_num})
        response.raise_for_status()
        data = response.json()
        for i in data:
            # проверяем наличие вопроса в БД
            check_db = Questions.query.get(i["id"])
            if check_db:
                while check_db:
                    # делаем запрос нового вопроса, если прошлый уже есть в БЖ
                    response_new = requests.get(url=ENDPOINT, params={"count": 1})
                    data_new = response_new.json()[0]
                    check_db = Questions.query.get(data_new["id"])
                 # загружаем новый вопрос в БД
                new_question = Questions(
                    id=data_new["id"],
                    question=data_new["question"],
                    answer=data_new["answer"],
                    date_create=data_new["created_at"].split("T")[0],
                    date_add=datetime.now()
                )
            else:
                new_question = Questions(
                    id=i["id"],
                    question=i["question"],
                    answer=i["answer"],
                    date_create=i["created_at"].split("T")[0],
                    date_add=datetime.now()
                )
            db.session.add(new_question)
            db.session.commit()
        last_q = Questions.query.order_by(Questions.date_add.desc()).first()
        return f"{last_q}"
    return render_template("questions.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
