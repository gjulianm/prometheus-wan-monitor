from setuptools import setup, find_packages

setup(
    name='prometheus-wan-monitor', version='1.0.0',
    description='WAN monitor, ready to scrape via Prometheus',
    url='https://github.com/gjulianm/prometheus-wan-monitor',
    author='Guillermo Julián',
    author_email='guillermo@gjulianm.me',
    license='MIT',
    packages=find_packages(),
    entry_points={
        # You can add other entry points here.
        'console_scripts': [
            'prometheus-wan-monitor=prometheus_wan_monitor.__main__:main'
        ]
    },
    install_requires=[  # Add here requirements
        "speedtest-cli",
        "coloredlogs",
        'prometheus-client'
    ],
    extras_require={
        'dev': [  # Requirements only needed for development
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False)
