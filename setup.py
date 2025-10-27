# setup.py
from setuptools import setup, find_packages

setup(
    name="edi_forecast",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Le tue dipendenze da requirements.txt
        "streamlit",
        "pandas",
        "OpenPyXL"
        # aggiungi le altre...
    ],
    python_requires=">=3.8",
)