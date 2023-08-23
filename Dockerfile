FROM python:3.9-buster

# Install system dependencies required by Playwright
RUN apt-get update \
    && apt-get install -y wget libx11-xcb1 libxcb-dri3-0 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2 libxss1 libxrandr2 libasound2 libpangocairo-1.0-0 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libdrm2 libgbm1 libdbus-glib-1-2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Set the working directory
WORKDIR /app

# Copy the requirements file to the container image
COPY requirements.txt /app

# Copy the Python script to the container
COPY . .

# Install the Playwright Python package and other production dependencies
RUN pip3 install -r requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir playwright[firefox] playwright-stealth fake-useragent

# Install the Playwright browsers
RUN playwright install firefox

CMD ["python", "cookies_gen.py"]

