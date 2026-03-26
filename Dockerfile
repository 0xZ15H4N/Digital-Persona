# Use official Python image
FROM python:3.8

# Set working directory
WORKDIR /app

# Copy backend code
COPY backend/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Flask default or your app port)
EXPOSE 5000

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the app
CMD ["python", "app.py"]