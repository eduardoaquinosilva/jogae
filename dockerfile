# Step 1: Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Step 2: Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# Step 3: Create and set the working directory
WORKDIR /app

# Step 4: Install system dependencies
# These are needed for libraries like Pillow and psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libjpeg-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Install Python dependencies
# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the project code into the container
COPY . .

# Step 7: Create a non-root user
# This single command creates both the 'jogae' system group and the 'jogae' system user,
# avoiding the previous syntax error.
RUN adduser --system --group jogae

# Step 8: Change ownership of the app directory
RUN chown -R jogae:jogae /app

# Step 9: Switch to the non-root user
USER jogae

# Step 10: Expose the port the app runs on
EXPOSE 8000

# Step 11: Define the command to run the ASGI application
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "jogae.jogae.asgi:application"]

# Note: Consider using multi-stage builds for production for a smaller final image.
#       Also ensure your SQLite database file is stored in a persistent volume
