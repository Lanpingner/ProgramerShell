from setuptools import setup, find_packages

setup(
    name='ProgramerShell',
    version='1.0.0',
    description='A highly specialized shell for programmers with built-in extensions, using Wayland and GtkLayerShell.',
    author='Your Name',
    author_email='berromaa@gmail.com',
    url='https://github.com/Lanpingner/programershell',
    packages=find_packages(include=['programershell', 'programershell.*']),
    include_package_data=True,
    install_requires=[
        'PyGObject',
    ],
    entry_points={
        'console_scripts': [
            'programershell=programershell.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Shells',
    ],
    python_requires='>=3.8',
    zip_safe=False,
)

