FROM vllm/vllm-openai:latest
# Default model to load (can be overridden at runtime)
ENV VLLM_MODEL=meta-llama/Llama-3.2-3B-Instruct
EXPOSE 8000
# Launch OpenAI-compatible API server
CMD ["--model","${VLLM_MODEL}","--port","8000","--served-model-name","default"]
