#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#author:fugui

'''
cron: 0 11,14,17,21,0,1,2,3 * * *
new Env('美团');
此脚本只是搬运修改，方便青龙，v4等使用
请支持脚本作者：https://github.com/fuguiKz/meituan-shenquan
美团token获取教程：https://github.com/fuguiKz/meituan-shenquan
变量解释：https://github.com/fuguiKz/meituan-shenquan
# 11 10 22:00 应要求更改cdn

环境变量填写，环境变量优先
export meituan_token=""     # 美团token       
export meituan_wm_latitude=""       # 去除小数点的纬度(如30657401)
export meituan_wm_longitude=""      # 去除小数点的经度(如104065827)
export meituan_propId=""        # 所需要兑换道具的propId(推荐填写5)
export meituan_exchangeCoinNumber=""        # propId对应某类必中符所需的豆子数量(推荐填写1800)
在原脚本的基础上支持了多种推送方式  34.266009, 117.213988
通知推送服务环境变量请查看：https://github.com/wuye999/myScripts/blob/main/send.md
'''

# 脚本内填写，填了环境变量就不用填脚本内的，都填了则优先使用环境变量
meituan_token=""     # 美团token       
meituan_wm_latitude="34266009"       # 去除小数点的纬度(如30657401)
meituan_wm_longitude="117213988"      # 去除小数点的经度(如104065827)
meituan_propId="5"        # 所需要兑换道具的propId(推荐填写5)
meituan_exchangeCoinNumber="1800"        # propId对应某类必中符所需的豆子数量(推荐填写1800)
# 在原脚本的基础上支持了多种推送方式
# 通知推送服务环境变量请查看：https://github.com/wuye999/myScripts/blob/main/send.md
# 填写在脚本内则去掉export 

import sys
sys.path.append('../../tmp')
from typing import Text
import urllib.request
import ssl
import json
import os
import re
import time
import datetime


## 获取通知服务
class Msg(object):
    def getsendNotify(self, a=1):
        try:
            url = 'https://mirror.ghproxy.com/https://raw.githubusercontent.com/acoolbook/scripts/main/sendNotify.py'
            response = requests.get(url,timeout=3)
            with open('sendNotify.py', "w+", encoding="utf-8") as f:
                f.write(response.text)
            return
        except:
            pass
        if a < 5:
            a += 1
            return self.getsendNotify(a)

    def main(self,f=1):
        global send,msg,initialize
        sys.path.append(os.path.abspath('.'))
        for n in range(3):
            try:
                from sendNotify import send,msg,initialize
                break
            except:
                self.getsendNotify()
        l=['BARK','SCKEY','TG_BOT_TOKEN','TG_USER_ID','TG_API_HOST','TG_PROXY_HOST','TG_PROXY_PORT','DD_BOT_TOKEN','DD_BOT_SECRET','Q_SKEY','QQ_MODE','QYWX_AM','PUSH_PLUS_TOKEN','PUSH_PLUS_USER']
        d={}
        for a in l:
            try:
                d[a]=eval(a)
            except:
                d[a]=''
        try:
            initialize(d)
        except:
            self.getsendNotify()
            if f < 5:
                f += 1
                return self.main(f)
            else:
                print('获取通知服务失败，请检查网络连接...')
Msg().main()   # 初始化通知服务   


# 读取环境变量
def get_env(env):
    try:
        if env in os.environ:
            a=os.environ[env]
        elif '/ql' in os.path.abspath(os.path.dirname(__file__)):
            try:
                a=v4_env(env,'/ql/config/config.sh')
            except:
                a=eval(env)
        elif '/jd' in os.path.abspath(os.path.dirname(__file__)):
            try:
                a=v4_env(env,'/jd/config/config.sh')
            except:
                a=eval(env)
        else:
            a=eval(env)
    except:
        a=''
    return a

# v4
def v4_env(env,paths):
    b=re.compile(r'(?:export )?'+env+r' ?= ?[\"\'](.*?)[\"\']', re.I)
    with open(paths, 'r') as f:
        for line in f.readlines():
            try:
                c=b.match(line).group(1)
                break
            except:
                pass
    return c 
    

