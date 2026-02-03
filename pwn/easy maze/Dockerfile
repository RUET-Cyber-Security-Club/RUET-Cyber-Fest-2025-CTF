FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# IMPORTANT: keep SECRET_KEY constant in production
ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    MAZE_FLAG=RCSC{W4lk_Th3_L0ng_M4z3} \
    SECRET_KEY=RCSC_maze_ctf_super_secret_key

EXPOSE 9004

ENV PORT=9004
CMD ["python", "app.py"]
