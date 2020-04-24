# -*- coding: utf-8 -*-

"""
IP地址离线解析
"""

from __future__ import absolute_import
import sys
import socket
import codecs
import mmap
from struct import pack, unpack

if 'ahi_stdout' not in dir():
    ahi_stdout = sys.stdout
    reload(sys)
    sys.setdefaultencoding("utf-8")
    sys.stdout = ahi_stdout


class DeriveIp():
    
    def __init__(self, filepath):
        self.ip_database = IPSeeker(filepath) 
        
    def derive(self, ip):
        city, carrier = self.ip_database.query(ip)
        return self.city_to_normal(city.decode('utf-8')), carrier.decode('utf-8')

    def city_to_normal(self, value):
        """ 城市名称转换"""

        beijing = u"北京"
        shanghai = u"上海"
        tianjin = u"天津"
        chongqing = u"重庆"
        xianggang = u"香港"
        aomen = u"澳门"
        taiwan = u"台湾"
        inner_mongolia = u"内蒙古"
        xinjiang = u"新疆"
        guangxi = u"广西"
        ningxia = u"宁夏"
        xizang = u"西藏"

        # 市 级别的结束词
        shi = u"市"
        shi_suffix = [u"市", u"地区", u"盟", u"州", u"县"]  # 有个别县是省直属的，比如 海南省陵水县

        # 省 级别的结束词 ipseeker中自动过滤掉了 自治区、特别行政区等词，所以只有“省”
        sheng = u"省"

        def get_shi(s):
            """ 
            根据地址字符串挑选出城市名
            s: 已去掉省相关的头部字符串
            """
            for suffix in shi_suffix:
                if suffix in s:
                    return s.split(suffix)[0]
            return s

        if value is None:
            return ''

        if value.startswith(beijing) \
                or value.startswith(shanghai) \
                or value.startswith(tianjin) \
                or value.startswith(chongqing) \
                or value.startswith(xianggang) \
                or value.startswith(aomen) \
                or value.startswith(taiwan):

            ret = value[:len(beijing)]

        elif value.startswith(inner_mongolia) \
                or value.startswith(xinjiang) \
                or value.startswith(guangxi) \
                or value.startswith(ningxia) \
                or value.startswith(xizang):

            if value.startswith(inner_mongolia):
                ret = get_shi(value[len(inner_mongolia):])

            else:
                ret = get_shi(value[len(xinjiang):])
        elif sheng in value:
            sub_city = value.split(sheng)[1]
            ret = get_shi(sub_city)
        else:
            ret = value

        return ret
    
def decode_str(old):
    """
    解码函数
    """
    try:
        return unicode(old, 'gbk').encode('utf-8')
    except:
        if old[-1] == '\x96':
            try:
                return unicode(old[:-1], 'gbk').encode('utf-8') + '?'
            except:
                pass
        return 'Invalid'


class IPSeeker(object):
    """ 
    解析IP地址的数据集
    """

    def __init__(self, path):
        self.path = path
        self.db = None
        self.open_db()
        self.idx_start, self.idx_end = self._read_idx()
        self.total = (self.idx_end - self.idx_start) / 7 + 1

    def open_db(self):
        if not self.db:
            self.db = open(self.path, 'rb')
            self.db = mmap.mmap(self.db.fileno(), 0, access = 1)
        return self.db

    def _read_idx(self):
        self.db.seek(0)
        start = unpack('I', self.db.read(4))[0]
        end = unpack('I', self.db.read(4))[0]
        return start, end

    def version(self):
        ip_end_offset = self.read_offset(self.idx_end + 4)
        a_raw, b_raw = self.read_record(ip_end_offset+4)
        return decode_str(a_raw + b_raw)

    def read_ip(self, off, seek=True):
        if seek:
            self.db.seek(off)
        buf = self.db.read(4)
        return unpack('I', buf)[0]

    def read_offset(self, off, seek=True):
        if seek:
            self.db.seek(off)
        buf = self.db.read(3)
        return unpack('I', buf+'\0')[0]

    def read_string(self, offset):
        if offset == 0:
            return 'N/A1'
        flag = self.get_flag(offset)
        if flag == 0:
            return 'N/A2'
        elif flag == 2:
            offset = self.read_offset(offset+1)
            return self.read_string(offset)
        self.db.seek(offset)
        raw_string  = ''
        while True:
            x = self.db.read(1)
            if x == '\0':
                break
            raw_string += x
        return raw_string

    def get_flag(self, offset):
        self.db.seek(offset)
        c = self.db.read(1)
        if not c:
            return 0
        return ord(c)

    def read_record(self, offset):
        self.db.seek(offset)
        flag = ord(self.db.read(1))

        if flag == 1:
            buf = self.db.read(3)
            a_offset = unpack('I', buf+'\0')[0]
            a_raw = self.read_string(a_offset)
            a_flag = self.get_flag(a_offset)
            if a_flag == 2:
                b_raw = self.read_string(a_offset+4)
            else:
                b_raw = self.read_string(a_offset+len(a_raw)+1)
        elif flag == 2:
            buf = self.db.read(3)
            a_offset = unpack('I', buf+'\0')[0]
            a_raw = self.read_string(a_offset)
            b_raw = self.read_string(offset+4)
        else:
            a_raw = self.read_string(offset)
            b_raw = self.read_string(offset+len(a_raw)+1)
        return a_raw, b_raw

    def output(self, output_file='ip.txt'):
        fp = codecs.open(output_file, 'w', 'utf8')
        idx = self.idx_start
        while idx <= self.idx_end:
            ip_int = self.read_ip(idx)
            ip_start = socket.inet_ntoa(pack('!I', ip_int))
            ip_end_offset = self.read_offset(idx + 4)

            ip_int = self.read_ip(ip_end_offset)
            ip_end = socket.inet_ntoa(pack('!I', ip_int))

            a_raw, b_raw = self.read_record(ip_end_offset+4)

            a_info = decode_str(a_raw)
            b_info = decode_str(b_raw)

            fp.write(u'%15s\t%15s\t%s,%s\n' %(
                ip_start, ip_end,
                a_info.decode('utf8'), b_info.decode('utf8')))
            idx += 7
        fp.close()

    def find(self, ip, l, r):
        if r - l <= 1:
            return l
        m = (l + r) / 2
        offset = self.idx_start + m * 7
        new_ip = self.read_ip(offset)
        if ip < new_ip:
            return self.find(ip, l, m)
        else:
            return self.find(ip, m, r)

    def query(self, ip):
        ip = unpack('!I', socket.inet_aton(ip))[0]
        i = self.find(ip, 0, self.total - 1)
        o = self.idx_start + i * 7
        o2 = self.read_offset(o + 4)
        (c, a) = self.read_record(o2 + 4)
        return decode_str(c), decode_str(a)

    def __del__(self):
        if self.db:
            self.db.close()



class IPSeekerInstance(object):
    """ 
    单例模式，为了使spark能够序列化
    """
    @classmethod
    def get_instance(cls, database_path):
        if not hasattr(cls, '_instance'):
            cls._instance = IPSeeker(database_path)
        return cls._instance


