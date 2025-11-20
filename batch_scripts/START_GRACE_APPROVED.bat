@echo off
REM Start Grace with single approval pre-granted
set GRACE_AUTO_APPROVE=true
set GRACE_ENV=development
set GRACE_SINGLE_APPROVAL=true
set GRACE_BATCH_CONSENT=true
set GRACE_SKIP_CONSENT_PROMPTS=true
python serve.py