#定义11点  用于开启server 酱推送
global d_time0,d_time1,d_time2,n_time
d_time0 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '11:00', '%Y-%m-%d%H:%M')


n_time = datetime.datetime.now()


#定义抢大额红包时间段d_time3和d_time4和d_time5和d_time6之间 ，d_time4提前11分钟意在防止下午红包池提前10分钟关闭和脚本抢大额红包有些地区到最后一刻10元以上红包都有剩余导致脚本报错，
# 若到最后一刻会自动放弃监测，抢所拥有的必中符的面值保底
###默认 抢大额(15元以上) 时间段为下午17:00点到16:49分和晚上21:00到23点59分   不建议进行更改
##以下默认中午试图抢大额红包 前提是道具库存中有10元以上必中符！！！！！！！！！

global d_time3,d_time4,d_time5,d_time6

d_time3 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '17:00', '%Y-%m-%d%H:%M')
d_time4 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '20:49', '%Y-%m-%d%H:%M')

d_time5 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '21:00', '%Y-%m-%d%H:%M')
d_time6 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:59', '%Y-%m-%d%H:%M')


#d_time6定义几点前不使用必中符,注意是不使用！！！若时间定义为17:00点,也就是17:00点之前的抽奖不会使用必中符,优先级高于自定义的大额抢红包时间,以节约道具库中的有效的必中符
##若d_time6定义为11:00点，则代表不对使用必中符时间进行限制，切记不能删除d_time7，若不需限制，只需将d_time7时间改为11:00,注意是英文的冒号
global d_time7
d_time7 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '11:00', '%Y-%m-%d%H:%M')


 #关闭ssl校验，用于抓包调试请求
ssl._create_default_https_context = ssl._create_unverified_context

#定义短期(半年以上)不会变的量
parActivityId="Gh1tkq-wvFU2xEP_ZPzHPQ"
wm_ctype="mtandroid"
#以下portraitId参数含义未知，用于每日浏览天天神卷30s后可领30豆的请求
portraitId=498



#定义精简通用请求头部
head={"Host": "i.waimai.meituan.com","User-Agent":"MeituanGroup/11.9.208","x-requested-with": "XMLHttpRequest","content-type":"application/x-www-form-urlencoded"} 
#定义美团外卖服务器地址
baseurl=r"https://i.waimai.meituan.com"
#定义 pushPlus 的webhook地址，用于企业微信等渠道的推送，默认为空，若采用企业微信，请手动填写
global webhook
webhook = ""

#定义全局变量并初始化 以下初始化赋值的变量不要改！！！！
global propIdforuse
showPriceNumber = "1"
wm_latitude =1.0
wm_longitude=1.0
token =""
propId=1
exchangeCoinNumber=1.0
serverkey=""
pushPlusToken = ""
yesornot = ""
yesornot2 = ""
propIdforuse =2
cwd = os.path.dirname(os.path.realpath(__file__))

##############################################################################
##标记这四类红包数量不为空，用来在有10元以上必中符时循环判断红包池余量抢购大额元红包，若您不需该功能，请自行将下一行的1改为0
eight = ten = fifteen = thirty =fifty=1
##############################################################################
# eight_left= 10
################################################################################
#若在您自定义的抢大额红包时间段中，您无法通过10元以上必中符抢到任何红包！！，则请将下面两行数值改大些，如改成10左右的数字
ten_left=0
fifteen_left=0
thirty_left=0
fifty_left=0

