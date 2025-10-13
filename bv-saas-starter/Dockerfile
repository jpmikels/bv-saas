# Use the official Python 3.10 as the base
FROM python:3.10-slim

# Set the main folder for the app inside the box
WORKDIR /app

# First, copy the shopping list into the box
COPY requirements.txt .

# Now, read the shopping list and install all the tools
RUN pip install --no-cache-dir -r requirements.txt

# Finally, copy the rest of your app's code into the box
COPY . .

# Tell the box what command to run when it starts
CMD ["python", "app.py"]
