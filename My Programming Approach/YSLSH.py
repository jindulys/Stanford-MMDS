import math

class HashFunc(object):
    '''universal hash function: ((a*x) % p) % n'''
    def __init__(self, buckets, dim = 1):
        self.n = buckets
        self.p = self.prime(buckets)
        self.a = [random.randint(1, self.p-1) for x in range(dim+1)]

    def __call__(self, x):
        if type(x) is list:
            x = x + [1]
        else:
            x = [x, 1]
        return (self.dot(x, self.a) % self.p) % self.n

    def dot(self, x, y):
        return sum([x[i]*y[i] for i in range(len(x))])


    def prime(self, p):
        p *= 2
        while not self.is_prime(p):
            p += 1
        return p

    def is_prime(self, num):
        for i in range(2,int(math.sqrt(num) + 1)):
            if (num % i) == 0:
                return False

        return True

def minhash(doc_shingles_dct, all_shingles_lst, hash_func_lst):
    nbr_permutations = len(hash_func_lst)
    doc_signature_dct = defaultdict(lambda:[sys.maxint] * nbr_permutations)
    #sort all columns
    print "\tsorting columns..."
    doc_column_dct = sort_documents(doc_shingles_dct, all_shingles_lst)

def sort_documents(doc_shingles_dct, all_shingles_lst):
    doc_binary_dct = {}
    i = 0
    for doc_id


def shingles_in_lst(word_lst, k):
    shingles_set = set()
    for i in xrange(len(word_lst)-k+1):
        result = ""
        for j in xrange(k):
            result += word_lst[i+j]
        shingles_set.add(result)
    return list(shingles_set)

def dict_from_file(file_location, k):
    '''here we get all sentences with their shingles from a file'''
    doc_shingles_dct = {}
    shingles_set = set()
    with open(file_location) as f:
        for line in f:
            idx = line.find(' ')
            doc_id = line[:idx]
            shingles_list = shingles_in_lst(line[idx+1:].split(), k)
            doc_shingles_dct[doc_id] = shingles_list

            for shingle in shingles_list:
                shingles_set.add(shingle)

    all_shingles_lst = list(shingles_set)
    all_shingles_lst.sort()

    return doc_shingles_dct, all_shingles_lst


def process_docs(file_location, k, nbr_of_bands):

    print "loading documents..."
    doc_shingles_dct, all_shingles_lst = dict_from_file(file_location, k)

    print "Generating permutation hash functions..."
    permutation_hash_func_lst = [HashFunc(len(all_shingles_lst)) for x in range(nbr_permutations)]

    print "Running minhash..."
    doc_signature_dict = minhash(doc_shingles_dct, all_shingles_lst, permutation_hash_func_lst)

if __name__ == "__main__":
    file_location = 'documents.txt'
    k = 3 #k value in k-gram for shingles
    nbr_of_bands = 3
    rows_per_band = 8
    nbr_permutations = nbr_of_bands * rows_per_band
    pairs_lst = process_docs(file_location, k, nbr_of_bands)
