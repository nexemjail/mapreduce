from collections import defaultdict


class MapReduceTask(object):
    def __init__(self):
        self.intermediate = defaultdict(list)
        self.result = []

    def emit_intermediate(self,key, value):
        self.intermediate[key].append(value)

    def emit(self, value):
        self.result.append(value)

    def execute(self, collection, mapper, reducer):
        for element in collection:
            key, value = mapper(element)
            self.emit_intermediate(key, value)

        for key, value in self.intermediate.iteritems():
            self.emit(reducer(key, value))

        return self.result
