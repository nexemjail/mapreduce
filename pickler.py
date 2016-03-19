#import pickle
import cPickle as pickle


def unpickle(string):
    return pickle.loads(string)


def pickle_object(obj):
    return pickle.dumps(obj)


def pickle_object_to_file(obj, filename):
    with open(filename, 'w') as file:
        pickle.dump(obj, file)


def unpickle_object_from_file(filename):
    with open(filename, 'r'):
        return pickle.load(filename)