#定义一个云端查询必中符库中所有的propId 和needNumber 的函数，并传给getpropId_Coninnumber()函数作为用户输入参考提示
def myredbean(token):
    wm_latitude = 1
    wm_longitude = 1
    msg("开始执行从美团接口查询proid 和 needNumber参数脚本:\n")
    datas = "parActivityId="+parActivityId+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+str(token)+"&userPortraitId="+str(portraitId)
    url_drawlottery = baseurl+r"/cfeplay/playcenter/batchgrabred/myRedBean"
    request =urllib.request.Request(url_drawlottery,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        cent = 1
        if(result2["code"]==0 and result2["subcode"]==0 and len(result2["data"]["propExchangeRuleInfos"])):
            for k in result2["data"]["propExchangeRuleInfos"]:
                msg("第%d类必中符 所需设置propId参数为%d\t所需红包豆数量为:%d\t总量为%d\n"%(cent,k["propId"],k["needNumber"],k["amount"]))
                cent=cent+1
            msg("一般这几类必中符金额依次为5元 8元 15元,大概率使用后兑换到20-5，25-8,40-15的红包，建议选择面值最大的一类,即propId填5,所需豆子数量填1800即可\n脚本会自动从设定的面值去尝试兑换，逐级尝试面值，直到兑换成功，所以推荐设置默认兑换15面值的必中符\n注意填写的propId和所需豆子数之间是上方的一一对应关系，错误对应将导致兑换失败!\n")
        elif (result2["code"]==1 and result2["subcode"]==-1):
            msg("%s,原因:输入token失效或错误 请继续运行程序并输入，脚本将在运行一遍后自动删除异常配置文件!!\n"%(result2["msg"]))
        else:
            msg("请求接口失效或参数异常，建议🙏重置参数!\n")
            send('### 美团 ###')   # 启用通知服务
            sys.exit(0)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            msg(e,"reason")


#定义从文本文件中获取存入变量的函数,第二次运行时不用输入，若需改变经纬度和token，则直接删除文件即可
def getVar():
    wm_latitude  = int(get_env('meituan_wm_latitude'))
    wm_longitude = int(get_env('wm_longitude'))
    token  = get_env('meituan_token')
    propId  = get_env('meituan_propId')
    exchangeCoinNumber = get_env('meituan_exchangeCoinNumber')
    return wm_latitude,wm_longitude,token,propId,exchangeCoinNumber

    
#定义获取batchId的函数
def getbatchId(token):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**开始执行获取batchId脚本:**\n")
    datas = "parActivityId="+parActivityId+"&wm_ctype="+wm_ctype+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+token
    url_getbatchId = baseurl+r"/cfeplay/playcenter/batchgrabred/corepage"
    request =urllib.request.Request(url_getbatchId,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        # msg(result2)
        # msg(result2["code"])
        if(result2["code"]==0):
            if "batchId" in result2["data"]:
                msg("batchId:%s\n"%(result2["data"]["batchId"]))
                return result2["data"]["batchId"]
            else:
                msg("获取batchId失败👀，当前非限时抢红包时间段,无法进行下一步，但已为您签到完毕🙏!\n")
                send('### 美团 ###')   # 启用通知服务
                sys.exit(0)

        elif (result2["code"]==1):
            msg("%s,接口需提交的token参数已改变👀,请修改后重新运行一遍脚本！\n"%(result2["msg"]))
            send('### 美团 ###')   # 启用通知服务
            sys.exit(0)
        else:
            msg("获取batchId错误👀，请检查网络，否则为接口失效！\n")
            send('### 美团 ###')   # 启用通知服务
            sys.exit(0)
        


    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg(e.code)
        if hasattr(e,"reason"):
            msg(e,"reason")



#定义每天七次签到领豆的函数，需传入获取的token
def signForBeans(token):
    msg("**开始执行签到领豆脚本:** \n")
    datas = "token="+token
    url_signforbeans = baseurl+r"/cfeplay/playcenter/batchgrabred/drawPoints/v2"
    request =urllib.request.Request(url_signforbeans,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        # msg(result2)
        # msg(result2["code"])
        if(result2["code"]==0):
            msg("👴%s\n"%(result2["msg"]))
        elif (result2["code"]==1):
            msg("👴未到领取时间或已经领取完了(每天可领7次,每次间隔需半小时\n)！")
        elif (result2["code"]==7):
            msg("token已失效！\n")
        else:
            msg("请求接口失效或网络不佳，请稍后再试!\n")


    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败👀，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            msg(e,"reason")


#def 限时抢红包函数
def drawlottery(batchId,token,propIdforuse):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**开始执行限时抢天天神券脚本🧧:**\n")
    datas = "parActivityId="+parActivityId+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+token+"&batchId="+batchId+"&isShareLink=true"+"&propType=1"+"&propId="+str(propIdforuse)
    url_drawlottery = baseurl+r"/cfeplay/playcenter/batchgrabred/drawlottery"
    request =urllib.request.Request(url_drawlottery,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        # msg(result2)
        # msg(result2["code"])
        if(result2["code"]==0):
            msg("领取成功!\n提示信息:%s\n红包属性:%s\n使用限制:%s\n红包价值:%s\n红包立即生效时间:%s\n红包剩余有效期:%s分钟\n"%(result2["msg"],result2["data"]["name"],result2["data"]["priceLimitdesc"],result2["data"]["showTitle"],result2["data"]["endTimeDesc"],str(float(result2["data"]["leftTime"])/60000)))
            global showPriceNumber
            showPriceNumber = result2["data"]["showPriceNumber"]
            if int(showPriceNumber)<500:
                msg("**当前红包面值为%d元，小于5元，👴将自动执行小额红包转红包豆脚本!!**\n"%(int(showPriceNumber)/100))
            else:
                msg("**当前红包面值为%d元，大于等于5元，👴将不会执行小额红包转红包豆脚本!!**\n"%(int(showPriceNumber)/100))
        elif (result2["code"]==1 and result2["subcode"]==3):
            msg("%s😅\n"%(result2["msg"]))
        elif(result2["code"]==1 and result2["subcode"]==-1):
            msg("token错误或已失效,%s\n"%(result2["msg"]))
        elif (result2["code"]==7):
            msg("token已失效！\n")
        else:
            msg("请求接口失效或参数异常，请稍后再试!\n")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            msg(e,"reason")


#定义接受红包函数，获得红包小于5元时，不执行此函数，并调用redtobean函数自动将红包转为红包豆，若两个函数都不执行，在抢红包成功5分钟左右红包会自动发放到账户
def acceptRed(batchId,token):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**开始执行发放天天神券🧧到红包库脚本:**\n")
    datas = "parActivityId="+parActivityId+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+token+"&batchId="+batchId
    url_acceptRed = baseurl+r"/cfeplay/playcenter/batchgrabred/acceptRed"
    request =urllib.request.Request(url_acceptRed,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        # msg(result2)
        # msg(result2["code"])
        if(result2["code"]==0):
            msg("*👴抢到的红包已经领取成功啦，快去使用吧!*\n")
        elif (result2["code"]==1):
            msg("%s\n"%(result2["msg"]))
        elif (result2["code"]==7):
            msg("token已失效！\n")
        else:
            msg("请求接口失效或参数异常，请稍后再试!\n")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败👀，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            
            msg(e,"reason")

#定义红包转红包豆函数，将小于5元的红包转为红包豆
def redtobean(batchId,token):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**默认尝试执行面值小于5元🧧自动转红包豆脚本:**\n")
    datas = "parActivityId="+parActivityId+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+token+"&batchId="+batchId
    url_drawlottery = baseurl+r"/cfeplay/playcenter/batchgrabred/redToBean"
    request =urllib.request.Request(url_drawlottery,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        # msg(result2)
        # msg(result2["code"])
        if(result2["code"]==0):
            msg("👴小额红包转红包豆成功!\n")
        elif (result2["code"]==1 and result2["subcode"]==12):
            # msg("%s😅\n"%(result2["msg"]))
            msg("没有待转换的红包😅\n")
        elif (result2["code"]==7):
            msg("token已失效！\n")
        else:
            msg("请求接口失效或参数异常，请稍后再试!\n")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            
            msg(e,"reason")
    



#查询已领取到的天天神券
def querymyreward(token):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**开始执行查询已领天天神券🧧脚本:**\n")
    datas = "parActivityId="+parActivityId+"&token="+token
    url_querymyreward = baseurl+r"/cfeplay/playcenter/batchgrabred/myreward"
    request =urllib.request.Request(url_querymyreward,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        # msg(result2)
        # msg(result2["code"])
        if(result2["code"]==0 and len(result2["data"]["myawardInfos"])):
            msg("👴开始遍历红包库:\n")
            msg("红包库详细信息:\n")
            msg("红包库中共有%d个红包\n"%(len(result2["data"]["myawardInfos"])))
            cent=0
            count = 0
            isover15=0
            for k in result2["data"]["myawardInfos"]:
                if not k["status"]:
                    msg("**第%d个红包有效!!!!**\n红包属性:%s\n使用限制:%s\n红包价值:%s元\n红包剩余有效期%s分钟\n"%(cent+1,k["name"],k["priceLimitdesc"],k["showPriceNumberYuan"],str(float(k["leftTime"])/60000)))
                    if(int(k["showPriceNumberYuan"])>15):
                        isover15 =1
                    msg("\n")
                else:
                    count=count+1
                    if cent == 0:
                        msg("**过期红包详情:**\n")
                    
                cent=cent+1
            if(propIdforuse!=5):
                msg("总计已领取%d个红包,其中已过期%d个😅,有效%d个\n"%(cent,count,cent-count))
            else:
                if isover15==1:
                    msg("恭喜你领取大额限时红包,具体价值如上所示!!总计已领取%d个红包,其中已过期%d个😅,有效%d个\n"%(cent,count,cent-count))
            msg("\n")
        elif (result2["code"]==1):
            msg("%s\n"%(result2["msg"]))
        elif (result2["code"]==7):
            msg("token已失效！\n")
        else:
            msg("请求接口失效或参数异常，请稍后再试!\n")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败👀，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            
            msg(e,"reason")


#获取每日浏览天天神券奖励的30豆
def sendTaskRedBean(token):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**开始执行领取每日30豆的脚本:**\n")
    datas = "parActivityId="+parActivityId+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+token+"&portraitId="+str(portraitId)
    url_sendTaskRedBean = baseurl+r"/cfeplay/playcenter/batchgrabred/sendTaskRedBean"
    request =urllib.request.Request(url_sendTaskRedBean,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        if(result2["status"]==0):
            msg("%s\n今天领取成功%d个红包豆，请明日再来！\n"%(result2["msg"],result2["sendBeanCount"]))
        elif (result2["status"]==1):
            msg("您今日已领取过😅,%s\n"%(result2["msg"]))
        elif (result2["status"]==-1):
            msg("portraitId已失效,%s\n"%(result2["msg"]))
        else:
            msg("请求接口失效或参数异常，请稍后再试!\n")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败👀，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            msg(e,"reason")


#定义每日签到得必中符函数
def doAction(token):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**开始执行每日签到领必中符🧧的脚本:**\n")
    datas = "parActivityId="+parActivityId+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+token+"&action=SiginInGetProp"
    url_doaction = baseurl+r"/cfeplay/playcenter/batchgrabred/doAction"
    request =urllib.request.Request(url_doaction,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        if(result2["code"]==0 and result2["data"]["signDays"]!=0):
            msg("签到%s\n,截止今日这周已签到%d天"%(result2["msg"],result2["data"]["signDays"]))
        elif (result2["code"]==0 and result2["data"]["signDays"]==0):
            msg("您今日已签到，请明天再来!")
        elif (result2["code"]==7):
            msg("参数异常或接口已失效")
        else:
            msg("请求接口失效或参数异常，请稍后再试!\n")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败👀，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            msg(e,"reason")


#查看道具库中的必中符记录
def querymyProps(token):
    global propIdforuse
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**开始执行查询道具库中必中符🧧详情的脚本:**\n")
    datas = "parActivityId="+parActivityId+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+token
    url_querymyprops = baseurl+r"/cfeplay/playcenter/batchgrabred/myProps"
    request =urllib.request.Request(url_querymyprops,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        if(result2["code"]==0 and len(result2["data"])):
            msg("👴开始遍历道具库:\n")
            msg("道具库详细信息:\n")
            msg("红包库中共有%d个必中符道具\n"%(len(result2["data"])))
            cent=0
            count = 0
            for k in result2["data"]:
                if k["status"]==1:
                    msg("第%d个必中符道具有效!!!!\n必中符道具id号:%s\n必中符道具属性:%s\n过期时间:%s\n"%(cent+1,k["recordNo"],k["propName"],k["expireTime"]))
                    if cent==0:
                        propIdforuse = k["propId"] 
                    msg("\n")
                else:
                    count=count+1   
                cent=cent+1
            if (count!=0):
                 msg("总计%d个必中符道具,已过期%d个😅,有效%d个\n"%(cent,count,cent-count))
            if ((cent-count)!=0):
                msg("**注意:每天中午抢红包🧧时将自动为您使用道具库中第一个道具!!** ")
            else:
                msg(" **注意:道具库无有效道具，无法使用必中符,下次抢红包将使用默认参数抢红包(拼手气😅)!!** ")

            msg("\n")
        elif (result2["code"]==7):
            msg("参数异常或接口已失效！")
        else:
            msg("必中符道具库为空，👴未帮您领取过道具!\n")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败👀，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            msg(e,"reason")

#已废弃，直接发送兑换请求即可，不在兑换时间段 subcode 为13
#定义运行时是否能兑换豆子成必中符,目前一直为14点至16点，故不定义此函数，采取每天14点至16点运行此程序时直接尝试兑换
#若需自行获取当前时间段是否可换豆子为道具，则post以下请求即可
# POST /cfeplay/playcenter/batchgrabred/canExchangeCheck HTTP/1.1
# Host: i.waimai.meituan.com
# Content-Length: 82
# User-Agent:MeituanGroup/11.9.208
# x-requested-with: XMLHttpRequest
# content-type: application/x-www-form-urlencoded


# parActivityId=Gh1tkq-wvFU2xEP_ZPzHPQ&wm_latitude=30657401&wm_longitude=104065827







#定义豆子兑换成必中符函数:
def exchange(token):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    wm_actual_latitude = str(wm_latitude)
    wm_actual_longitude =str(wm_longitude)
    propId = getVar()[3]
    exchangeCoinNumber = getVar()[4]
    msg("**开始执行每日豆子兑换必中符脚本**:\n")
    while(1):
        datas = "wm_actual_longitude="+wm_actual_longitude+"&wm_actual_latitude="+wm_actual_latitude+"&exchangeRuleId=&propId="+str(propId)+"&exchangeCoinNumber="+str(exchangeCoinNumber)+"&parActivityId="+parActivityId+"&wm_ctype="+wm_ctype+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+token
        url_exchange = baseurl+r"/cfeplay/playcenter/batchgrabred/exchange"
        request =urllib.request.Request(url_exchange,headers=head,data=datas.encode("utf-8"),method="POST")
        try:
            response = urllib.request.urlopen(request)
            result = response.read().decode("utf-8")
            result2 = json.loads(result)
            if(result2["code"]==0 and result2["subcode"]==0):
                msg("%s,您设置的红包豆兑换指定额度的必中符成功!!!请查看下方道具库详情!😄\n"%(result2["msg"]))
                break
            elif (result2["code"]==1 and result2["subcode"]==13):
                msg("%s\n"%(result2["msg"]))
                break
            elif (result2["code"]==1 and result2["subcode"]==-1):
                msg("%s,您现在的红包豆不足以兑换此类红包!\n正尝试兑换*次一等级*必中符\n"%(result2["msg"]))
                if(propId==2):
                    msg("您现有的红包豆数量太少，无法兑换任何面值的必中符,下次运行时将再次为您尝试!\n")
                    break
                if(propId ==3):
                    propId =2
                if(propId==4):
                    propId =3
                if(propId ==5):
                    propId =4
            elif (result2["code"]==7):
                msg("参数异常或接口已失效\n")
            else:
                msg("请求接口失效或参数异常，请稍后再试!\n")
        except urllib.error.URLError as e:
            if hasattr(e,"code"):
                msg("脚本执行失败👀，错误代码如下:\n")
                msg(e.code)
            if hasattr(e,"reason"):
                msg(e,"reason")

###定义查询豆子详情的函数
def myRedBeanRecords(token):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**开始执行查询豆子变化详情参数脚本**:\n")
    datas = "parActivityId="+parActivityId+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+str(token)+"&userPortraitId="+str(portraitId)+"&pageNum=1"
    url_myredbeanRecords = baseurl+r"/cfeplay/playcenter/batchgrabred/myRedBeanRecords"
    request =urllib.request.Request(url_myredbeanRecords,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        response = urllib.request.urlopen(request,timeout=10)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)
        cent=1
        if(result2["code"]==0 and result2["subcode"]==0 and len(result2["data"]["redBeanRecordInfos"])):
            leftdou= result2["data"]["totalObtainAmount"]-result2["data"]["usedAmount"]-result2["data"]["expiredAmount"]
            msg("**总获得红包豆:%d,已使用红包豆:%d,已过期红包豆:%d,剩余可用红包豆:%d**\n"%(result2["data"]["totalObtainAmount"],result2["data"]["usedAmount"],result2["data"]["expiredAmount"],leftdou))
            for k in result2["data"]["redBeanRecordInfos"]:
                msg("exchangeTime:%s\texchangeMessage:%s\texchangeNumber:%s\n"%(k["exchangeTime"],k["exchangeMessage"],k["exchangeNumber"]))
                cent=cent+1
                if(cent>10):
                    break  
            msg("*只显示最近十条红包豆的变化* \n")
        elif (result2["code"]==1 and result2["subcode"]==-1):
            msg("%s\n"%(result2["msg"]))
        else:
            msg("请求接口失效或参数异常，建议🙏重置参数!\n")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败👀，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            msg(e,"reason")    




#定义查询红包池函数 
def queryredpool(token):
    wm_latitude = getVar()[0]
    wm_longitude = getVar()[1]
    msg("**开始执行查询红包池详情脚本:**\n")
    datas = "parActivityId="+parActivityId+"&wm_latitude="+str(wm_latitude)+"&wm_longitude="+str(wm_longitude)+"&token="+str(token)+"&wm_ctype="+wm_ctype
    url_myredbeanRecords = baseurl+r"/cfeplay/playcenter/batchgrabred/corepage"
    request =urllib.request.Request(url_myredbeanRecords,headers=head,data=datas.encode("utf-8"),method="POST")
    try:
        global eight,ten,fifteen,thirty,fifty,eight_left,ten_left,fifteen_left,thirty_left,fifty_left
        response = urllib.request.urlopen(request)
        result = response.read().decode("utf-8")
        result2 = json.loads(result)

        if(result2["code"]==0 and result2["subcode"]==0 and len(result2["data"]["awardInfos"])):
            for k in result2["data"]["awardInfos"]:
                if"leftStock" not in k:
                    msg("该地区没有红包池，脚本异常退出！")
                # if (round(float(k["showPriceNumberYuan"]))==8 and k["leftStock"]==eight_left):
                #     eight = 0
                if (round(float(k["showPriceNumberYuan"]))==10 and k["leftStock"]==ten_left):
                    ten = 0
                if (round(float(k["showPriceNumberYuan"]))==15 and k["leftStock"]==fifteen_left):
                    fifteen = 0
                if (round(float(k["showPriceNumberYuan"]))==30 and k["leftStock"]==thirty_left):
                    thirty = 0
                if (round(float(k["showPriceNumberYuan"]))==50 and k["leftStock"]==fifty_left):
                    fifty = 0
                msg("*红包池中%s元总量:%d张,已被领取:%d张,剩余%d张*\n"%(k["showPriceNumberYuan"],k["totalStock"],k["sendStock"],k["leftStock"]))
                
        elif (result2["code"]==1 and result2["subcode"]==-1):
            msg("token失效,导致获取活动信息失败！%s\n"%(result2["msg"]))
        else:
            msg("请求接口失效或参数异常，建议🙏重置参数!\n")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            msg("脚本执行失败👀，错误代码如下:\n")
            msg(e.code)
        if hasattr(e,"reason"):
            msg(e,"reason")    

def main():
    global propIdforuse
    temp = sys.stdout
    msg("本脚本提供多种推送方式,可以多选一或者全选!\n")
    token = get_env('meituan_token')
    myredbean(token)
    # sys.stdout = Logger(str(cwd)+r'/output.txt')
    token = getVar()[2]
    signForBeans(token)
    #
    queryredpool(token)
    batchId = getbatchId(token)
    ##先去保持每天签到 以获得必中符或者豆子
    doAction(token)
    exchange(token)   
    querymyProps(token)
    #定义bool类型变量判断当前时间段是不是自定义的大额抢红包时间段
    istimeforbig1= (n_time <=d_time4) and(n_time>=d_time3)
    istimeforbig2= (n_time <=d_time6) and(n_time>=d_time4)
    if n_time > d_time7:
        if istimeforbig1:
            if propIdforuse ==5:
                msg("**当前符合抢30元以上大额红包的条件**\n")
                msg("**正使用15元必中符为您尝试抢30元以上的红包**\n")
                    ##拥有15块以上的必中符，先等待着试图抢30,要是15没了，就直接去抢30的红包，或许有可能抢到50
                while  fifteen ==1 :
                    if not istimeforbig1:
                        msg("*👴尽力了，等到红包池要关闭了都未等到15元以上大额红包被抢完，开始保底15元，注意查收！*\n")
                        break
                    if(thirty ==1 and fifty ==1):
                        msg("*15有剩余，30元已被抢完，50元已被抢完，跳出监测，正在为您抢保底15元红包!*\n")
                        break
                    queryredpool(token)


        if istimeforbig2 :
            if propIdforuse ==5:
                msg("**当前符合抢30元以上大额红包的条件**\n")
                msg("**正使用15元必中符为您尝试抢30元以上的红包**\n")
                    ##拥有15块以上的必中符，先等待着试图抢30,要是15没了，就直接去抢30的红包，或许有可能抢到50
                while  fifteen ==1 :
                    if not istimeforbig2 :
                        msg("*👴尽力了，等到红包池要关闭了都未等到15元以上大额红包被抢完，开始保底15元，注意查收！*\n")
                        break
                    if(thirty ==1 and fifty ==1):
                        msg("*15有剩余，30元已被抢完，50元已被抢完，跳出监测，正在为您抢保底15元红包!*\n")
                        break
                    queryredpool(token)

        if istimeforbig1:    
            if propIdforuse ==3:
                msg("**当前符合抢30元以上大额红包的条件**\n")
                msg("**正使用10元必中符为您尝试抢30元以上的红包**\n")
                    ##拥有10块以上的必中符，先等待着试图抢30,要是10和15都没了，就直接去抢30的红包，或许有可能抢到50

                while  fifteen ==1 :
                    if(thirty ==1 and fifty ==1 ):
                        msg("&15有剩余，30元已被抢完，50元已被抢完，跳出监测，正在为您抢保底15元红包！*\n")
                        break 
                    if(br ==1):
                        break
                    if not istimeforbig1:
                            msg("*👴尽力了，等到红包池要关闭了都未等到15元以上大额红包被抢完，开始保底15元，注意查收！*\n")
                            break
                    if ten ==0 :
                        queryredpool(token)
                    while ten ==1:
                        if not istimeforbig1:
                            br = 1
                            msg("*👴尽力了，等到红包池要关闭了都未等到任意大额红包被抢完，开始保底10元，注意查收！*\n")
                        queryredpool(token)  
        
        if istimeforbig2:    
            if propIdforuse ==3:
                msg("**当前符合抢30元以上大额红包的条件**\n")
                msg("**正使用10元必中符为您尝试抢30元以上的红包**\n")
                    ##拥有10块以上的必中符，先等待着试图抢30,要是10和15都没了，就直接去抢30的红包，或许有可能抢到50

                while  fifteen ==1 :
                    if(thirty ==1 and fifty ==1 ):
                        msg("&15有剩余，30元已被抢完，50元已被抢完，跳出监测，正在为您抢保底15元红包！*\n")
                        break 
                    if(br ==1):
                        break
                    if not istimeforbig2:
                            msg("*👴尽力了，等到红包池要关闭了都未等到15元以上大额红包被抢完，开始保底15元，注意查收！*\n")
                            break
                    if ten ==0 :
                        queryredpool(token)
                    while ten ==1:
                        if not istimeforbig2:
                            br = 1
                            msg("*👴尽力了，等到红包池要关闭了都未等到任意大额红包被抢完，开始保底10元，注意查收！*\n")
                        queryredpool(token)  

    if n_time < d_time7  :
        propIdforuse =1      
    drawlottery(batchId,token,propIdforuse)

    if(int(showPriceNumber)<500):
        redtobean(batchId,token)
    else:
        acceptRed(batchId,token)
    querymyreward(token)
    sendTaskRedBean(token)
    querymyProps(token)
    myRedBeanRecords(token)
    sys.stdout = temp
    send('### 美团 ###')   # 启用通知服务

    
if __name__ == "__main__":
    main()
    
    
