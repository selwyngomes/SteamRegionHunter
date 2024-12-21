from setuptools import setup, find_packages

setup(
    name="steam_region_hunter",
    version="1.0.0",
    description="A Steam Region Price Comparison Tool",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "pandas",
        "tabulate",
        "tqdm",
        "openpyxl"
    ],
    entry_points={
        "console_scripts": [
            "steam-region-hunter=steam_region_hunter.main:main"
        ]
    },
    include_package_data=True,
)
