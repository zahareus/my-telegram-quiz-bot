FROM python:3.12

WORKDIR /usr/src/suggestion
COPY requirements.txt .
ENV PYTHONPATH="/usr/src/suggestion"
RUN pip install -r requirements.txt

COPY . ./
CMD ["python3", "./main.py"]



