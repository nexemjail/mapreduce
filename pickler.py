import pickle


def pickle_object(obj):
    return pickle.dumps(obj)


def pickle_object_to_file(obj, filename):
    pickle.dump(obj, filename)