from setuptools import setup, find_packages

setup(
    name="fiberqms",
    version="0.1.0",
    description="Fiber Network Quality Monitoring System",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/fiberqms",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask>=2.0.1',
        'flask-socketio>=5.0.1',
        'python-dotenv>=0.19.0',
        'speedtest-cli>=2.1.3',
        'pandas>=1.3.3',
        'twilio>=7.0.0',
        'eventlet>=0.33.0'
    ],
    entry_points={
        'console_scripts': [
            'fiberqms=app.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.8',
)