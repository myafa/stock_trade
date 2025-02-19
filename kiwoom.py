
# coding: utf-8

# In[ ]:


from PyQt5 import QtWidgets ,QAxContainer ,QtCore
import time
from datetime import datetime
# In[ ]:


class Kiwoom(QAxContainer.QAxWidget):
    def __init__(self):
        super().__init__()
        self._createKiwoomInstance()
        self._setSignalSlots()
        fileName = datetime.now().strftime('%y%m%d')
        self.file = open(fileName, 'a')
    def _createKiwoomInstance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
    def _setSignalSlots(self):
        self.OnEventConnect.connect(self._eventConnect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
    def button_clicked(self):
        self.OnReceiveRealData.connect(self.receiveRealData) 
        
    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)",trcode,rqname)
        return ret
    def _comm_get_data(self, code, realType, fieldName, index, itemName):
        ret = self.dynamicCall("CommGetData(QString,QString,QString,int,QString)",code,realType,fieldName,index,itemName)
        return ret.strip()
    def _receive_tr_data(self,screenNo,rqname,trcode,recordName,next,unused1,unused2,unused3,unused4):
        if next == '2':
            self.remainedData = True
        else:
            self.remainedData = False
        
        if rqname == "opt10081_req":
            self._opt10081(rqname,trcode)
        
        try:
            self.tr_event_loop.exit()
        except AttributeError:
            print ("Attribute Error occured")
    
    def comm_rq_data(self, rqname, trcode, next, screenNo):
        self.dynamicCall("CommRqData(QString,Qstring,int,QString)",rqname,trcode,next,screenNo)
        self.tr_event_loop = QtCore.QEventLoop()
        self.tr_event_loop.exec_()
    
    def _eventConnect(self, errCode):
        if errCode == 0:
            print("Connected")
        else:
            print("Disconnected")
        self.loginEventLoop.exit()
    def commConnect(self):
        self.dynamicCall("CommConnect()")
        self.loginEventLoop = QtCore.QEventLoop()
        self.loginEventLoop.exec_()
        
    def get_connect_state(self):
        return self.dynamicCall("GetConnectState()")
    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString,QString)",id,value)

    def getCommRealData(self, strCode, nFid):
        realData = self.dynamicCall("GetCommRealData(Qstring, int)",strCode ,nFid)
        return realData
    def setRealReg(self, screenNo, strCodeList, strFidList, strRealType): # sNo, "share1;share2;...", "FID1;FID2;..."
        self.dynamicCall("SetRealReg(QString,QString,QString,QString)",screenNo,strCodeList,strFidList,strRealType)
    def receiveRealData(self,sCode, sRealType, sRealData):
        temp = []
        
        for fid in RealType.REALTYPE[sRealType].keys():
            value = self.getCommRealData(sCode,fid)
            #self.rData[fid].append(value)
            temp+=value
        self.file.write("".join(temp)+"\n")    
        print("".join(temp)+"\n")
    def get_code_list_by_market(self, market):
        codeList =self.dynamicCall("GetCodeListByMarket(QString)",market)
        codeList = codeList.split(';')
        return codeList[:-1]
    def get_mastercode_name(self, code):
        codeName = self.dynamicCall("GetMasterCodeName(QString)",code)
        return codeName
    def _opt10081(self, rqname, trcode):
        data_cnt = 1#self._get_repeat_cnt(trcode,rqname)
        for i in range(data_cnt):
            date = self._comm_get_data(trcode,"",rqname,i,"일자")
            open = self._comm_get_data(trcode,"",rqname,i,"시가")
            high = self._comm_get_data(trcode,"",rqname,i,"고가")
            low  = self._comm_get_data(trcode,"",rqname,i,"저가")
            close =self._comm_get_data(trcode,"",rqname,i,"현재가")
            volume=self._comm_get_data(trcode,"",rqname,i,"거래량")
            print(date,open,high,low,close,volume)
    def get_daily(self, code, start):
        self.daily = {'data':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volumn':[]}
        self.set_input_value("종목코드",code)
        self.set_input_value("기준일자",start)
        self.set_input_value("수정주가구분",1)
        self.comm_rq_data("opt10081_req","opt10081",0,"0101")
        time.sleep(0.2)

class RealType(object):
    REALTYPE = {
        '주식시세': {
            10: '현재가',
            11: '전일대비',
            12: '등락율',
            27: '최우선매도호가',
            28: '최우선매수호가',
            13: '누적거래량',
            14: '누적거래대금',
            16: '시가',
            17: '고가',
            18: '저가',
            25: '전일대비기호',
            26: '전일거래량대비',
            29: '거래대금증감',
            30: '거일거래량대비',
            31: '거래회전율',
            32: '거래비용',
            311: '시가총액(억)'
        },

        '주식체결': {
            20: '체결시간(HHMMSS)',
            10: '체결가',
            11: '전일대비',
            12: '등락율',
            27: '최우선매도호가',
            28: '최우선매수호가',
            15: '체결량',
            13: '누적체결량',
            14: '누적거래대금',
            16: '시가',
            17: '고가',
            18: '저가',
            25: '전일대비기호',
            26: '전일거래량대비',
            29: '거래대금증감',
            30: '전일거래량대비',
            31: '거래회전율',
            32: '거래비용',
            228: '체결강도',
            311: '시가총액(억)',
            290: '장구분',
            691: 'KO접근도'
        },

        '주식호가잔량': {
            21: '호가시간',
            41: '매도호가1',
            61: '매도호가수량1',
            81: '매도호가직전대비1',
            51: '매수호가1',
            71: '매수호가수량1',
            91: '매수호가직전대비1',
            42: '매도호가2',
            62: '매도호가수량2',
            82: '매도호가직전대비2',
            52: '매수호가2',
            72: '매수호가수량2',
            92: '매수호가직전대비2',
            43: '매도호가3',
            63: '매도호가수량3',
            83: '매도호가직전대비3',
            53: '매수호가3',
            73: '매수호가수량3',
            93: '매수호가직전대비3',
            44: '매도호가4',
            64: '매도호가수량4',
            84: '매도호가직전대비4',
            54: '매수호가4',
            74: '매수호가수량4',
            94: '매수호가직전대비4',
            45: '매도호가5',
            65: '매도호가수량5',
            85: '매도호가직전대비5',
            55: '매수호가5',
            75: '매수호가수량5',
            95: '매수호가직전대비5',
            46: '매도호가6',
            66: '매도호가수량6',
            86: '매도호가직전대비6',
            56: '매수호가6',
            76: '매수호가수량6',
            96: '매수호가직전대비6',
            47: '매도호가7',
            67: '매도호가수량7',
            87: '매도호가직전대비7',
            57: '매수호가7',
            77: '매수호가수량7',
            97: '매수호가직전대비7',
            48: '매도호가8',
            68: '매도호가수량8',
            88: '매도호가직전대비8',
            58: '매수호가8',
            78: '매수호가수량8',
            98: '매수호가직전대비8',
            49: '매도호가9',
            69: '매도호가수량9',
            89: '매도호가직전대비9',
            59: '매수호가9',
            79: '매수호가수량9',
            99: '매수호가직전대비9',
            50: '매도호가10',
            70: '매도호가수량10',
            90: '매도호가직전대비10',
            60: '매수호가10',
            80: '매수호가수량10',
            100: '매수호가직전대비10',
            121: '매도호가총잔량',
            122: '매도호가총잔량직전대비',
            125: '매수호가총잔량',
            126: '매수호가총잔량직전대비',
            23: '예상체결가',
            24: '예상체결수량',
            128: '순매수잔량(총매수잔량-총매도잔량)',
            129: '매수비율',
            138: '순매도잔량(총매도잔량-총매수잔량)',
            139: '매도비율',
            200: '예상체결가전일종가대비',
            201: '예상체결가전일종가대비등락율',
            238: '예상체결가전일종가대비기호',
            291: '예상체결가',
            292: '예상체결량',
            293: '예상체결가전일대비기호',
            294: '예상체결가전일대비',
            295: '예상체결가전일대비등락율',
            13: '누적거래량',
            299: '전일거래량대비예상체결률',
            215: '장운영구분'
        },

        '장시작시간': {
            215: '장운영구분(0:장시작전, 2:장종료전, 3:장시작, 4,8:장종료, 9:장마감)',
            20: '시간(HHMMSS)',
            214: '장시작예상잔여시간'
        },

        '업종지수': {
            20: '체결시간',
            10: '현재가',
            11: '전일대비',
            12: '등락율',
            15: '거래량',
            13: '누적거래량',
            14: '누적거래대금',
            16: '시가',
            17: '고가',
            18: '저가',
            25: '전일대비기호',
            26: '전일거래량대비(계약,주)'
        },

        '업종등락': {
            20: '체결시간',
            252: '상승종목수',
            251: '상한종목수',
            253: '보합종목수',
            255: '하락종목수',
            254: '하한종목수',
            13: '누적거래량',
            14: '누적거래대금',
            10: '현재가',
            11: '전일대비',
            12: '등락율',
            256: '거래형성종목수',
            257: '거래형성비율',
            25: '전일대비기호'
        },

        '주문체결': {
            9201: '계좌번호',
            9203: '주문번호',
            9205: '관리자사번',
            9001: '종목코드',
            912: '주문분류(jj:주식주문)',
            913: '주문상태(10:원주문, 11:정정주문, 12:취소주문, 20:주문확인, 21:정정확인, 22:취소확인, 90,92:주문거부)',
            302: '종목명',
            900: '주문수량',
            901: '주문가격',
            902: '미체결수량',
            903: '체결누계금액',
            904: '원주문번호',
            905: '주문구분(+:현금매수, -:현금매도)',
            906: '매매구분(보통, 시장가등)',
            907: '매도수구분(1:매도, 2:매수)',
            908: '체결시간(HHMMSS)',
            909: '체결번호',
            910: '체결가',
            911: '체결량',
            10: '체결가',
            27: '최우선매도호가',
            28: '최우선매수호가',
            914: '단위체결가',
            915: '단위체결량',
            938: '당일매매수수료',
            939: '당일매매세금'
        },

        '잔고': {
            9201: '계좌번호',
            9001: '종목코드',
            302: '종목명',
            10: '현재가',
            930: '보유수량',
            931: '매입단가',
            932: '총매입가',
            933: '주문가능수량',
            945: '당일순매수량',
            946: '매도매수구분',
            950: '당일총매도손익',
            951: '예수금',
            27: '최우선매도호가',
            28: '최우선매수호가',
            307: '기준가',
            8019: '손익율'
        },

        '주식시간외호가': {
            21: '호가시간(HHMMSS)',
            131: '시간외매도호가총잔량',
            132: '시간외매도호가총잔량직전대비',
            135: '시간외매수호가총잔량',
            136: '시간외매수호가총잔량직전대비'
        }
    }
