from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="logiclens",
    version="0.1.0",
    author="LogicLens Team",
    author_email="team@logiclens.ai",
    description="AI-powered log analysis and system monitoring tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AkashicRecords/LogicLens",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.1",
        "flask-cors>=3.0.10",
        "python-dotenv>=0.19.0",
        "gunicorn>=20.1.0",
        "requests>=2.31.0",
        "python-ollama>=0.2.0",
        "psutil>=5.9.0",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "logiclens=app.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "logiclens": ["frontend/build/*"],
    },
) 