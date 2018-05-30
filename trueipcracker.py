# -*- coding: utf-8 -*- 
__author__ = 'jack & pentestlab.net'

import socket
import sys
import IP
import threadpool
import os
import time
import datetime
import requests
import re
from threading import *
screenLock = Semaphore(value=1)

socket.setdefaulttimeout(5)
__http_header = u'''\
GET {url} HTTP/1.1\r\n\
Host: {host}\r\n\
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n\
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36\r\n\
Accept-Language: zh-CN,zh;q=0.8\r\n\r\n
'''

max_t = 10
lines=0
doamin_list =[]

if os.path.exists('getIP.txt'):
    os.remove('getIP.txt')


def x2Unicode(d, charset=None):
    udata = ''
    if isinstance(d, str):
        if not charset:
            try:
                charset = chardet.detect(d).get('encoding')
            except:
                pass
        if charset:
            udata = d.decode(charset, 'ignore')
        else:
            udata = d
    elif isinstance(d, unicode):
        udata = d
    else:
        return (None, charset)

    return (udata, charset)

def is_reg(re_data,reg_good):
    re_data, code = x2Unicode(re_data)
    if reg_good in re_data:
        return True

def get_iplist(ip_path):
    _f = open(ip_path,'r')
    return _f.readlines()

def Check(host,port,send_data_whole,reg_good):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    str_buf =''
    try:
        s.connect((host,port))
        s.send(send_data_whole)
        f = s.makefile('rw', bufsize=0)
        str_buf = f.read(8094)
        #print host
        #print str_buf
    except Exception as e:
        #print e.message
        return 0
    if is_reg(str_buf,reg_good):
        return 1
    else:
        return 0

def get(host,port,data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    str_buf =''
    #print host
    #print data
    try:
        s.connect((host,port))
        s.send(data)
        f = s.makefile('rw', bufsize=0)
        str_buf = f.read(8094)
        #print str_buf
        return str_buf
    except Exception as e:
        print e.message
        exit()

def get_title(domain):
    domain_t = IP._getDomainStr(domain)
    #print domain_t   

    # 根据传递进来的 domain 获取    首先直接打开网站获取到 title 然后再去修改 header的值 去对比titie
    # 如果网站本来就打不开呢 打得开 获取 title  打不开直接 输出title
    try:
        http_domain = u'http://'+unicode(domain_t[0])
        u = u'('+http_domain+'.*?)"'
        u2 = u''+http_domain+u'(.*)'
        t = u'<title>.*</title>'
        _re_title = re.compile(t)
        _re_url = re.compile(u2)
        abc = 'http://'+domain.strip()
        r = requests.get(abc,verify=False,allow_redirects=True)
        url = _re_url.findall(r.url)[0]
        get1 = _re_url.findall('http://'+domain)[0]
        if get1 =='':
            get1 = '/'
        r1 = get(domain_t[0],80,__http_header.replace('{host}',domain_t[0]).replace('{url}',get1))
        r2,code = x2Unicode(r1) 
        title = _re_title.findall(r2)[0]
        print 'Get key words:\n"'+title.decode('utf-8')+'"'
        u_title,code = x2Unicode(title)
        return url,u_title,domain_t[0]
    except Exception as a:
        print a.message
        #return url,'1',domain_t[0]
        return 0

def run(task):
    screenLock.acquire()
    print '['+task[0]+'---'+task[4]+'] is checking...'
    screenLock.release()
    if Check(task[0],task[1],task[2],task[3]):
        _f = open('getIP_'+task[4]+'.txt','a+')
        ture_ip.append(task[0])
        _f.write(task[4]+'  '+task[0].strip()+'\n')
        _f.close()
        screenLock.acquire()
        print 'find ture IP...'
        screenLock.release()
ture_ip = []

def useage():
    if len(sys.argv)!=4 :
        if len(sys.argv)==3:
            pass
        else:
            print '------------------------------------------------------------------'
            print '# useage:                                                        #'
            print '# python trueIPcrack.py domain.txt iplist.txt thread_num         #'
            print '------------------------------------------------------------------'
            exit()
    if len(sys.argv)==4 :
        global max_t
        max_t = int(sys.argv[3])

def getlinescountstrip(filepath):
    global lines
    thefile=open(filepath)
    line=thefile.readline().strip('\n').strip('\r')
    while line:
        doamin_list.append(line)
        line=thefile.readline().strip('\n').strip('\r')
        lines=lines+1
    thefile.close()


if __name__ == '__main__':
    _start_time = datetime.datetime.now()
    useage()
    print '\n start checking......\n'
    getlinescountstrip(sys.argv[1])
    for domain in doamin_list:
        ture_ip = []
        print domain
        try:
            url,title,domain_t = get_title(domain=domain.strip())
        except:
            print 'get keyword erro,exit...'
            continue
        pool = threadpool.ThreadPool(max_t) 
        task_list = [] 
        iplist = IP.ip_praserfromfile(sys.argv[2]) 
        print '\n Find '+str(len(iplist))+' ip(s) check ...\n'
        print 'If find true ip,"getIp_[doamin].txt" will create current floder.\n'
        time.sleep(3)
        task_list =[]

        for ip in iplist:
            task_list.append([ip,80,__http_header.replace('{host}',domain_t).replace('{url}',url),title,domain_t])
        fuck = threadpool.makeRequests(run, task_list) 
        [pool.putRequest(req) for req in fuck] 
        pool.wait() 
        _end_time = datetime.datetime.now()
        print '------------------------------------------------------------------'
        print '#task finished... please check the getIP.txt to find the results'
        print '#the ture IP is '+ str(ture_ip)
        print '#It takes '+str((_end_time-_start_time).seconds)+'.'+str((_end_time-_start_time).microseconds)+' s'
        print '------------------------------------------------------------------'
