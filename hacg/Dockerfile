FROM python:3.9-slim

WORKDIR /app

RUN python -m pip install -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

COPY . /app
CMD ["python", "main.py"]
