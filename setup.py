from setuptools import setup, find_packages

setup(
    name="typeracer",
    version="1.0.0",
    description="A terminal-based type racing game",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "typeracer=typeracer.main:main",
        ],
    },
)
