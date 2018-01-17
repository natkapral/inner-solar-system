from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='solar_system',
      version='0.1',
      description='3d model of planets of the inner solar system using OpenGL, pygame and skyfield',
      long_description=readme(),
      keywords='3d model of the inner solar system',
      url='http://github.com/extremka/inner-solar-system',
      author='Natalia',
      license='MIT',
      packages=['solar_system'],
      install_requires=[
         'pygame',
         'PyOpenGL',
         'skyfield',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
