# Use a base image with Python installed
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory into the container
COPY . ./

# Expose the port that Dash runs on (default is 8050)
EXPOSE 8050

# Command to run the Dash app when the container starts
CMD gunicorn -b 0.0.0.0:8050 app:server