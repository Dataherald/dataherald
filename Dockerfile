FROM python:3.11.4

LABEL Author="Juan Carlos José Camacho"
LABEL version="0.0.1b"

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

EXPOSE 80

CMD ["uvicorn", "dataherald.app:app", "--host", "0.0.0.0", "--port", "80"]
