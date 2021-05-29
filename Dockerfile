FROM python:3.7
#ENV FLASK_APP=kafka-producer.py
#ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["python3", "requestTrustScores.py", "5001"]
