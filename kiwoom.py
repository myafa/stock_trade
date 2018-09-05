
# coding: utf-8

# In[ ]:


from PyQt5 import QtWidgets ,QAxContainer ,QtCore


# In[ ]:


class Kiwoom(QAxContainer.QAxWidget):
    def __init__(self):
        super().__init__()
        self._createKiwoomInstance()
        self._setSignalSlots()
    
    def _createKiwoomInstance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
    def _setSignalSlots(self):
        self.OnEventConnect.connect(self._eventConnect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
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
        print(22)
        return realData
    def setRealReg(self, screenNo, strCodeList, strFidList, strRealType): # sNo, "share1;share2;...", "FID1;FID2;..."
        self.dynamicCall("SetRealReg(QString,QString,QString,QString)",screenNo,strCodeList,strFidList,strRealType)
    def receiveRealData(self,sCode, sRealType, sRealData):
        temp = []
        print (1)
        for fid in RealType.REALTYPE[sRealType].keys():
            value = self.getCommRealData(sCode,fid)
            self.rData[fid].append(value)
            temp+=value
        print(temp)
    def get_code_list_by_market(self, market):
        codeList =self.dynamicCall("GetCodeListByMarket(QString)",market)
        codeList = codeList.split(';')
        return codeList[:-1]
    def get_mastercode_name(self, code):
        codeName = self.dynamicCall("GetMasterCodeName(QString)",code)
        return codeName
    def _opt10081(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode,rqname)
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

