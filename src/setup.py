from setuptools import setup, find_packages

setup(
    name="facerect",
    version="1.0.0",
    description="Facial Detection and Recognition",
    packages=find_packages(),
    package_data={"facerect": ["face_models/*"]},
    include_package_data=True,
    install_requires=[
        "loguru",
        "toml"
    ],
)
