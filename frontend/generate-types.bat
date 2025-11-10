@echo off
echo Generating TypeScript types from OpenAPI schema...

REM Download OpenAPI schema from backend
curl -s http://127.0.0.1:8000/openapi.json -o src\api\openapi.json

REM Generate TypeScript types
npx openapi-typescript src\api\openapi.json -o src\api\types.gen.ts

echo.
echo TypeScript types generated at src\api\types.gen.ts
echo.
