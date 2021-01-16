import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="steam_reviews",
    version="0.1.0",
    author="Haotian Xu",
    author_email="i@xht97.cn",
    description="A package of getting game reviews from steam platform easily, for further text analytics projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TommyXu97/SteamReviews",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)