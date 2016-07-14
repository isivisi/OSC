from setuptools import setup

setup(
    name='opensm',
    description='Sound mixer',
    author='John Iannandrea',
    author_email='jiannandrea@gmail.com',
    url='http://github.com/isivisi/opensoundmixer',
    install_requires=[
        'requests',
        'numpy'
    ],
    include_package_data=True,
    version='0.1.0',
    packages=['opensm'],
    zip_safe=False,
    license='GNU',
    keywords='sound mixer',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'opensm = opensm.osm:main'
        ]
    }
)
