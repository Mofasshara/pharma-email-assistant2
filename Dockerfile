FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["python", "-m", "uvicorn", "agents.api:app", "--host", "0.0.0.0", "--port", "80"]
