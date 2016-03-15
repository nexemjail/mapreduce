import inspect
import marshal as pickle


def get_foo():
    def func((k,v)):
        return (k, sum(v))
    return func




code = inspect.getsource(get_foo())
#print code
print get_foo().func_code

foo = FunctionType(code,get_foo().func_globals)
print foo((1,(1,2,3)))

#
# str = pickle.dumps(get_foo().func_code)
#
#
# foo =  pickle.loads(str)
# foo((1,(1,2,3,4,5)))
#
#
