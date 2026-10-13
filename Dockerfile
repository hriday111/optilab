FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY designs ./designs
COPY robot ./robot
ENV PYTHONPATH=/app/src
CMD ["robot", "--outputdir", "/reports", "robot/dry_run.robot"]
