import sys

def str_to_class(classname):
    slices = classname.split('.')
    if len(slices) > 1:
        return getattr(sys.modules['.'.join(slices[:-1])], slices[-1])
    else:
        return getattr(sys.modules['__main__'], classname)
