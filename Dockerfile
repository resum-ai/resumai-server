FROM python:3.10
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

## Copy all src files
COPY . .

## Run the application on the port 8080
EXPOSE 8000

# gunicorn 배포 명령어
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "resumai.wsgi:application"]