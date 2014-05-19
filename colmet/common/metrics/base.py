# encoding: utf8 #
'''
This module contains the base class for the metrics that provide the
base functions to register/unregister counter and also pack/unpack data.
'''
from datetime import datetime
from colmet.common.exceptions import CounterAlreadyExistError, NoneValueError


import struct
import operator
import ctypes

######################
# Base counter types #
######################


class BaseType(object):
    struct_code = None
    length = None

    before_pack = lambda self, value: value
    after_unpack = lambda self, value: value

    def __eq__(self, other):
        return (self.struct_code == other.struct_code
                and self.length == other.length)


class UInt8(BaseType):
    struct_code = 'H'
    length = struct.calcsize("<%s" % struct_code)


class UInt16(BaseType):
    struct_code = 'H'
    length = struct.calcsize("<%s" % struct_code)


class UInt32(BaseType):
    struct_code = 'I'
    length = struct.calcsize("<%s" % struct_code)


class UInt64(BaseType):
    struct_code = 'Q'
    length = struct.calcsize("<%s" % struct_code)


class UFloat(BaseType):
    struct_code = 'f'
    length = struct.calcsize("<%s" % struct_code)


class UDouble(BaseType):
    struct_code = 'd'
    length = struct.calcsize("<%s" % struct_code)


class String(BaseType):
    def __init__(self, length):
        self.struct_code = '%ss' % length
        self.length = struct.calcsize("<%s" % self.struct_code)

    after_unpack = lambda self, value: value.rstrip("\0")


#####################
# Base metric class #
#####################


