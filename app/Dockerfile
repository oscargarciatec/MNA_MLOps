# Dockerfile (located inside the 'app' folder)

# Use a Python base image
FROM python:3.13-slim

# Set environment variables for the application
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy all the app folder files and install dependencias from requirements file.
# requirements.txt is at the root of the build context (the 'app' folder)
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# The CMD instruction is simplified because api.py and Modelo.py are now at the root
# of the container's working directory (/app)
CMD exec uvicorn api:app --host 0.0.0.0 --port $PORT