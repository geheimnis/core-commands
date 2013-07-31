import hashlib

class hash_class:

    def __init__(self):
        pass

    def get_name(self):
        return 'SHA-256'

    def get_output_size(self):
        return 256 

    def get_block_size(self):
        return 512 

    def hash(self, text):
        return hashlib.sha256(text).digest()