class MetaCountersType(type):
    '''
    This type handle the counters/headers registration for the metric. For each
    counter/header defined in the list _counters/_headers, it create a
    corresponding property and register their specifities for the class usage.
    '''

    '''
    Define the representation of the counters.
    '''
    _counter_representations = {
        'bytes': lambda value: "%s (bytes)" % MetaCountersType._normalize(value, 1024, 10000, ['', 'K', 'M', 'G', 'T']),
        'kbytes': lambda value: "%s (bytes)" % MetaCountersType._normalize(value, 1024, 10000, ['K', 'M', 'G', 'T']),
        "mbytes": lambda value: "%s (bytes)" % MetaCountersType._normalize(value, 1024, 10000, ['M', 'G', 'T']),
        "ts_date": lambda value: datetime.fromtimestamp(value).strftime("%d/%m/%Y - %H:%M:%S"),
        "sec": lambda value: "%s (seconds)" % str(value),
        "usec": lambda value: "%s (seconds)" % MetaCountersType._normalize(value, 1000, 1000, ['u', 'm', '']),
        "nsec": lambda value: "%s (seconds)" % MetaCountersType._normalize(value, 1000, 1000, ['n', 'u', 'm', '']),
        "count": lambda value: "%s (count)" % MetaCountersType._normalize(value, 1000, 10000, ['', 'K', 'M', 'G', 'T']),
        "mbytes-usec": lambda value: "%s (bytes*seconds)" % MetaCountersType._normalize(float(value * 1024 * 1024 / 1000 / 1000), 1024, 10000, [' ', 'K', 'M', 'G', 'T']),
        "n/a": lambda value: "%s" % str(value)
    }

    @staticmethod
    def _normalize(value, factor, limit, exts):
        '''
        Return the normalized 'value' according to 'factor', 'limit' and
        the extentions given in 'exts'. Until 'value' is bigger than 'limit',
        'value' is divided by 'factor'.
        '''
        exp = 0

        try:
            val = float(value)
        except  TypeError:
            # value is not available (in case of newly created cgroup with no tasks)
            raise NoneValueError

        while val > limit and exp < len(exts) - 1:
            val = val / factor
            exp += 1
        return "%.0f%s" % (val, exts[exp])

    '''
    The accumulation functions used for the counters. These functions
    takes 3 parameters: x, y and a coefficient.

    By default there are the functions:
    - 'add'  : x,y,coeff: y if x == None else x if y == None else x + coeff * y
    - 'none' : x,y,coeff -> y if x == None else y
    - 'min'  : x,y,coeff -> y if x == None else x if y == None else x if x < y else y
    - 'max'  : x,y,coeff -> y if x == None else x if y == None else x if x >= y else y
    '''
    _counter_accumulation_functions = {
        'add': lambda x, y, coeff: y if x is None else x if y is None else x + coeff * y,
        'none': lambda x, y, coeff: y if x is None else x,
        'min': lambda x, y, coeff: y if x is None else x if y is None else x if x < y else y,
        'max': lambda x, y, coeff: y if x is None else x if y is None else x if x >= y else y,
    }

    def __new__(cls, name, bases, attrs):
        if len(bases) > 1:
            raise TypeError("Counters cannot be derived from multiple class")

        attrs['_header_definitions'] = {}
        attrs['_counter_definitions'] = {}
        attrs['_fmt'] = None
        attrs['_counter_representations'] = MetaCountersType._counter_representations
        attrs['_counter_accumulation_functions'] = MetaCountersType._counter_accumulation_functions

        # Copy the header/counter definition from the parent class if
        # any
        if len(bases) == 1:
            parent_cls = bases[0]
            for key in ['_header_definitions', '_counter_definitions', '_fmt',
                        '_counter_represensations',
                        '_counter_accumulation_functions']:
                if hasattr(parent_cls, key):
                    parent_item = getattr(parent_cls, key)
                    if isinstance(parent_item, (dict, set)):
                        attrs[key] = parent_item.copy()
                    else:
                        attrs[key] = parent_item

        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        # Registering headers
        if '_headers' in attrs:
            for (h_name, h_type, h_repr) in attrs['_headers']:
                cls.registerHeader(h_name, h_type, h_repr)
                cls._set_header_property(h_name)

        # Registering counters
        if '_counters' in attrs:
            for c_name, c_type, c_repr, c_acc_fn, c_descr in attrs['_counters']:
                cls.registerCounter(c_name, c_type, c_repr, c_acc_fn, c_descr)
                cls._set_counter_property(c_name)

        return type.__init__(cls, name, bases, attrs)

    def _set_header_property(cls, name):
        '''
        Internal function to set the property setter/getter for a given header
        value
        '''
        fget = lambda t: t._get_header(name)
        fset = lambda t, value: t._set_header(name, value)
        setattr(cls, name, property(fget, fset))

    def _set_counter_property(cls, name):
        '''
        Internal function to set the property setter/getter for a given counter
        value
        '''
        fget = lambda t: t._get_counter(name)
        fset = lambda t, value: t._set_counter(name, value)
        setattr(cls, name, property(fget, fset))

    def registerCounter(cls, c_name, c_type, c_representation,
                        c_accumulate_function, c_descr, c_index=None):
        '''
        Register a counter for the given class.

        This method must be used as a class method when defining a derived
        class of BaseCounters
        '''
        if c_name in cls._counter_definitions or c_name in cls._header_definitions:
            raise CounterAlreadyExistError()

        if c_index is None:
            if len(cls._counter_definitions) > 0:
                c_index = 1 + max([index for (_, (_, _, _, _, index, _)) in
                                  cls._counter_definitions.iteritems()])
            else:
                c_index = 0

        cls._counter_definitions[c_name] = (
            c_type,
            c_representation,
            c_accumulate_function,
            c_descr,
            c_index,
            None
        )

        cls._updateStructFmt()

    def registerHeader(cls, h_name, h_type, h_representation, h_index=None):
        '''
        Register a header for the given class

        This method must be used as a class method when defining a derived
        class of BaseCounters
        '''
        if h_name in cls._header_definitions or h_name in cls._counter_definitions:
            raise CounterAlreadyExistError()

        if h_index is None:
            if len(cls._header_definitions) > 0:
                h_index = 1 + max([index for (_, (_, _, index, _))
                                  in cls._header_definitions.iteritems()])
            else:
                h_index = 0

        cls._header_definitions[h_name] = (
            h_type,
            h_representation,
            h_index,
            None
        )
        cls._updateStructFmt()

    def _updateStructFmt(cls):
        '''
        Internal method to update the struct format of the class.

        the struct format is computed from the _headers and _counters definitions.
        '''
        offset = 0
        sorted_hdef = sorted(cls._header_definitions.items(), key=lambda(k, v): v[2])
        for (h_name, (h_type, h_representation, h_index, _)) in sorted_hdef:
            cls._header_definitions[h_name] = (h_type, h_representation, h_index, offset)
            offset += h_type.length
        sorted_cdef = sorted(cls._counter_definitions.items(), key=lambda(k, v): v[4])
        for (c_name, (c_type, c_representation, c_acc_fn, c_descr, c_index, _)) in sorted_cdef:
            cls._counter_definitions[c_name] = (c_type, c_representation, c_acc_fn, c_descr, c_index, offset)
            offset += c_type.length

        sorted_hdef = sorted(cls._header_definitions.items(), key=lambda(k, v): v[2])
        header_fmt_list = [
            (h_name, h_type.struct_code)
            for (h_name, (h_type, _, _, _)) in sorted_hdef
        ]
        sorted_cdef = sorted(cls._counter_definitions.items(), key=lambda(k, v): v[4])
        counter_fmt_list = [
            (c_name, c_type.struct_code)
            for (c_name, (c_type, _, _, _, _, _)) in sorted_cdef
        ]

        h_key_list, h_fmt_code_list = zip(*header_fmt_list) if len(header_fmt_list) > 0 else ([], [])
        c_key_list, c_fmt_code_list = zip(*counter_fmt_list) if len(counter_fmt_list) > 0 else ([], [])

        cls._fmt = "<" + "".join(list(h_fmt_code_list)) + "".join(list(c_fmt_code_list))
        cls._fmt_length = struct.calcsize(cls._fmt)

        cls._fmt_header_ordered_keys = list(h_key_list)
        cls._fmt_counter_ordered_keys = list(c_key_list)


