FROM python:3.12-bookworm

WORKDIR /bot

ENV PYTHONBUFFERED=1

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD [ "python", "-u", "main.py" ]