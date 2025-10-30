# syntax=docker/dockerfile:1.7
FROM ollama/ollama:latest

# Expose Ollama’s API port
EXPOSE 11434

# Optional: create a persistent volume mount point for model storage
VOLUME ["/root/.ollama"]

# Set up environment variable (can be overridden by docker-compose)
ENV OLLAMA_HOST=0.0.0.0

# This is the default entrypoint for the Ollama base image,
# so you usually don’t need to redefine it — but it’s explicit here:
CMD ["serve"]
