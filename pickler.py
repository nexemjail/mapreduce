import pickle


<<<<<<< HEAD
def unpickle(string):
    return pickle.loads(string)


=======
>>>>>>> master
def pickle_object(obj):
    return pickle.dumps(obj)


def pickle_object_to_file(obj, filename):
<<<<<<< HEAD
    with open(filename, 'w') as file:
        pickle.dump(obj, file)


def unpickle_object_from_file(filename):
    with open(filename,'r'):
        return pickle.load(filename)
=======
    pickle.dump(obj, filename)
>>>>>>> master
