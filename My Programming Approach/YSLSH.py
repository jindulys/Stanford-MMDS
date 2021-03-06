import math
import sys
import random
from collections import defaultdict

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

    print "\ttraversing rows..."
    for i in xrange(len(all_shingles_lst)):
        permutation_lst = []
        # compute all permutations for this row and save them to be used by all columns.
        # this is import since it avoids computing these permutations again for each column.

        for hash_func in hash_func_lst:
            permutation_lst.append(hash_func(i))

        for doc_id, column_lst in doc_column_dct.iteritems():
            if column_lst[i]:
                for j, permutation in enumerate(permutation_lst):
                    doc_signature_dct[doc_id][j] = min(doc_signature_dct[doc_id][j], permutation)
    return dict(doc_signature_dct)

def LSH(doc_signature_dct, nbr_of_bands):
    '''locality sensitive hashing dividing signatures into bands'''

    nbr_of_permutations = len(doc_signature_dct.itervalues().next())
    rows_per_band = nbr_of_permutations / nbr_of_bands

    if rows_per_band != int(rows_per_band):
        raise ValueError("nbr of bands is not a multiple of nbr of permutations")

    buckets_dct_lst = [defaultdict(list) for x in range(nbr_of_bands)]

    for doc_id, signature in doc_signature_dct.iteritems():
        for j in range(nbr_of_bands):
            band = signature[j*rows_per_band:(j+1)*rows_per_band]
            bucket = ''.join(str(e) for e in band)
            buckets_dct_lst[j][bucket].append(doc_id)
    return buckets_dct_lst


def look_for_pairs(buckets_dct_lst):

    '''Here in any of the band they both are same we defined it is same'''
    pairs_dict = {}
    for buckets in buckets_dct_lst:
        for key, docs_lst in buckets.iteritems():
            n = len(docs_lst)
            if n > 1:
                for i in xrange(n-1):
                    #for j in xrange(1,n):   --> here I made a mistake
                    for j in xrange(i+1, n):
                        pairs_dict[(docs_lst[i], docs_lst[j])] = None
    return pairs_dict.keys()



def sort_documents(doc_shingles_dct, all_shingles_lst):
    doc_binary_dct = {}
    i = 0
    for doc_id, shingles_lst in doc_shingles_dct.iteritems():
        sorted_binary_lst = sort_document(shingles_lst, all_shingles_lst)
        doc_binary_dct[doc_id] = sorted_binary_lst
        i += 1
        if i%1000 == 0:
            print '\t\tsorted %i documents'%i
    return doc_binary_dct

def sort_document(shingles_lst, all_shingles_lst):
    sorted_binary_lst = []
    shingles_lst.sort()
    j = 0
    for shingle in all_shingles_lst:
        if (j < len(shingles_lst)):
            if shingle == shingles_lst[j]:
                sorted_binary_lst.append(True)
                j += 1
            else:
                sorted_binary_lst.append(False)
        else:
            sorted_binary_lst.append(False)
    return sorted_binary_lst


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

    print "Running LSH..."
    buckets_dct_lst = LSH(doc_signature_dict, nbr_of_bands)

    print "Getting Candidate Pairs..."
    pairs_lst = look_for_pairs(buckets_dct_lst)

    return pairs_lst


if __name__ == "__main__":
    file_location = 'documents.txt'
    k = 3 #k value in k-gram for shingles
    nbr_of_bands = 3
    rows_per_band = 8
    nbr_permutations = nbr_of_bands * rows_per_band
    pairs_lst = process_docs(file_location, k, nbr_of_bands)

    print "Found %i probable duplicated documents" % len(pairs_lst)
