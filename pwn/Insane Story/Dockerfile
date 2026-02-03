# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy all files and folders from the current directory to /app in the container
COPY . /app

# Install any needed packages specified in requirements.txt if it exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Expose the port used by server.py
EXPOSE 1576

# Run the server.py script when the container launches
CMD ["python", "server.py"]
