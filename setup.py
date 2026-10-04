from setuptools import setup, find_packages

setup(
        name='SpaceDock',
        version='1.0',
        url='https://spacedock.info',
        license='MIT with additions',
        author='VITAS',
        author_email='github.v@52k.de',
        description='Website engine for Kerbal Space Program mods',
        packages=find_packages(),
        scripts=['spacedock']
)
