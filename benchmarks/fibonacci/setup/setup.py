from setuptools import Extension, setup
from Cython.Build import cythonize
# import pyximport; pyximport.install(pyimport=True)
from Cython.Compiler import Options




sourcefiles = ['server.py', 'helloworld_pb2_grpc.py', 'helloworld_pb2.py']

# sourcefiles = ['server.py']
extensions = [Extension("server", sourcefiles)]

# Options.embed = "serve"
setup(
    name= 'Cython gRPC server',
    ext_modules = cythonize(extensions)
    # ext_modules = cythonize("server.py")
)
