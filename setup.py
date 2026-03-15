from setuptools import find_packages, setup


setup(
    name="affect_aif",
    version="0.1.0",
    description="JAX-first multi-agent active inference trust-game simulations",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=1.26",
        "scipy>=1.11",
        "pandas>=2.0",
        "matplotlib>=3.8",
        "seaborn>=0.13",
        "jax>=0.4.28",
    ],
    python_requires=">=3.10",
)
