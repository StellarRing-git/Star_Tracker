import contextlib
@contextlib.contextmanager
def redirect_argv(num):
    sys._argv = sys.argv[:]
    sys.argv=[str(num)]
    yield
    sys.argv = sys._argv

with redirect_argv(1):
    print(sys.argv)