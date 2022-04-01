from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util.number import bytes_to_long, long_to_bytes


class Cryptographer:
    def __init__(self, public_key_location, private_key_location):
        self.__public_key = RSA.importKey(open(public_key_location, 'rb').read())
        self.__private_key = RSA.importKey(open(private_key_location, 'rb').read())

    @staticmethod
    def generate_rsa_keys(private_key_location, public_key_location):
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open(private_key_location, "wb")
        file_out.write(private_key)
        file_out.close()

        public_key = key.publickey().export_key()
        file_out = open(public_key_location, "wb")
        file_out.write(public_key)
        file_out.close()

    def sign(self, data):
        h = SHA256.new(data)
        return pkcs1_15.new(self.__private_key).sign(h)

    def verify(self, data, signature):
        h = SHA256.new(data)
        try:
            pkcs1_15.new(self.__public_key).verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False


if __name__ == '__main__':
    data = 'Hello, world!'
    data_bytes = bytes(data, 'utf-8')
    cryptographer = Cryptographer('../secrets/public_key.pem', '../secrets/private_key.pem')
    signature = bytes_to_long(cryptographer.sign(data_bytes))
    print(type(signature))
    print('signature -- ', signature)
    signature = long_to_bytes(signature)
    print(cryptographer.verify(data_bytes, signature))
