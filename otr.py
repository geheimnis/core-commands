#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OTR chatting session manager
============================
a simple OTR principle inspired chatting session manager. NOT compatible with
any of existing OTR implementations.
"""
import time

from hash import hash_generator, object_hasher
from _geheimnis_ import get_uuid
from crypt import xipher


class OTRSession:

    _database = None

    _init_message = """
HERE BEGINS AN OTR SESSION
==========================
You should not have read this message. But if you do, which means that you've
also decrypted the remaining parts of this session, here are important infor-
mation for you.
  You now have the ability to forge part of a dialog. First, we'll discuss how
our messages are constructed. Each 'packet', or a part of encrypted text
messages, which is transmitted in our OTR session, are simply so constructed:

  1. Use the 'authenticate key', which is equal to the SHA-1 binary value of
     the encrypting key, to generate the HMAC value of plaintext.
  2. Put the HMAC value just ahead of plaintext. It is clear to see that this
     only increases the plaintext's length by a given length, namely 160 bits.
  3. Use the encrypting key to encrypt this whole stuff, using the algorithm
     that you've seen, in CTR mode.
  4. Pack the ciphertext produced in 3 with sender, receiver or codebook ID
     and timestamp together, and HMAC sign them, also using this authenticate
     key. This should be clear of you.

  To forge a dialog, you can always take the first transmitted packet in this
