FROM python:2.7
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y poppler-utils

RUN mkdir /parlament
WORKDIR /parlament
COPY pip-requirements.txt /parlament/
RUN pip install -r pip-requirements.txt

COPY . /parlament

RUN python setup.py develop
ENV PARLAMENT_SETTINGS settings.py
CMD ["python", "offenesparlament/manage.py", "runserver", "--host", "0.0.0.0"]
EXPOSE 5000
