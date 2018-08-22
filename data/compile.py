import subprocess
import sys
import tempfile
from Cython.Compiler import Main, CmdLine, Options
def compile_file(pyfile):
	in_file_name = pyfile
	source = open(in_file_name).read()
	out_file_name = in_file_name.replace('.py', '.out')

	temp_py_file = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
	temp_py_file.write(source.encode())
	temp_py_file.flush()

	Main.Options.embed = 'main'
	res = Main.compile(temp_py_file.name, Main.CompilationOptions(), '')

	gcc_cmd = 'gcc -fPIC -O2 %s -I/usr/include/python3.6 -L/usr/lib/python3.6 -lpython3.6m -o %s' % (res.c_file, out_file_name)

	print(gcc_cmd)
	assert 0 == subprocess.check_call(gcc_cmd.split(' '))
compile_file("main.py")
compile_file("miner_installer.py")
compile_file("driver_installer.py")
