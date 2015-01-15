class first:
    def __init__(self, n):
        self.n = n
        self.num  = 0


    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if self.num < self.n:
            cur, self.num = self.num, self.num+1
            return cur
        else:
            raise StopIteration()

def generFirst(n):
    num = 0
    while num < n:
        yield num
        num += 1


if __name__ == "__main__":
    print "This is the input point"
    myFirst = first(100)
    mySum = sum(myFirst)
    print mySum

    myGerSum = sum(generFirst(100))
    print myGerSum
