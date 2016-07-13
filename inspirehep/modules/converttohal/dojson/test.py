import djson
simple = dojson.Overdo()

@simple.over('first', '^.*st$')
def first(self, key, value):
    return value + 1

@
