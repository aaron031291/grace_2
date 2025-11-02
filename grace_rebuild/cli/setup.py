"""
Setup file for Grace CLI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding='utf-8').splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="grace-cli",
    version="1.0.0",
    description="Terminal interface for Grace AI system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Grace AI Team",
    author_email="team@grace-ai.dev",
    url="https://github.com/yourusername/grace",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=requirements,
    extras_require={
        'audio': ['pyaudio>=0.2.14', 'pydub>=0.25.1'],
        'dev': ['pytest>=7.4.3', 'pytest-asyncio>=0.21.1', 'pytest-mock>=3.12.0', 'pytest-cov>=4.1.0'],
    },
    entry_points={
        'console_scripts': [
            'grace=enhanced_grace_cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.9',
    include_package_data=True,
    zip_safe=False,
)
