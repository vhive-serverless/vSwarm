# Set the base image to use to Ubuntu
# FROM --platform=amd64  ubuntu:jammy-20221130
FROM --platform=riscv64  ubuntu:jammy-20221130
  
# Update the default application repository sources list
# RUN apt update 

# Install Memcached
RUN apt-get update  && apt-get install -y memcached

# Port to expose (default: 11211)
EXPOSE 11211

# Default Memcached run command arguments
CMD ["-m", "128"]

# Set the user to run Memcached daemon
USER daemon

# Set the entrypoint to memcached binary
ENTRYPOINT memcached

# docker build --platform linux/amd64  --tag pourpourr/memcached .
# docker build --platform linux/amd64  --tag pourpourr/memcached:x86 .
# docker push docker.io/pourpourr/memcached:x86
# docker build --platform linux/riscv64  --tag pourpourr/memcached:riscv64 .
# docker push docker.io/pourpourr/memcached:riscv64