FROM mambaorg/micromamba:0.23.0

ARG MAMBA_USER=mambauser
ARG MAMBA_USER_ID=1000
ARG MAMBA_USER_GID=1000
ENV MAMBA_USER=$MAMBA_USER

USER root

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml
RUN micromamba install -y -f /tmp/env.yaml && micromamba clean --all --yes
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# install flood_app package
ADD . /flood_app
RUN pip install /flood_app

# Expose ports
EXPOSE 80

# Set the default directory where CMD will execute
WORKDIR /flood_app

# Set the default command to execute
# when creating a new container
CMD start-app
