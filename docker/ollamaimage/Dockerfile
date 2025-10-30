# syntax=docker/dockerfile:1.7
FROM ollama/ollama:latest

EXPOSE 11434
VOLUME ["/root/.ollama"]

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_MODEL=llama3.2:3b

# Replace the image's default ENTRYPOINT ["ollama"] so CMD runs under a shell.
ENTRYPOINT ["/bin/sh", "-lc"]
CMD ["ollama serve & sleep 5 && ollama run ${OLLAMA_MODEL:-llama3.2:3b}"]