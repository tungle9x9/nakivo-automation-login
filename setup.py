from setuptools import setup, find_packages

setup(
    name="nakivo_automation_platform",
    version="1.0.0",
    description="Enterprise-grade SDET Test Automation Platform for NAKIVO Backup & Replication",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "selenium>=4.20.0",
        "pytest>=8.0.0",
        "pytest-html>=4.1.1",
        "pytest-xdist>=3.5.0",
        "allure-pytest>=2.13.5",
        "pydantic>=2.7.0",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.1",
        "requests>=2.31.0",
    ],
)
