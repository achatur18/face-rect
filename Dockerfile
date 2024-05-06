FROM python:3.11
RUN apt-get update && apt-get install -y libgl1 
WORKDIR /app
ADD . .
COPY main.py ./main.py
RUN pip install -r requirements.txt
EXPOSE 8000 
RUN useradd -ms /bin/bash appuser 
USER appuser
RUN pip install python-multipart
CMD ["uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0"]