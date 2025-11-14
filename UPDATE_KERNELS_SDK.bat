@echo off
echo ========================================
echo Updating All Kernels to Use SDK
echo ========================================
echo.

set KERNELS_DIR=backend\kernels

echo Updating federation_kernel.py...
powershell -Command "(Get-Content '%KERNELS_DIR%\federation_kernel.py') -replace 'from \.base_kernel import BaseDomainKernel', 'from backend.core.kernel_sdk import KernelSDK' -replace 'from \.base_kernel import KernelIntent', 'from .base_kernel import KernelIntent' -replace 'class (\w+)\(BaseDomainKernel\)', 'class $1(KernelSDK)' -replace 'super\(\).__init__\(\"federation\"\)', 'super().__init__(kernel_name=\"federation\")' | Set-Content '%KERNELS_DIR%\federation_kernel.py'"

echo Updating governance_kernel.py...
powershell -Command "(Get-Content '%KERNELS_DIR%\governance_kernel.py') -replace 'from \.base_kernel import BaseDomainKernel', 'from backend.core.kernel_sdk import KernelSDK' -replace 'class (\w+)\(BaseDomainKernel\)', 'class $1(KernelSDK)' -replace 'super\(\).__init__\(\"governance\"\)', 'super().__init__(kernel_name=\"governance\")' | Set-Content '%KERNELS_DIR%\governance_kernel.py'"

echo Updating intelligence_kernel.py...
powershell -Command "(Get-Content '%KERNELS_DIR%\intelligence_kernel.py') -replace 'from \.base_kernel import BaseDomainKernel', 'from backend.core.kernel_sdk import KernelSDK' -replace 'class (\w+)\(BaseDomainKernel\)', 'class $1(KernelSDK)' -replace 'super\(\).__init__\(\"intelligence\"\)', 'super().__init__(kernel_name=\"intelligence\")' | Set-Content '%KERNELS_DIR%\intelligence_kernel.py'"

echo Updating infrastructure_kernel.py...
powershell -Command "(Get-Content '%KERNELS_DIR%\infrastructure_kernel.py') -replace 'from \.base_kernel import BaseDomainKernel', 'from backend.core.kernel_sdk import KernelSDK' -replace 'class (\w+)\(BaseDomainKernel\)', 'class $1(KernelSDK)' -replace 'super\(\).__init__\(\"infrastructure\"\)', 'super().__init__(kernel_name=\"infrastructure\")' | Set-Content '%KERNELS_DIR%\infrastructure_kernel.py'"

echo Updating code_kernel.py...
powershell -Command "(Get-Content '%KERNELS_DIR%\code_kernel.py') -replace 'from \.base_kernel import BaseDomainKernel', 'from backend.core.kernel_sdk import KernelSDK' -replace 'class (\w+)\(BaseDomainKernel\)', 'class $1(KernelSDK)' -replace 'super\(\).__init__\(\"code\"\)', 'super().__init__(kernel_name=\"code\")' | Set-Content '%KERNELS_DIR%\code_kernel.py'"

echo Updating verification_kernel.py...
powershell -Command "(Get-Content '%KERNELS_DIR%\verification_kernel.py') -replace 'from \.base_kernel import BaseDomainKernel', 'from backend.core.kernel_sdk import KernelSDK' -replace 'class (\w+)\(BaseDomainKernel\)', 'class $1(KernelSDK)' -replace 'super\(\).__init__\(\"verification\"\)', 'super().__init__(kernel_name=\"verification\")' | Set-Content '%KERNELS_DIR%\verification_kernel.py'"

echo Updating memory_kernel.py...
powershell -Command "(Get-Content '%KERNELS_DIR%\memory_kernel.py') -replace 'from \.base_kernel import BaseDomainKernel', 'from backend.core.kernel_sdk import KernelSDK' -replace 'class (\w+)\(BaseDomainKernel\)', 'class $1(KernelSDK)' -replace 'super\(\).__init__\(\"memory\"\)', 'super().__init__(kernel_name=\"memory\")' | Set-Content '%KERNELS_DIR%\memory_kernel.py'"

echo Updating librarian_kernel.py...
powershell -Command "(Get-Content '%KERNELS_DIR%\librarian_kernel.py') -replace 'from \.base_kernel import BaseDomainKernel', 'from backend.core.kernel_sdk import KernelSDK' -replace 'class (\w+)\(BaseDomainKernel\)', 'class $1(KernelSDK)' -replace 'super\(\).__init__\(\"librarian\"\)', 'super().__init__(kernel_name=\"librarian\")' | Set-Content '%KERNELS_DIR%\librarian_kernel.py'"

echo Updating self_healing_kernel.py...
powershell -Command "(Get-Content '%KERNELS_DIR%\self_healing_kernel.py') -replace 'from \.base_kernel import BaseDomainKernel', 'from backend.core.kernel_sdk import KernelSDK' -replace 'class (\w+)\(BaseDomainKernel\)', 'class $1(KernelSDK)' -replace 'super\(\).__init__\(\"self_healing\"\)', 'super().__init__(kernel_name=\"self_healing\")' | Set-Content '%KERNELS_DIR%\self_healing_kernel.py'"

echo.
echo ========================================
echo ✅ All Kernels Updated to Use SDK
echo ========================================
echo.
echo Next Steps:
echo 1. Run: VERIFY_SYSTEM.bat
echo 2. Test: python test_system_e2e.py
echo.
pause