class BaseCounters(object):
    '''
    This class define the base class for a metric. It provides the basic
    functions for packing/unpacking, registering header/counter.

    The counters and headers are registered by adding an entry into
    the lists '_headers' and '_counters'.

    By default the headers contain the 'metric_backend', the 'hostname',
    the 'job_id', and the 'timestamp'.  '''

    __metaclass__ = MetaCountersType
    __metric_name__ = "base"
    _headers = [('metric_backend', String(255), 'string'),
                ('hostname', String(255), 'string'),
                ('job_id', UInt64(), 'count'),
                ('timestamp', UInt64(), 'count')]

    _counters = [
    ]

    ################
    # Static methods
    ################

    @staticmethod
    def create_metric_from_raw(raw):
        from . import get_counters_class
        backend = struct.unpack('255s', raw[0:255])[0].rstrip("\0")
        counters_class = get_counters_class(backend)
        counters = counters_class(raw=raw[0:counters_class._fmt_length])
        return counters

    @staticmethod
    def pack_from_list(counters_list):
        length = reduce(operator.add, [counters._fmt_length for counters in counters_list])
        raw = ctypes.create_string_buffer(length)

        offset = 0
        for counters in counters_list:
            new_offset = offset + counters._fmt_length
            counters.pack_into(raw, offset)
            offset = new_offset
        return raw

    @staticmethod
    def unpack_to_list(raw, unpack_counters=False):
        length = len(raw)
        offset = 0
        counters_list = list()
        while(offset < length):
            counters = BaseCounters.create_metric_from_raw(raw[offset:])
            offset += counters._fmt_length
            counters_list.append(counters)

        if unpack_counters:
            for counters in counters_list:
                counters.unpack()

        return counters_list

    #################
    # Class methods #
    #################
    @classmethod
    def get_zero_counters(cls, timestamp=None, *args):
        raise TypeError(
            "The metrics need to implement "
            "how to get zero counters"
        )

    @classmethod
    def fetch(cls, input_backend, timestamp, *args):
        raise TypeError(
            "The metrics need to implemend "
            "how to get counters"
        )

    ##################
    # Object methods #
    ##################
    #
    # Private object methods
    #
    def _is_buffer(self):
        return self._buf is not None

    def _create_buffer(self):
        self._buf = ctypes.create_string_buffer(self._fmt_length)
        return self._buf

    def _empty_fill(self):
        if self._packed:
            self._buf.raw.zfill(self._fmt_length)
        else:
            for c_name in self._counter_definitions.keys():
                self._set_counter(c_name, None)

    def _set_header(self, key, value):
        if self._packed:
            (h_type, _, _, h_offset) = self._header_definitions[key]
            struct.pack_into(h_type.struct_code, self._buf, h_offset, h_type.before_pack(value))
        else:
            self._header_values[key] = value

    def _get_header(self, key):
        if self._packed:
            (h_type, _, _, h_offset) = self._header_definitions[key]
            return h_type.after_unpack(struct.unpack_from(h_type.struct_code, self._buf, h_offset)[0])
        else:
            return self._header_values[key]

    def _get_counter(self, key):
        if self._packed:
            (c_type, _, _, _, _, c_offset) = self._counter_definitions[key]
            return c_type.after_unpack(struct.unpack_from(c_type.struct_code, self._buf, c_offset)[0])
        else:
            return self._counter_values[key]

    def _set_counter(self, key, value):
        if self._packed:
            (c_type, _, _, _, _, c_offset) = self._counter_definitions[key]
            struct.pack_into(c_type.struct_code, self._buf, c_offset, c_type.before_pack(value))
        else:
            self._counter_values[key] = value

    def __repr__(self):
        msg = "%s  Job(%s)/ %s -> Host(%s) -> %s" % (
            self.timestamp,
            self.job_id,
            self.metric_backend,
            self.hostname,
            self._format_counters()
        )
        return msg

    def _format_counters(self, prefix=""):
        '''
        Return a string formatted that represent the counters 'prefix' is inserted to the formatted string.
        '''
        msg_counters = {}
        key_maxlen = 0
        for key in self._counter_definitions.keys():
            if len(key) > key_maxlen:
                key_maxlen = len(key)
        msg_format_values = "\n\t" + prefix + "%" + str(key_maxlen) + "s : %s"
        for k in self._counter_definitions.keys():
            (_, c_repr, _, c_index, _, _) = self._counter_definitions[k]
            if not c_index in msg_counters:
                msg_counters[c_index] = ""

            msg_counters[c_index] += msg_format_values % (
                k,
                self._counter_representations[c_repr](self._get_counter(k))
            )
        sorted_msg = [msg_counters[k] for k in sorted(msg_counters.keys())]
        return (prefix + '{%s\n' + prefix + '}') % ("".join(sorted_msg))

    #
    # Public object methods
    #

    def get_metric_name(self):
        return self.__metric_name__

    def pack(self):
        '''
        Convert the data into the packed form
        '''
        if not self._is_buffer():
            self._create_buffer()

        self.pack_into(self._buf)
        self._packed = True

    def unpack(self):
        '''
        Convert the data into the unpacked form
        '''
        if not self._is_buffer():
            raise ValueError("The metric buffer should not be empty")

        self.unpack_from(self._buf)
        self._packed = False

    def pack_into(self, raw_buffer, offset=0):
        '''
        Convert the data into the packed form to a specific buffer
        '''

        fmt_values = ([self._header_definitions[key][0].before_pack(self._get_header(key)) for key in self._fmt_header_ordered_keys]
                      + [self._counter_definitions[key][0].before_pack(self._get_counter(key)) for key in self._fmt_counter_ordered_keys])
        struct.pack_into(self._fmt, raw_buffer, offset, *fmt_values)

    def unpack_from(self, raw_buffer, offset=0):
        '''
        Convert the data into the packed form from a specific buffer
        '''
        fmt_values = struct.unpack_from(self._fmt, raw_buffer, offset)
        index = 0
        for key in self._fmt_header_ordered_keys:
            self._header_values[key] = self._header_definitions[key][0].after_unpack(fmt_values[index])
            index += 1
        for key in self._fmt_counter_ordered_keys:
            self._counter_values[key] = self._counter_definitions[key][0].after_unpack(fmt_values[index])
            index += 1

    def get_packed(self):
        if not self._packed:
            self.pack()
        return self._buf[0:self._fmt_length]

    def __init__(self, raw=None):
        self._counter_values = {}
        self._header_values = {}
        if raw is not None:
            if len(raw) != self._fmt_length:
                raise ValueError(
                    "The buffer length (%s) given in parameters "
                    "must be the same size as the metric (%s)"
                    % (len(raw), self._fmt_length)
                )
            self._packed = True
            self._buf = ctypes.create_string_buffer(raw)
        else:
            self._packed = False
            self._buf = None
            self.metric_backend = self.get_metric_name()

    def accumulate(self, other_stats, destination, coeff=1):
        """Update destination from operator(self, other_stats)"""
        for counters in [self, other_stats, destination]:
            if counters._packed:
                counters.unpack()

        d_counters = destination._counter_values
        o_counters = other_stats._counter_values
        s_counters = self._counter_values
        for (name, (_, _, acc_fn, _, _, _)) in self._counter_definitions.iteritems():
            d_counters[name] = \
                self._counter_accumulation_functions[acc_fn](s_counters[name],
                                                             o_counters[name],
                                                             coeff)

    def delta(self, other_stats, destination):
        """Update destination with self - other_stats"""
        return self.accumulate(other_stats, destination, coeff=-1)
