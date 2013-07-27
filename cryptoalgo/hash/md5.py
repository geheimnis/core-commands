import hashlib

class hash_class:

    def __init__(self):
        pass

    def get_name(self):
        return 'MD5'

    def get_output_size(self):
        return 128

    def get_block_size(self):
        return 512

    def hash(self, text):
        return hashlib.md5(text).digest()
