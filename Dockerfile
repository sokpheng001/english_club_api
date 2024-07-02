FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

#  Mount the uploads directory to serve static files
VOLUME ["/app/uploads"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
