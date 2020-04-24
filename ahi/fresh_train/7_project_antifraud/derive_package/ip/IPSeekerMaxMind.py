# -*- coding:utf-8 -*-

"""
国外ip地址解析
"""

# import os
import geoip2.database


class IPSeekerMaxMind(object):
    """
        Seeking ip in geoip2.database
    """
    def __init__(self, db_path):
        self.reader = geoip2.database.Reader(db_path)

    def get_response(self, ip):
        return self.reader.city(ip)

    def get_country_iso_code(self, ip):
        response = self.get_response(ip)
        return response.country.iso_code

    # 获取城市名称
    def get_city_name(self, ip):
        response = self.get_response(ip)
        return response.city.name

    # 获取城市的中文名称
    def get_city_cn_name(self, ip):
        response = self.get_response(ip)
        return response.city.names['zh-CN']

    # 获取国家名称
    def get_country_name(self, ip):
        response = self.get_response(ip)
        return response.country.name

    # 获取国家的中文名称
    def get_country_cn_name(self, ip):
        response = self.get_response(ip)
        return response.country.names['zh-CN']

    # 获取经纬度，返回(经度，纬度)
    def get_location_long_lat(self, ip):
        response = self.get_response(ip)
        return response.location.longitude, response.location.latitude

    # 同时获取(国家, 城市, 经度, 纬度)
    def get_common_info(self, ip):
        response = self.get_response(ip)
        country = response.country.name
        city = response.city.name
        longitude = response.location.longitude
        latitude = response.location.latitude
        return country, city, longitude, latitude

    def __del__(self):
        if self.reader:
            self.reader.close()