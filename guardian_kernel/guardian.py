import sys
import os
import socket

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from guardian_kernel.immutable_log import immutable_log
from guardian_kernel.base_models import Base, engine

async def main():
    """Main entrypoint for the Guardian Kernel"""
    print("Guardian Kernel Initialized")

    # Create a health check socket
    health_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    health_socket.bind(('127.0.0.1', 65432))
    health_socket.listen()
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Log a startup message
    await immutable_log.append(
        actor="guardian_kernel",
        action="system_start",
        resource="guardian_kernel",
        subsystem="guardian",
        payload={"message": "Guardian Kernel started"},
        result="success"
    )
    
    print("Guardian Kernel running...")

    # Accept one connection to signal readiness, then close
    conn, addr = await asyncio.get_event_loop().sock_accept(health_socket)
    conn.close()
    health_socket.close()

if __name__ == "__main__":
    asyncio.run(main())