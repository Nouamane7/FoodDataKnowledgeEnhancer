from setuptools import setup, find_packages

setup(
    name="food-processor",
    version="1.0.0",
    description="Transform PostgreSQL ingredients into detailed MongoDB products using local LLMs",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "psycopg2-binary==2.9.7",
        "pymongo==4.5.0",
        "ollama==0.2.1",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "pydantic==2.4.2",
    ],
    entry_points={
        'console_scripts': [
            'food-processor=main:main',
        ],
    },
)
