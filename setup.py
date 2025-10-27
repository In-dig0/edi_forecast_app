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
        "openpyxl",
        "python-dotenv"
        # aggiungi le altre...
    ],
    python_requires=">=3.8",
)