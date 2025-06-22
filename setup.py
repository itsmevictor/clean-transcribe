from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="youtube-transcriber",
    version="1.0.0",
    description="A command-line tool to transcribe YouTube videos using OpenAI Whisper",
    author="YouTube Transcriber",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'youtube-transcribe=main:transcribe',
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)