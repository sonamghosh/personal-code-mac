import queue
import codecs
import hashlib
import json
import base64
from collections import OrderedDict
from operator import itemgetter

class MessageService:
    def __init__(self):
        # Hold the name of the sequence and queue for the msgs
        self.seq_info = {}
        # Messages that are in the wait queue for enqueueing
        self.seq_msgs = []
        # The 5 msg output queues
        self.msg_queues = [queue.Queue() for i in range(5)]


    def encode_str(self, val):
        """
        @brief - Base64 utf-8 Sha256 encodes a string value

        @param val (str) - String value present in the _hash field
        that will be encoded
        """
        # Base64 utf-8 Encode
        utf8_base64_encoded = base64.encodebytes(val.encode('utf-8'))
        # sha256 hash
        hashed_str = hashlib.sha256(utf8_base64_encoded).hexdigest()
        return hashed_str


    def transform(self, msg):
        """
        @brief Follows the transformation rules for dealing with a msg
        dictionary in the queues. Rules are applied in order.

        @param msg (dict) - Message dictionary in the queue which contains
        essential fields and values for transformation
        """
        for field, val in msg.items():
            # Ignore private fields (start with _) except '_hash'
            if not field.startswith('_'):
                # Reverse val if 'Qadium' in value of some field
                if isinstance(val, str) and 'Qadium' in val:
                    msg[field] = val[::-1]
                # Replace integer values with bitwise negation of value
                elif isinstance(val, int):
                    msg[field] = ~val
            # Use the @m encode_str method to generate a 'hash' field with encoded value
            if '_hash' in field:
                enc_val = self.encode_str(val)
                # Throw exception if hash exists already and the value is different from the hashed value from before
                if field == 'hash':
                    if msg['hash'] != enc_val:
                        raise Exception('Hash values are different')
                msg['hash'] = enc_val

        return msg

    def dispatch(self, msg):
        """
        @brief Given five output queues 0 to 4, this method decides which queue
        gets a msg based on various rules followed in order.

        Field containing '_special' -> Queue 0
        Field containing 'hash' -> Queue 1
        Field with value 'muidaQ' -> Queue 2
        Field with a integer value -> Queue 3
        Otherwise -> Queue 4

        @param msg (dict) - Message dictionary with the field and value information

        Note: Ignore values of private fields (starts with '_')
        """

        if '_special' in msg:
            return 0
        elif 'hash' in msg:
            return 1
        else:
            for field, val in msg.items():
                # Ignore values with private fields
                if not field.startswith("_"):
                    if isinstance(val, str) and 'muidaQ' in val:
                        return 2
                    elif isinstance(val, int):
                        return 3
        # Otherwise
        return 4


    def enqueue_sequence(self, msg):
        """
        @brief Searches for the _sequence field and _part field for msg num
        and applies dispatch rules based on the first msg in a sequence
        and applies transformation rules to the other messages

        """
        seq_name = msg['_sequence']
        # Check for first msg in sequence
        if msg['_part'] == 0:
            # Apply dispatch rules to first msg
            queue_num = self.dispatch(msg)
            # Add to dict
            self.seq_dict = {seq_name: {'route': queue_num,
                                        'last': 0}}
            # Send enqueued msg to correct queue
            self.msg_queues[queue_num].put(json.dumps(msg))
        # Otherwise send to front of output queue
        else:
            self.seq_msgs.append(msg)

        # Search list for next msg in sequence
        self.seq_msgs.sort(key=itemgetter('_sequence', '_part'), reverse=True)
        for i in reversed(range(len(self.seq_msgs))):
            # search for routing info
            if seq_name in self.seq_dict:
                if self.seq_msgs[i].get('_sequence') == seq_name and self.seq_msgs[i].get('_part') == self.seq_dict[seq_name]['last']+1:
                    # enqueue
                    self.msg_queues[self.seq_dict[seq_name]['route']].put(json.dumps(self.seq_msgs.pop(i)))
                    # Update last queued msg in sequence
                    self.seq_dict[seq_name]['last'] += 1

    def enqueue(self, msg):
        # msg as JSON obj
        msg = json.loads(msg, object_pairs_hook=OrderedDict)
        # Apply transformation rules
        transformed_msg = self.transform(msg)
        if '_sequence' in transformed_msg:
            self.enqueue_sequence(transformed_msg)
        else:
            # Apply dispatch rules
            queue_num = self.dispatch(transformed_msg)
            queued_msg = json.dumps(transformed_msg)
            # Enqueue msg
            self.msg_queues[queue_num].put(queued_msg)

    def next(self, queue_num):
        return self.msg_queues[queue_num].get(block=False)


def get_message_service():
    return MessageService()
