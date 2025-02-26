FROM python:3.10

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "mock_hiscox_api.py"]
