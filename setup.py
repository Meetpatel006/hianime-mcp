from setuptools import setup, find_packages

setup(
    name="animemcp",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "cloudscraper",
        "mcp",
        "anyio",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
            "isort",
            "mypy",
        ]
    },
    python_requires=">=3.9",
)
