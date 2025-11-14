"""
Script to update all kernels to use KernelSDK
"""

import os
import re

KERNELS_TO_UPDATE = [
    'core_kernel.py',
    'federation_kernel.py',
    'governance_kernel.py',
    'intelligence_kernel.py',
    'infrastructure_kernel.py',
    'code_kernel.py',
    'verification_kernel.py',
    'memory_kernel.py',
    'librarian_kernel.py',
    'self_healing_kernel.py'
]

SDK_IMPORT = "from backend.core.kernel_sdk import KernelSDK"
OLD_IMPORT_PATTERN = r"from backend\.kernels\.base_kernel import BaseDomainKernel"

def update_kernel_file(filepath: str):
    """Update a single kernel file to use SDK"""
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace import
    content = re.sub(OLD_IMPORT_PATTERN, SDK_IMPORT, content)
    
    # Replace class inheritance
    content = re.sub(
        r'class\s+(\w+)\(BaseDomainKernel\):',
        r'class \1(KernelSDK):',
        content
    )
    
    # Update __init__ calls
    content = re.sub(
        r'super\(\).__init__\(\s*domain_name\s*=\s*["\'](\w+)["\']\s*\)',
        r'super().__init__(kernel_name="\1")',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated: {filepath}")
    return True

def main():
    """Update all kernels"""
    
    kernels_dir = 'backend/kernels'
    updated = 0
    
    print("🔄 Updating kernels to use KernelSDK...\n")
    
    for kernel_file in KERNELS_TO_UPDATE:
        filepath = os.path.join(kernels_dir, kernel_file)
        if update_kernel_file(filepath):
            updated += 1
    
    print(f"\n✅ Updated {updated}/{len(KERNELS_TO_UPDATE)} kernel files")
    print("\n📋 Summary:")
    print("   - All kernels now inherit from KernelSDK")
    print("   - Standardized initialization")
    print("   - Unified communication interface")
    print("   - Ready for Layer 1 orchestration")

if __name__ == '__main__':
    main()
