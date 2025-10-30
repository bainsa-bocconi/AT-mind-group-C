# syntax=docker/dockerfile:1.7
FROM ollama/ollama:latest

# Expose Ollama’s API port
EXPOSE 11434

# Optional: create a persistent volume mount point for model storage
VOLUME ["/root/.ollamaimage"]

# Set up environment variable (can be overridden by docker-compose)
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_MODEL=llama3.2:3b
CMD ["bash", "-lc", "ollama serve & sleep 5 && ollama pull ${OLLAMA_MODEL:-llama3.2:3b} && wait"]
