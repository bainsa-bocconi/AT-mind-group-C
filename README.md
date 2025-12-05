# AT-mind-group-C
Official repository for project: AT Mind; group C

Instruction - How the system works:
- On a GPU machine (possibly a Linux / WSL2 server, for compatibility issues with vLLM), run the vllm, chroma and fastapi servers after having installed all the local dependencies (the setup.sh file does that automatically). You would need an **HF token** to access the LLama model. You can ask it here, it's free: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct. You would also need an **NGROK token**, available, also for free, at https://dashboard.ngrok.com/api. You will need to manually enter these keys in the .env file once.
- The commands to be run on a bash terminal are: 
   - chmod +x setup.sh start.sh
   - ./setup.sh
   - ./start.sh
- share to everyone the ngrok link. From that link, you can enter the website from any device connected to the internet.
