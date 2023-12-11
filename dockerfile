# Define base image
FROM python:3.11.7-alpine3.19

# set maintainer label
LABEL maintainer  ="Worashdev.com"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copies the requirements.txt file from the local directory into the /tmp directory of the container.
COPY ./requirements.txt /tmp/requirements.txt 

COPY ./requirements.dev.txt /tmp/requirements.dev.txt 

# Copies the contents of the ./recipe_app directory from the local directory into the /recipe_app directory of the container.
COPY ./recipe_app /recipe_app

# Sets the working directory inside the container to /recipe_app.
WORKDIR /recipe_app

# Exposes port 8000. It's a declaration that the container listens on this port at runtime.
EXPOSE 8000

# Set the default value for the DEV argument
ARG DEV=false

# Creates a Python virtual environment at /py
RUN python -m venv /py

# Upgrades pip within the virtual environment. 
RUN /py/bin/pip install --upgrade pip

# Installs Python packages listed in /tmp/requirements.txt into the virtual environment.
RUN /py/bin/pip install -r /tmp/requirements.txt

# Executes the following commands based on the condition.
RUN if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi

# Removes the /tmp directory to clean up
RUN rm -rf /tmp

# Adds a new system user named django-recipe-app-user without a password and without creating a home directory
RUN adduser --disabled-password --no-create-home django-recipe-app-user

# Updates the system PATH to include the /py/bin directory
ENV PATH="/py/bin:$PATH"

# Switches the user context to django-recipe-app-user 
USER django-recipe-app-user 

