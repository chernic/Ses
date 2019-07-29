import os
import logging
import time
import os, io, sys, re, time, json, base64
import webbrowser, urllib.request

ChinaStockIndexList = [
    {"1":"000728",  "Name": "国元证券", "Code":"000728", "Base":"5.35"},
    {"2":"002945",  "Name": "华林证券", "Code":"002945", "Base":"0"},
    {"3":"002939",  "Name": "长城证券", "Code":"002939", "Base":"0"},
    {"4":"300059",  "Name": "东方财富", "Code":"300059", "Base":"8.34"},
    {"5":"002736",  "Name": "国信证券", "Code":"002736", "Base":"6.59"},
    {"6":"600837",  "Name": "海通证券", "Code":"600837", "Base":"7.45"},
    {"7":"601901",  "Name": "方正证券", "Code":"601901", "Base":"4.43"},
    {"8":"601881",  "Name": "中国银河", "Code":"601881", "Base":"5.51"},
    {"9":"600999",  "Name": "招商证券", "Code":"600999", "Base":"11.13"},
    {"10":"601688", "Name": "华泰证券", "Code":"601688", "Base":"13.40"},
    {"11":"600621", "Name": "华鑫股份", "Code":"600621", "Base":"6.12"},
    {"12":"600030", "Name": "中信证券", "Code":"600030", "Base":"14.72"},
]

# 如果日志文件夹不存在，则创建
log_dir = "log"  # 日志存放文件夹名称
log_path = os.getcwd() + os.sep + log_dir
if not os.path.isdir(log_path):
    os.makedirs(log_path)

# 设置logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
main_log_handler = logging.FileHandler(
    log_dir + "/dd_%s.log" % time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time())), mode="w+",
    encoding="utf-8")
main_log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
main_log_handler.setFormatter(formatter)
logger.addHandler(main_log_handler)

# 控制台打印输出日志
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
formatter = logging.Formatter("%(message)s")
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

period_All_List = [
                    "min",      #分时线
                    "daily",    #日K线
                    "weekly",   #周K线
                    "monthly"   #月K线
                  ]
period_min = period_All_List[0]
period_daily = period_All_List[1]

