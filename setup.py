from setuptools import setup, find_packages


setup(
    name='sanskrit',
    version='0.1.0',
    description='Sanskrit utilities',
    long_description='TODO',

    url='https://github.com/sanskrit/sanskrit',
    author='learnsanskrit.org',
    author_email='info@learnsanskrit.org',
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='sanskrit',

    packages=find_packages(exclude=['docs', 'test*']),
    install_requires=['sqlalchemy >= 0.7'],
    extras_require={
        'dev': ['pytest'],
        'test': ['pytest'],
    }
)
