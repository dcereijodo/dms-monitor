"""
Start AWS Database Migration Service (DMS) tasks and wait for completion.
"""
from setuptools import find_packages, setup

dependencies = [
    'click',
    'boto3>=1.9.97,<=1.15.17',
]

setup(
    name='dms-monitor',
    version='0.1.0',
    url='https://github.com/dcereijodo/dms-monitor',
    license='BSD',
    author='David Cereijo',
    author_email='dcereijo@pagantis.com',
    description='Start AWS Database Migration Service (DMS) tasks and wait for completion.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'dms-monitor = dms_monitor.cli:dms_monitor',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
