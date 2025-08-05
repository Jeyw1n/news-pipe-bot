FROM python:3.12-bookworm

WORKDIR /bot

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD [ "python", "main.py" ]