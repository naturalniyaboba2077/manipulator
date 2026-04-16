from setuptools import setup, find_packages
from pathlib import Path

base_dir = Path(__file__).resolve().parent
requirements_path = base_dir / "requirements.txt"

with requirements_path.open() as f:
    requirements = [
        line.strip()
        for line in f.readlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name='motion-core-API',
    version='0.1.2',
    description='Библиотека для управления оборудованием компании Applied Robotics',
    author='Mikhail Filchenkov',
    author_email='m.filchenkov@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.10',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    license='MIT',
)
