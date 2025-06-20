"""Setup script for packaging the Trending Issue Resolver."""

from setuptools import setup, find_packages

setup(
    name="trending_issue_resolver",
    version="0.1.0",
    description="AI-powered trending issue detection and resolution system",
    author="Trending Issue Resolver Team",
    packages=find_packages(),
    install_requires=[
        "google-cloud-bigquery>=3.11.0",
        "google-cloud-datastore>=2.18.0",
        "google-cloud-aiplatform>=1.38.0",
        "requests>=2.31.0",
        "streamlit>=1.24.0",
        "pandas>=1.5.3",
        "plotly>=5.13.1",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)