OTR session as raw material. The first transmitted packet is always in a
content of this text(see <https://github.com/geheimnis/core-commands/otr.py>).
And you'll find or derive the 'authenticate key' used. After doing so, write
down your custom message, HMAC it, and join the HMAC value and your custom
message together, with HMAC value comes first. You should have known the
plaintext of this original transmitted packet, including the leading HMAC
value, because you have got the 'authenticate key'.
  Then, compare your joined plaintext and your guessed plaintext, bit by bit.
When there is at the N-th place a difference between two bits, flip the cor-
responsing bit in the same place of the original ciphertext. Finally, truncate
your ciphertext, and wrapped it like we have discussed in step 4.
  Now you've produced a plausible forged dialog part, which shall be
recognized by the partners joined in this session. Have fun!

OTR会话开始
===========
您本不该阅读到这条消息的。但是如果您还是读到了，那么您也应该能解密整个会话的其
他部分。如果这样，这里有些对您有用的东西。
  您现在可以伪造这个会话了。在讨论之前，我们先介绍这一会话中消息的结构。每份
”消息”，亦即一次发送的加密信息，是如此产生的：

  1. 使用“认证密钥”，即加密密钥的SHA1产生的二进制散列值，计算明文的HMAC校验
     值。
  2. 将HMAC校验值放于明文的头部。显然，明文的长度的增量是一个确定值：160比特。
  3. 运用加密密钥将这一新数据加密。算法您已经了解了，操作模式是CTR模式。
  4. 将第3步产生的密文和发送者、接收者或者密码本ID、发送时间戳之类的信息包装在
     一起，然后用HMAC签署它们。仍然使用原来的认证密钥。您应该很清楚这一结构。

  为了伪造这个会话，您可以用这一会话中传输的第一个包作为材料。这个包传输的内容
总是这篇文章的内容（参考代码：
          <https://github.com/geheimnis/core-commands/otr.py>
）。显然，您已经找到了或者能求出会话的认证密钥。在此之后，准备您的伪造信息，
计算HMAC值，然后HMAC认证值打头，伪造信息在后构建原始数据。由于您也已经了解了包
括相应的HMAC认证值在内的会话第一包的内容，您可以将您的原始数据和这一包的内容进
行按比特位的比较。如果您在第N比特上发现数据的不同，就请翻转这一第一数据包的密
文在对应比特位上的比特。最后，将您处理完的新密文数据的大小进行截取，使之符合您
的密文长度，然后根据上述第4步的方法封装数据。
  这样您就构建了可以被通信双方认可的伪造对话。祝好运！

    """

    INIT_METHOD_SHAREDSECRET = 1
    INIT_METHOD_CODEBOOK = 2
    INIT_METHOD_PGPLETTER = 4

    _session_id = None
    _store_piece = None

    def __init__(self, database):
        self._database = database
        self._init_message = self._init_message.strip()

    def new(self, buddy_identity, method, **argv):
        if method not in [1,2,4]:
            raise Exception("Unrecognized initialization method.")

        buddy_id = buddy_identity.get_id()
        if buddy_id == None:
            raise Exception("Invalid buddy id.")

        sharedsecret = ''
        if method == 1:
            sharedsecret = argv['shared_secret']
        elif method == 2:
            pass
        elif method == 4:
            pass

        hasher = hash_generator()
        sharedsecret = hasher.option({
            'algorithm': 'WHIRLPOOL',
            'output_format': 'raw',           
        }).digest(sharedsecret)

        authenticate_key = self._derive_authenticate_key(sharedsecret)

        chaos = \
            hasher.option('algorithm', 'MD5').digest(authenticate_key)

        session_id = get_uuid(chaos)

        piece = {
            'begin_time': time.time(),
            'shared_secret': sharedsecret,
            'send': [],
            'receive': [],
            'buddy_id': buddy_id,
        }

        self._database.set('otrsessions', session_id, piece)
        if False != self.load(session_id):
            self.set_send(self._init_message)
            return session_id

        return False

    def load(self, session_id):
        self._session_id = None
        self._store_piece = self._database.get('otrsessions', session_id)
        if self._store_piece != None and type(self._store_piece) == dict:
            self._session_id = session_id
            return session_id
        return False

    def terminate(self):
        """Terminate a Session

        The shared secret will be removed. This session ID, however, will be
        kept with storing its authenticate key."""
        if self._session_id:
            self._store_piece = self._derive_authenticate_key(
                self._store_piece['shared_secret']
            )
        self._session_id = None

    def set_send(self, plaintext):
        if not self._session_id:
            return False

        if len(plaintext) > len(self._init_message):
            # This will lead to impossible of forging our session.
            return False

        sharedsecret = self._store_piece['shared_secret']

        authenticator = hash_generator().option({
            'HMAC': self._derive_authenticate_key(sharedsecret),
            'algorithm': 'SHA-1',
            'output_format': 'RAW',
        })

        plaintext_HMAC = authenticator.digest(plaintext)

        new_plaintext = plaintext_HMAC + plaintext

        ciphertext = xipher(sharedsecret).encrypt(new_plaintext)

        packet_core = {
            'ciphertext': ciphertext,
            'timestamp': time.time(),
        }
        packet_hash = object_hasher('SHA-1').hash(packet_core)
        packet_sign = authenticator.digest(packet_hash)

        packet = {
            'HMAC': packet_sign,
            'core': packet_core,
            'session_id': self._session_id,
        }

        self._store_piece['send'].append(packet)

        return True

    def set_receive(self, packet):
        try:
            packet_sign, packet_core, session_id = \
                packet['HMAC'], packet['core'], packet['session_id']

            self.load(session_id)
            if self._session_id == None:
                return False

            sharedsecret = self._store_piece['shared_secret']
            authenticator = hash_generator().option({
                'HMAC': self._derive_authenticate_key(sharedsecret),
                'algorithm': 'SHA-1',
                'output_format': 'RAW',
            })

            packet_hash = object_hasher('SHA-1').hash(packet_core)
            packet_sign2 = authenticator.digest(packet_hash)
            if packet_sign2 != packet_sign:
                return False

            ciphertext = packet_core['ciphertext']
            timestamp = packet_core['timestamp']

            plaintext = xipher(sharedsecret).decrypt(ciphertext)
            head_length = len(packet_sign2)
            HMAC_head = plaintext[:head_length] # equals to such length
            plaintext = plaintext[head_length:]

            self._store_piece['receive'].append({
                'plaintext': plaintext,
                'timestamp': timestamp,
                'buddy_id': self._store_piece['buddy_id'],
            })

            return True

        except Exception,e:
            raise Exception('Error loading OTR packet - %s' % e)
             
    def get_send(self):
        return self._store_piece['send'].pop(0)

    def get_receive(self):
        return self._store_piece['receive'].pop(0)

    def _derive_authenticate_key(self, sharedsecret):
        return hash_generator().option({
            'algorithm': 'SHA-1',
            'output_format': 'RAW'
        }).digest(sharedsecret)

if __name__ == '__main__':

    from _geheimnis_ import get_database
    from identity import identity as ID
    me = ID()
    me.initialize('testIdentity', '')

    buddy = ID()
    buddy.initialize('MyBuddy', '')

    db = get_database(me, '0000')

    otrsession = OTRSession(db)

    print '* Generate a session'
    session_id = otrsession.new(
        buddy,
        otrsession.INIT_METHOD_SHAREDSECRET,
        shared_secret = 'Some secret'
    )
    print '- Session ID: %s' % session_id

    otrsession = OTRSession(db)
    otrsession.load(session_id)

    print '* Get init message'
    p = otrsession.get_send()

    print '* Set receive'
    otrsession.set_receive(p)

    print otrsession.get_receive()

    otrsession.terminate()
