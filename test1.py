__author__ = 'malbert'

class ToLoad(object):
    def __init__(self, var, func):
        self.var  = var
        self.func = func

    # style note: try to avoid overshadowing built-ins (e.g. type)
    def __get__(self, obj, cls):
            internal = getattr(obj, '_'+self.var)
            if internal is None:
                value = getattr(obj, self.func)()
                setattr(obj, '_'+self.var, value)
                return value
            else:
                return internal

class Foo(object):
    x = ToLoad('x', '_load_x')

    def __init__(self, y):
        self.y = y
        self._x = None

    def _load_x(self):
        print('Loading {0} into x'.format(self.y))
        return self.y

a = Foo(1)
b = Foo(2)
print(a.x)
print(b.x)
print(a.x)