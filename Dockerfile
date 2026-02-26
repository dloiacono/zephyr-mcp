FROM python:3.13-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir build \
    && python -m build --wheel \
    && pip install --no-cache-dir dist/*.whl


FROM python:3.13-slim

LABEL org.opencontainers.image.title="zephyr-mcp" \
      org.opencontainers.image.description="MCP server for Zephyr Scale test management" \
      org.opencontainers.image.source="https://github.com/dloiacono/zephyr-mcp"

RUN groupadd --gid 1000 mcp \
    && useradd --uid 1000 --gid mcp --shell /bin/bash --create-home mcp

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/zephyr-mcp /usr/local/bin/zephyr-mcp

USER mcp
WORKDIR /home/mcp

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["zephyr-mcp"]
CMD ["--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
