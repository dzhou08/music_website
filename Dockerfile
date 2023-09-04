FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
WORKDIR /app
COPY . /app
RUN cd /app

RUN pip install -r requirements.txt

RUN apt-get update \
  && apt-get -y install tesseract-ocr

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
