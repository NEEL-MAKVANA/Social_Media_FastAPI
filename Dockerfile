# Use the official python image as the base image
FROM python:3.10.12
# Set the working directory inside the container
WORKDIR /app
# Copy the requirements files
COPY requirements.txt .
# Command to install all requirements
RUN pip install --no-cache-dir -r requirements.txt
# Copy the application code
COPY . .
# Run alembic migration to upgrade database to the latest version
RUN alembic upgrade head
# Expose port 3000
EXPOSE 8000






