FROM python:3
ADD . .
WORKDIR .
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "web_server.py"]
