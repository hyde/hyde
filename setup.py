from setuptools import setup, find_packages
from hyde.version import __version__

setup(name='hyde',
      version=__version__,
      description='hyde is a pythonic static website generator',
      author='Lakshmi Vyas',
      author_email='lakshmi.vyas@gmail.com',
      url='http://ringce.com/hyde',
      packages=find_packages(),
      install_requires=(
          'argparse',
          'commando',
          'jinja2',
          'pyYAML',
          'markdown',
          'smartypants',
          'pygments'
      ),
      scripts=['main.py'],
      entry_points={
          'console_scripts': [
              'hyde = main:main'
          ]
      },
      license='MIT',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Unix',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development',
            'Topic :: Software Development :: Build Tools',
            'Topic :: Software Development :: Websites',
            'Topic :: Software Development :: Static Websites',
      ],
)
