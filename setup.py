from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="hidr-agent",
    version="1.0.0",
    author="HIDR Agent Team",
    author_email="contact@hidr-agent.com",
    description="Host Intrusion Detection & Response System for Windows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hidr-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "gui": [
            "matplotlib>=3.5.0",
            "pandas>=1.3.0",
            "plotly>=5.0.0",
        ],
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "hidr-agent=monitor:main",
            "hidr-gui=run_gui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    keywords="security, malware, detection, edr, cybersecurity, windows, monitoring",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/hidr-agent/issues",
        "Source": "https://github.com/yourusername/hidr-agent",
        "Documentation": "https://github.com/yourusername/hidr-agent/wiki",
    },
)