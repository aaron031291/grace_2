from setuptools import setup, find_packages

setup(
    name="grace-ai",
    version="1.0.0",
    description="Grace - Autonomous AI System with Self-Governance and Self-Healing",
    author="Grace Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "sqlalchemy>=2.0.25",
        "aiosqlite>=0.19.0",
        "python-jose[cryptography]>=3.3.0",
        "pydantic>=2.5.3",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "httpx>=0.24.0",
        "requests>=2.31.0",
    ],
    entry_points={
        'console_scripts': [
            'grace=grace_cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: AI",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.11',
)
