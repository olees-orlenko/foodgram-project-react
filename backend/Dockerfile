FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY foodgram/ .
CMD ["gunicorn", "--bind", "0.0.0.0:8888", "foodgram.wsgi:application"]