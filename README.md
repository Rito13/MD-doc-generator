## Introduction
This is simple python project for generating mark down documentation from GDExtension doc files.

Main part of script comes from [GodotEngine Repository](https://github.com/godotengine/godot/tree/master/doc/tools/make_rst.py).
But it was modified so .md files are generated intead of .rst.

## License 
see LICENSE.txt file

## Setup
 - Create virtual enviroment under name of `.venv`.
 - Install `polib` inside .venv, you can use pip for that task.
 
## Running
`.venv/bin/python3 make_md.py GDEngine_doc/ {directory to your .xml docs} -o {output directory}`
or you can run `.venv/bin/python3 make_md.py --help` for more informations.
