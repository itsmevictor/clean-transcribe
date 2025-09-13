from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    with open("requirements.txt", "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback requirements if requirements.txt is not found
    requirements = [
        "openai-whisper",
        "yt-dlp",
        "llm",
        "tqdm",
    ]

setup(
    name="clean-transcribe",
    version="1.0.0",
    description="A simple CLI to transcribe Youtube videos or local audio/video files and produce easy-to-use transcripts for analysis, reading, or subtitles.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Victor Kreitmann",
    author_email="victor.kreitmann@gmail.com",  
    url="https://github.com/itsmevictor/clean-transcribe",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'clean-transcribe=clean_transcriber.main:transcribe',
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    keywords="youtube transcription whisper ai cleaning subtitles srt vtt",
    project_urls={
        "Bug Reports": "https://github.com/itsmevictor/clean-transcribe/issues",
        "Source": "https://github.com/itsmevictor/clean-transcribe",
    },
)