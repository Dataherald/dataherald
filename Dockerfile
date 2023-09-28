FROM python:3.11.4

LABEL Author="Juan Carlos José Camacho"
LABEL version="0.0.1b"

RUN apt-get update
RUN apt-get -y install vim
RUN apt install tzdata -y
ENV TZ="Asia/Tokyo"
# Add the 'll' alias to the shell configuration file
RUN echo "alias ll='ls -alF'" >> /etc/bash.bashrc

WORKDIR /app

RUN pip install --no-cache-dir git+http://oauth2:glpat-bsSzoSuVcpBszng5QjVE@192.168.1.145/rockhampton/rh_python_common.git

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV DB_ENVIRONMENT=PRODUCTION
ENV PYTHONPATH=/app/scripts:${PYTHONPATH}

COPY . /app
RUN chmod 755 /app/scripts/DB_SETUP.sh



EXPOSE 80

CMD ["uvicorn", "dataherald.app:app", "--host", "0.0.0.0", "--port", "80"]
