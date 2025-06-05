from setuptools import setup

setup(
    name="sqlgen",
    version="0.1.5",
    author="ryohei-iwamoto",
    author_email="celeron5576@gmail.com",
    description="Convert CSV or pandas DataFrame to SQL INSERT statements with batching, null handling, and size-limited output.",
    url="https://github.com/ryohei-iwamoto/sqlgen",
    py_modules=["sqlgen"],
    install_requires=["pandas"],
    extras_require={"progress": ["tqdm"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
