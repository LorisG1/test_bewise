FROM python:alpine

WORKDIR /app

EXPOSE 5000

COPY requirements.txt .

RUN pip install --upgrade pip \
    pip install -r requirements.txt

COPY . .

CMD ["python", "main_test.py"]