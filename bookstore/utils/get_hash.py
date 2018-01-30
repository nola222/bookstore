from hashlib import sha1

def get_hash(str):
    '''取一个字符串的哈希值'''
    sh = sha1()
    sh.update(str.encode('utf8'))
    return sh.hexdigest()


