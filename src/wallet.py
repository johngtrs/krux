# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
try:
    import ujson as json
except ImportError:
    import json
from ur.ur import UR
from embit.descriptor.descriptor import Descriptor
from embit.descriptor.arguments import Key, KeyHash, AllowedDerivation
import urtypes

class Wallet:
    """Represents the wallet that the current key belongs to"""

    def __init__(self, key):
        self.key = key
        self.wallet_data = None
        self.wallet_qr_format = None
        self.descriptor = None
        self.label = None
        self.policy = None
        if not self.key.multisig:
            self.descriptor = Descriptor.from_string('wpkh(%s/{0,1}/*)' % self.key.xpub_btc_core())
            self.label = ( 'Single-key' )
            self.policy = { 'type': self.descriptor.scriptpubkey_type() }

    def is_multisig(self):
        """Returns a boolean indicating whether or not the wallet is multisig"""
        return self.key.multisig

    def is_loaded(self):
        """Returns a boolean indicating whether or not this wallet has been loaded"""
        return self.wallet_data is not None

    def load(self, wallet_data, qr_format):
        """Loads the wallet from the given data"""
        descriptor, label = parse_wallet(wallet_data)

        if self.is_multisig():
            if not descriptor.is_basic_multisig:
                raise ValueError('not multisig')
            if self.key.xpub() not in [key.key.to_base58() for key in descriptor.keys]:
                raise ValueError('xpub not a cosigner')
        else:
            if not descriptor.key:
                raise ValueError('not single-key')
            if self.key.xpub() != descriptor.key.key.to_base58():
                raise ValueError('xpub does not match')

        self.wallet_data = wallet_data
        self.wallet_qr_format = qr_format
        self.descriptor = descriptor
        self.label = label

        if self.descriptor.key:
            # If child derivation info is missing to generate receive addresses,
            # use the default scheme
            if isinstance(self.descriptor.key, (Key, KeyHash)):
                if self.descriptor.key.allowed_derivation is None:
                    self.descriptor.key.allowed_derivation = AllowedDerivation.default()
            if not self.label:
                self.label = ( 'Single-key' )
            self.policy = { 'type': self.descriptor.scriptpubkey_type() }
        else:
            # If child derivation info is missing to generate receive addresses,
            # use the default scheme
            for i in range(len(self.descriptor.miniscript.args)):
                key = self.descriptor.miniscript.args[i]
                if isinstance(key, (Key, KeyHash)):
                    if key.allowed_derivation is None:
                        key.allowed_derivation = AllowedDerivation.default()

            m = int(str(self.descriptor.miniscript.args[0]))
            n = len(self.descriptor.keys)
            cosigners = [key.key.to_base58() for key in self.descriptor.keys]
            if self.descriptor.is_sorted:
                cosigners = sorted(cosigners)
            if not self.label:
                self.label = ( '%d of %d multisig' ) % (m, n)
            self.policy = {
                'type': self.descriptor.scriptpubkey_type(),
                'm': m,
                'n': n,
                'cosigners': cosigners
            }

    def wallet_qr(self):
        """Returns the original wallet data and qr format for display back as a QR code"""
        return (self.wallet_data, self.wallet_qr_format)

def parse_wallet(wallet_data):
    """Exhaustively tries to parse the wallet data from a known format, returning
       a descriptor and label if possible.

       If the descriptor cannot be derived, an exception is raised.
    """
    if isinstance(wallet_data, UR):
        # Try to parse as a Crypto-Output type
        try:
            output = urtypes.crypto.Output.from_cbor(wallet_data.cbor)
            return Descriptor.from_string(output.descriptor()), None
        except:
            pass

        # If a generic UR bytes object was sent, extract the data for further processing
        try:
            wallet_data = urtypes.Bytes.from_cbor(wallet_data.cbor).data
        except:
            pass

    # Process as a string
    wallet_data = wallet_data.decode() if not isinstance(wallet_data, str) else wallet_data

    # Try to parse as JSON and look for a 'descriptor' key
    try:
        wallet_json = json.loads(wallet_data)
        if 'descriptor' in wallet_json:
            descriptor = Descriptor.from_string(wallet_json['descriptor'])
            label = wallet_json['label'] if 'label' in wallet_json else None
            return descriptor, label
    except:
        pass

    # Try to parse as a key-value file
    try:
        key_vals = []
        for word in wallet_data.split(':'):
            for key_val in word.split('\n'):
                key_val = key_val.strip()
                if key_val != '':
                    key_vals.append(key_val)

        if len(key_vals) > 0:
            script = key_vals[key_vals.index('Format') + 1].lower()
            if script != 'p2wsh':
                raise ValueError('invalid script type: %s' % script)

            policy = key_vals[key_vals.index('Policy') + 1]
            m = int(policy[:policy.index('of')].strip())
            n = int(policy[policy.index('of')+2:].strip())

            keys = []
            for i in range(len(key_vals)):
                xpub = key_vals[i]
                if xpub.lower().startswith('xpub') or xpub.lower().startswith('tpub'):
                    fingerprint = key_vals[i-1]
                    keys.append((xpub, fingerprint))

            if len(keys) != n:
                raise ValueError('expected %d keys, found %d' % (n, len(keys)))

            derivation = key_vals[key_vals.index('Derivation') + 1]

            keys.sort()
            keys = ['[%s/%s]%s' % (key[1], derivation[2:], key[0]) for key in keys]

            descriptor = Descriptor.from_string(('wsh(sortedmulti(%d,' % m) + ','.join(keys) + '))')
            label = key_vals[key_vals.index('Name') + 1] if key_vals.index('Name') >= 0 else None
            return descriptor, label
    except:
        pass

    raise ValueError('invalid wallet format')
