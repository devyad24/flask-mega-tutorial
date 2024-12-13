FROM python:slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY config.py microblog.py babel.cfg .flaskenv google-crendentials.json tests.py boot.sh ./
RUN chmod a+x boot.sh

RUN flask translate compile

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]

