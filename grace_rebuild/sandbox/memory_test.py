
try:
    # Try to allocate 100MB string
    big_data = 'x' * (100 * 1024 * 1024)
    print("Allocated")
except MemoryError:
    print("Memory limit reached")