def exchange(stockCode):
    ex = "sh" if (int(stockCode) // 100000 == 6) else "sz"
    return str(ex + stockCode)

def exchanges(stockCodes):
    Str = "";
    if ( stockCodes and len(stockCodes) > 0) :
        for stockCode in stockCodes:
            Str  = Str+ exchange(stockCode["Code"])  + ",";
            # print(Str[:-1])
    return { "stockCode":stockCode, "Str":Str[:-1] }

def r(rr):
    if rr:
        return "{0:>5.2f}".format( float(rr) )
    else:
        return "     "
        
def r3(rr):
    if rr:
        return "{0:>5.3f}".format( float(rr) )
    else:
        return "     "



def Pre(b,s,x):
    if(x>b*2):
        b=b*2
    pre=int(round((x-s)/b*100,0)/2)
    return {
            0: "          ",
            1: " *        ",
            2: " **       ",
            3: " ***      ",
            4: " ****     ",
            5: " *****    ",
            6: " ******   ",
            7: " *******  ",
            8: " ******** ",
            9: " *********",
    }.get(pre,'error')    #'error'为默认返回值，可自设置


def Gold(Now,Base):
    Base=float(Base)
    Now=float(Now)
    # if(Now>Base*2):
        # Base=Base*2

    B13=Base*1.3
    B15=Base*1.5
    B17=Base*1.7
    B20=Base*2.0
    B26=Base*2.6
    B30=Base*3.0
    B34=Base*3.4
    B40=Base*4.0

    if betwween(Now,B13,B15):
        return r(B13)+"|"+r( 0 )+"|"+r( 0 )+"|"+r( 0 )+"|"+r( 0 )+"  "+r(Now)+"  "+r3(Now/B13)+Pre(Base,B13,Now)
    if betwween(Now,B15,B17):                           
        return r( 0 )+"|"+r(B15)+"|"+r( 0 )+"|"+r( 0 )+"|"+r( 0 )+"  "+r(Now)+"  "+r3(Now/B15)+Pre(Base,B15,Now)
    if betwween(Now,B17,B20):                         
        return r( 0 )+"|"+r( 0 )+"|"+r(B17)+"|"+r( 0 )+"|"+r( 0 )+"  "+r(Now)+"  "+r3(Now/B17)+Pre(Base,B17,Now)
    if betwween(Now,B20,B26):                         
        return r( 0 )+"|"+r( 0 )+"|"+r( 0 )+"|"+r(B20)+"|"+r( 0 )+"  "+r(Now)+"  "+r3(Now/B20)+Pre(Base,B20,Now)
    if betwween(Now,B26,B30):                         
        return r( 0 )+"|"+r( 0 )+"|"+r( 0 )+"|"+r( 0 )+"|"+r(B26)+"  "+r(Now)+"  "+r3(Now/B26)+Pre(Base,B26,Now)

def betwween(x,a,b):
    if float(a)<float(x) and float(x)<float(b):
        return True
    else :
        return False
            
def getChinaStockIndividualInfo(stockCode, period):
    try:
        dataUrl = "http://hq.sinajs.cn/list=" + exchanges(stockCode)["Str"]
        stdout = urllib.request.urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312')
        
        tempData1 = re.search('''(")(.+)(")''', stdoutInfo).group(2)
        tempDatas = re.findall('''(")(.+)(")''', stdoutInfo)
        

        # print(tempData1)
        # print(tempDatas[0][1])

        twitter={}
        i=0
        for tempDataX in tempDatas:
            tempData=tempDataX[1]
            stockInfo = tempData.split(",")
            # stockCode = stockCode,
            stockName   = stockInfo[0]  #名称
            stockStart  = stockInfo[1]  #开盘
            stockLastEnd= stockInfo[2]  #昨收盘
            stockCur    = stockInfo[3]  #当前
            stockMax    = stockInfo[4]  #最高
            stockMin    = stockInfo[5]  #最低
            stockUp     = round(float(stockCur) - float(stockLastEnd), 2)
            stockRange  = round(float(stockUp) / float(stockLastEnd), 4) * 100
            stockVolume = round(float(stockInfo[8]) / (100 * 10000), 2)
            stockMoney  = round(float(stockInfo[9]) / (100000000), 2)
            stockTime   = stockInfo[31]
            
            
            Code=stockCode[i]["Code"]
            Base=stockCode[i]["Base"]
            B13=float(Base)*1.3
            B15=float(Base)*1.5
            B17=float(Base)*1.7
            B20=float(Base)*2.0
            B40=float(Base)*4.0
            
            if betwween(stockLastEnd,B13,B15):
                logger.info( stockName+Gold(stockLastEnd,Base))
            if betwween(stockLastEnd,B15,B17):
                logger.info( stockName+Gold(stockLastEnd,Base))
            if betwween(stockLastEnd,B17,B20):
                logger.info( stockName+Gold(stockLastEnd,Base))
            if betwween(stockLastEnd,B20,B40):
                logger.info( stockName+Gold(stockLastEnd,Base))
            
            
            i=i+1

            #content = "#" + stockName + "#(" + stockCode + ")" + " 开盘:" + stockStart \
            #+ ",最新:" + stockCur + ",最高:" + stockMax + ",最低:" + stockMin \
            #+ ",涨跌:" + str(stockUp) + ",幅度:" + str(stockRange) + "%" \
            #+ ",总手:" + str(stockVolume) + "万" + ",金额:" + str(stockMoney) \
            #+ "亿" + ",更新时间:" + stockTime + "  "

    except Exception as e:
        print(">>>>>> Exception: " + str(e))
    else:
        return twitter
    finally:
        None

while True:
    getChinaStockIndividualInfo(ChinaStockIndexList,period_daily)
    time.sleep(30)
    logger.info("")
    
