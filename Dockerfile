FROM python:3.11.1-slim

# set work directory
WORKDIR /app


# install dependencies
COPY requirements.txt .
# copy project

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN pip install python-dotenv

COPY . .