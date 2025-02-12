from setuptools import setup, find_packages

setup(
    name='tldr-tools',  
    version='0.2.4.1',     
    packages=find_packages(),  
    install_requires=[  
        'requests',
        'python-dotenv',
        'beautifulsoup4',
        'numpy',
        'pyyaml',
        'pandas'
    ],
    tests_require=['pytest'],
    # package_data={'tbd': ['data/tbd.json']}
    entry_points={  
        'console_scripts': [
            'tldr-submit=tldr_tools.tldr_submit:main', 
            'tldr-status=tldr_tools.tldr_status:main', 
            'tldr-download = tldr_tools.tldr_download:main',
            'chaff-batch = chaff_tools.batch:main', # Run contaminate and ready on batch (multiple receptors)
            'chaff-extract = chaff_tools.extract:main', # Extract downloaded tldr into a single flat folder
            'chaff-contaminate = chaff_tools.contaminate:main', # Create yaml from actives and chaff directory
            'chaff-ready = chaff_tools.make_dockopt_ready:main', # Create .tar.gz for given input 
            'chaff-splitdb2 = chaff_tools.split_db2:main', # split into train and test for input folder and fraction
        ],
    },
    author='Hai Pham',  
    author_email='haipham8315@gmail.com',  
    description='Use TLDR for dockopt, decoy generation, and job management.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/maomlab/tldr_docking', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', 
)