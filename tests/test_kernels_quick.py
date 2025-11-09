"""
Quick test to verify all 9 domain kernels load correctly
"""

print("Testing Grace Domain Kernels...")
print("="*60)

try:
    from backend.kernels import (
        BaseDomainKernel,
        memory_kernel,
        core_kernel,
        code_kernel,
        governance_kernel,
        verification_kernel,
        intelligence_kernel,
        infrastructure_kernel,
        federation_kernel
    )
    
    print("✓ All kernel imports successful!")
    print()
    
    kernels = [
        ("Base Kernel", BaseDomainKernel, "Foundation"),
        ("Memory Kernel", memory_kernel, "Knowledge & Storage"),
        ("Core Kernel", core_kernel, "System & User Interaction"),
        ("Code Kernel", code_kernel, "Code Gen & Execution"),
        ("Governance Kernel", governance_kernel, "Policy & Safety"),
        ("Verification Kernel", verification_kernel, "Contracts & Benchmarks"),
        ("Intelligence Kernel", intelligence_kernel, "ML & Causal Reasoning"),
        ("Infrastructure Kernel", infrastructure_kernel, "Monitoring & Workers"),
        ("Federation Kernel", federation_kernel, "External Integrations"),
    ]
    
    print("Loaded Kernels:")
    print("-" * 60)
    for name, kernel, purpose in kernels:
        if name == "Base Kernel":
            print(f"  {name:25} - {purpose}")
        else:
            kernel_name = kernel.kernel_name if hasattr(kernel, 'kernel_name') else 'unknown'
            print(f"✓ {name:25} ({kernel_name:15}) - {purpose}")
    
    print()
    print("="*60)
    print(f"✅ SUCCESS: All 9 domain kernels loaded!")
    print()
    print("Architecture:")
    print("  270+ APIs → 9 Intelligent AI Agents → 1 Intent per Domain")
    print()
    print("Test endpoints:")
    print("  POST /kernel/memory")
    print("  POST /kernel/core")
    print("  POST /kernel/code")
    print("  POST /kernel/governance")
    print("  POST /kernel/verification")
    print("  POST /kernel/intelligence")
    print("  POST /kernel/infrastructure")
    print("  POST /kernel/federation")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
