from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-max-v2",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="MCP Max v2 - A modern Python project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-max-v2",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        # List your project's dependencies here
        # e.g., 'numpy>=1.19.0',
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.5b2",
            "isort>=5.8.0",
            "mypy>=0.812",
            "flake8>=3.9.0",
        ],
    },
)
