from setuptools import setup, find_packages

setup(
    name='tldr_tools',  
    version='0.1.0',     
    packages=find_packages(),  
    install_requires=[  
        'requests',
        'python-dotenv',
        'beautifulsoup4',
        # 'dotenv',
    ],
    entry_points={  
        'console_scripts': [
            'tldr-submit=tldr_submit:main', 
            'tldr-status=tldr_status:main', 
            'tldr-download = tldr_download:main',
        ],
    },
    author='Hai Pham',  
    author_email='haipham8315@gmail.com',  
    description='Use TLDR for dockopt, decoy generation, and job management.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/haip/tldr_docking', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', 
)