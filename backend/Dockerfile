# 1. Base Image 
FROM python:3.9-slim

# 2. Create a folder inside the container to hold your app, and move inside it
WORKDIR /app

# 3. Copy the requirements file
COPY requirements.txt .

# 4. Run the command to install the dependencies
RUN pip install -r requirements.txt

# 5. Copy the actual application code (app.py) into the container
COPY app.py .

# 6. Expose the port so traffic can reach it (Backend uses 5000) 
EXPOSE 5000

# 7. The command that runs when the container starts
CMD ["python", "app.py"]