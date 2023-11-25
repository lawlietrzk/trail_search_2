FROM python:3.10.8-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m playwright install firefox
RUN python -m playwright install-deps

# Run the application:
COPY . app/
EXPOSE 8501

WORKDIR /app

CMD streamlit run app.py