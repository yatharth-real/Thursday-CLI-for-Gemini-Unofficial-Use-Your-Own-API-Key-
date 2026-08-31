from setuptools import setup, find_packages

setup(
    name="thursday-cli",
    version="0.1.0",
    description="Thursday: A vibrant, highly visual TUI and CLI built for Google Gemini models.",
    author="Community",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "rich",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "thursday=thursday.cli:main",
        ],
    },
)
