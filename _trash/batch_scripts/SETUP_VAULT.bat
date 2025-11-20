@echo off
echo ========================================
echo   Grace Secrets Vault - Setup
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python...
python --version
echo.

echo Generating secure vault key...
echo.

python -c "from cryptography.fernet import Fernet; key = Fernet.generate_key(); print('Generated Key:'); print(key.decode()); print(''); print('Add this to your .env file:'); print('GRACE_VAULT_KEY=' + key.decode())"

echo.
echo ========================================
echo.
echo IMPORTANT:
echo 1. Copy the GRACE_VAULT_KEY line above
echo 2. Add it to your .env file
echo 3. Restart the backend
echo 4. Your vault will persist across restarts
echo.
echo Without this key, secrets are lost on restart!
echo.
echo ========================================

pause
