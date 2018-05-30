__author__ = 'PentestLab.Net'
# -*- coding: utf-8 -*- 

import re
_re_IP = r'\d+\.\d+\.\d+\.\d+'
_re_startwithIP = r'^\d+\.\d+\.\d+\.\d+.*'
_re_networkc = r'^\d+\.\d+\.\d+'
_re_networkb = r'^\d+\.\d+'
_re_domain = r'\w+\.[\w+\.]+[a-zA-Z]+'
re_ip = re.compile(_re_IP)
re_startwithIP = re.compile(_re_startwithIP)
re_networkC = re.compile(_re_networkc)
re_networkB = re.compile(_re_networkb)
re_domain = re.compile(_re_domain)


def _ip2int(ip):
    return sum([256**j*int(i) for j,i in enumerate(ip.split('.')[::-1])])

def _int2ip(intip):
    return '.'.join([str(intip/(256**i)%256) for i in range(3,-1,-1)])

def _ip2networkC(ip):
    return re_networkC.findall(ip)[0]

def _ip2networkB(ip):
    return re_networkB.findall(ip)[0]

def _getIPinStr(string):
    ip = re_ip.findall(string)
    return ip

def _getDomainStr(string):
    domain = re_domain.findall(string)
    return domain

def _iprange2ipCB(iprange):
    ip_list = []
    if '-' in iprange:
        ip_tmp = iprange.split('-')
        net = re_network.findall(ip_tmp[0])[0]
        ip_strat = _ip2int(ip_tmp[0])
        ip_end = _ip2int(net+'.'+ip_tmp[1])
        for ip in range(ip_strat,ip_end+1):
            ip_list.append(_int2ip(ip))
        return ip_list
    if '/24' in iprange:
        ip_tmp = iprange.rstrip('/24')
        net = _ip2networkC(ip_tmp)
        for i in range(1,255):
            ip_list.append(net+'.'+str(i))
        return ip_list
    if '/16' in iprange:
        ip_tmp = iprange.rstrip('/16')
        net = _ip2networkB(ip_tmp)
        for i in xrange(1,65535):
            ip = _int2ip(_ip2int(net+'.0.0')+i)
            ip_list.append(ip)
        return ip_list
    return False


def ip_praserfromfile(file):
    _file = open(file,'r')
    target_list = []
    for line in _file.readlines():
        #for domain
        domain = _getDomainStr(line.strip())# return array 
        ip = _getIPinStr(line.strip())
        if domain:
            target_list.append(domain[0])
        elif ip:
            #for ip and ip range
            if '-' in line or '/24' in line or '/16' in line and _getIPinStr(line):
                list = _iprange2ipCB(line.strip())
                if list:
                    if len(list)>0:
                        target_list = target_list+list
            else:
                target_list.append(ip[0])
    return target_list   #   return   ip array 

def _ipStrip2(iplist,num=6):
    iplen = len(iplist)
    ip_list = []
    for i in xrange(0,iplen,iplen/num):
        ip_list.append(iplist[i:i+iplen/num])
    return ip_list

def quchong(results_list):
    s = []
    [ s.append(k) for k in results_list if k not in s ]
    return s
