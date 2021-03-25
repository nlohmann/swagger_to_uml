from setuptools import setup, find_packages

requires = [
    'PyYAML==5.4'
]

setup(
    name='swagger_to_uml',
    version='0.1',
    description='swagger_to_uml',
    classifiers=[
        "Programming Language :: Python"
    ],
    author='Niels Lohmann',
    author_email='mail@nlohmann.me',
    license='MIT',
    url='http://nlohmann.me',
    keywords='swagger uml plantuml',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    scripts=['bin/swagger_to_uml']
)
