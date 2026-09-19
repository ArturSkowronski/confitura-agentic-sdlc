# Serwer MCP warsztatu na bazie toolboxa (potrzebuje mvn do run_build). Buduj po fabryka-toolbox: scripts/obrazy.sh
ARG BASE=fabryka-toolbox:lekcja
FROM ${BASE}
RUN pip3 install --no-cache-dir --break-system-packages "mcp>=1.10,<2"
COPY workspace.py server.py /app/
WORKDIR /app
ENV WORK_DIR=/work/repo EVENTS_FILE=/work/events.jsonl PORT=3000 PYTHONUNBUFFERED=1
EXPOSE 3000
CMD ["python3", "/app/server.py"]
