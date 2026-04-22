@echo off
:: This ensures the script knows where it is even if run as Administrator
set BASE_DIR=%~dp0
cd /d %BASE_DIR%

echo 🚀 Starting Granite 4.0 Research Brain...
echo 📍 Looking for llama-server in: bin\llama-server.exe

bin\llama-server.exe ^
  -m models\granite-4.0-micro-Q4_K_M.gguf ^
  -md models\granite-4.0-1b-Q4_K_M.gguf ^
  --port 8080 ^
  --ctx-size 4096 ^
  --n-gpu-layers 99 ^
  --draft 5 ^
  --chat-template granite

pause