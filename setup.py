from setuptools import setup, find_packages

setup(
    name="sqlgen",
    version="0.1.0",
    author="ryohei-iwamoto",
    author_email="celeron5576@gmail.com",
    description="Convert CSV or pandas DataFrame to SQL INSERT statements with batching, null handling, and size-limited output.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ryohei-iwamoto/sqlgen",  # GitHub repo URL
    packages=find_packages(),
    install_requires=[
        "pandas"
    ],
    extras_require={
        "progress": ["tqdm"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
