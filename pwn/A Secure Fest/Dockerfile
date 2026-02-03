FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Create non-root user and challenge directory
RUN useradd -m ctf && mkdir -p /challenge && chown -R ctf:ctf /challenge

WORKDIR /challenge

# Copy prebuilt binary + server
COPY fest server.py ./

# Set permissions
RUN chmod 755 fest && \
    chown ctf:ctf fest server.py

# Set the flag as an environment variable
ENV FLAG="RCSC{Ev3ryth1ng_1s_F3st1ng}"

USER ctf

EXPOSE 9001

# At container start:
#  - write the FLAG into flag.txt
#  - chmod it
#  - then exec server.py
CMD ["sh", "-c", "echo \"$FLAG\" > /challenge/flag.txt && chmod 600 /challenge/flag.txt && exec python3 server.py"]
