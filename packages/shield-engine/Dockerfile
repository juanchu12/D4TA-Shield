FROM python:3.12-slim

# OCR is optional at runtime; skip tesseract packages in the image to save ~200MB+ on small VMs.
# Re-add tesseract-ocr + spa/eng when you need scanned-PDF fallback.
WORKDIR /app

COPY pyproject.toml README-PHASE1.md ./
COPY src ./src

RUN pip install --no-cache-dir . \
    && rm -rf /root/.cache/pip

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')" || exit 1

CMD ["uvicorn", "shield_engine.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
