FROM python:3-alpine

ENV REMOTE_SQLITEDICT_PORT 18753
ENV REMOTE_SQLITEDICT_DB_ROOT /data

WORKDIR /usr/src/app
COPY remote_sqlitedict.py .
COPY setup.py .

RUN python setup.py install

VOLUME /data

CMD [ "sh", "-c", "python -u -m remote_sqlitedict $REMOTE_SQLITEDICT_PORT -d $REMOTE_SQLITEDICT_DB_ROOT" ]