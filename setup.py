from setuptools import setup

setup(
	name="capdropper",
	version="1.0.0",
	description="Adds Drop Caps to .epub ebooks",

	author="Anupam Krishna",

	keywords="epub ebook drop cap",

	packages=['capdropper'],

	entry_points={
		"console_scripts": ['capdropper=capdropper:console_main']
	},
	include_package_data=True
	)