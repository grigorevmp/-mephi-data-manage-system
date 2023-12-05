FROM python:3
ADD . .
WORKDIR .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y python3 python3-pip
CMD ["python3", "web_server.py"]
