# Use the Python image as the base
FROM python:alpine3.17

# Prevent Python from writing bytecode files and run in unbuffered mode
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apk add --update --no-cache curl unzip git openssh-client

# Install Terraform
RUN curl -LO https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip \
    && unzip terraform_1.5.0_linux_amd64.zip \
    && rm terraform_1.5.0_linux_amd64.zip \
    && mv terraform /usr/local/bin/

# Create app folder and set permissions
RUN mkdir /app && chmod -R 777 /app

# Set the working directory in the container
WORKDIR /app

# Copy the source code into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint command
CMD ["python", "-m", "digitalai.release.integration.wrapper"]