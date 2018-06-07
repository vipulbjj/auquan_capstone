
# coding: utf-8

# In[ ]:


from datetime import datetime, timedelta
import calendar
import os.path
import numpy as np
import pandas as pd
from itertools import groupby

TYPE_LINE_UNDEFINED = 0
TYPE_LINE_BOOK_DATA_STK = 1
TYPE_LINE_BOOK_DATA_FUT = 2
TYPE_LINE_BOOK_OPTION = 3
TYPE_LINE_TRADED_VOLUME = 4

def checkDate(lineItem):
    try:
        datetime.strptime(lineItem, '%Y/%m/%d')
        return True
    except ValueError:
        return False


def checkTimestamp(lineItem):
    return True


# Returns the type of lineItems
def validateLineItem(lineItems):
    if len(lineItems) < 4:
        return TYPE_LINE_UNDEFINED
    if checkDate(lineItems[0]) and checkTimestamp(lineItems[1]) and lineItems[2] == "Book":
        if lineItems[4][-3:] == "-10":
            return TYPE_LINE_BOOK_DATA_FUT
        else:
            return TYPE_LINE_BOOK_DATA_STK
    if len(lineItems) == 7 and lineItems[3] == '|':
        return TYPE_LINE_BOOK_OPTION
    if checkDate(lineItems[0]) and checkTimestamp(lineItems[1]) and lineItems[2] == "TradeInfo":
        return TYPE_LINE_TRADED_VOLUME
    return TYPE_LINE_UNDEFINED

def parseBookDataOptionLine(lineItems):
    if (len(lineItems) < 7):
        return None
    bidVol = float(lineItems[1])
    bidPrice = float(lineItems[2])
    askPrice = float(lineItems[4])
    askVol = float(lineItems[5])
    return {'bidVolume': bidVol,
            'bidPrice': bidPrice,
            'askPrice': askPrice,
            'askVolume': askVol}


def get_exp_date(trade_date, holiday_dates):
    date = max(week[-4] for week in calendar.monthcalendar(trade_date.year, trade_date.month))
    if date >= trade_date.day:
        exp_date = datetime(year=trade_date.year, month=trade_date.month, day=date)
    else:
        if trade_date.month != 12:
            date = max(week[-4] for week in calendar.monthcalendar(trade_date.year, 1 + trade_date.month))
            exp_date = datetime(year=trade_date.year, month=1 + trade_date.month, day=date)
        else:
            date = max(week[-4] for week in calendar.monthcalendar(1 + trade_date.year, 1))
            exp_date = datetime(year=1 + trade_date.year, month=1, day=date)
    if datetime.strftime(exp_date, '%Y%m%d') in holiday_dates:
        exp_date = exp_date + timedelta(days=-1)
    return exp_date.replace(hour=15, minute=30)

def groupAndSortByTimeUpdates(instrumentUpdates):
    instrumentUpdates.sort(key=lambda x: x['timeOfUpdate'])
    groupedInstruments = []
    # groupby only works on already sorted elements, so we sorted first
    for timeOfUpdate, sameTimeInstruments in groupby(instrumentUpdates, lambda x: x['timeOfUpdate']):
        instruments = []
        for sameTimeInstrument in sameTimeInstruments:
            instruments.append(sameTimeInstrument)
        groupedInstruments.append([timeOfUpdate, instruments])
    return groupedInstruments

class InstrumentsFromFile():
    def __init__(self, fileName, expiryTime):
        self.fileName = fileName
        self.expiryTime = expiryTime
        self.currentInstrumentSymbol = None
        self.currentTimeOfUpdate = None
        self.currentBookData = None
        self.currentFutureBookData = None
        self.futureFlag = False

    def processLine(self, line):
        lineItems = line.split()
        lineItemType = validateLineItem(lineItems)
        if (lineItemType == TYPE_LINE_BOOK_DATA_STK):
            inst = None
            if self.currentInstrumentSymbol is not None:
                inst = {'stockInstrumentId' : self.currentInstrumentSymbol,
                        'tradeSymbol' : self.currentInstrumentSymbol,
                        'timeOfUpdate' : self.currentTimeOfUpdate,
                        'bookData' : self.currentBookData,
                        'expiryTime' : self.expiryTime,
                        'futureBookData' : self.currentFutureBookData}
            self.currentTimeOfUpdate = datetime.strptime(lineItems[0] + ' ' + lineItems[1], "%Y/%m/%d %H:%M:%S:%f")
            self.currentInstrumentSymbol = lineItems[4]
            self.currentBookData = None
            self.currentFutureBookData = None
            self.futureFlag = False
            return inst
        elif(lineItemType == TYPE_LINE_BOOK_OPTION):
            parsedOption = parseBookDataOptionLine(lineItems)
            if not self.futureFlag:
                if self.currentBookData is None:
                    self.currentBookData = {}
                    self.currentBookData['bidVolume'] = np.array([parsedOption['bidVolume']])
                    self.currentBookData['bidPrice'] = np.array([parsedOption['bidPrice']])
                    self.currentBookData['askPrice'] = np.array([parsedOption['askPrice']])
                    self.currentBookData['askVolume'] = np.array([parsedOption['askVolume']])
                else:
                    self.currentBookData['bidVolume'] = np.append(self.currentBookData['bidVolume'], parsedOption['bidVolume'])
                    self.currentBookData['bidPrice'] = np.append(self.currentBookData['bidPrice'], parsedOption['bidPrice'])
                    self.currentBookData['askPrice'] = np.append(self.currentBookData['askPrice'], parsedOption['askPrice'])
                    self.currentBookData['askVolume'] = np.append(self.currentBookData['askVolume'], parsedOption['askVolume'])
            else:
                if self.currentFutureBookData is None:
                    self.currentFutureBookData = {}
                    self.currentFutureBookData['bidVolume'] = np.array([parsedOption['bidVolume']])
                    self.currentFutureBookData['bidPrice'] = np.array([parsedOption['bidPrice']])
                    self.currentFutureBookData['askPrice'] = np.array([parsedOption['askPrice']])
                    self.currentFutureBookData['askVolume'] = np.array([parsedOption['askVolume']])
                else:
                    self.currentFutureBookData['bidVolume'] = np.append(self.currentFutureBookData['bidVolume'], parsedOption['bidVolume'])
                    self.currentFutureBookData['bidPrice'] = np.append(self.currentFutureBookData['bidPrice'], parsedOption['bidPrice'])
                    self.currentFutureBookData['askPrice'] = np.append(self.currentFutureBookData['askPrice'], parsedOption['askPrice'])
                    self.currentFutureBookData['askVolume'] = np.append(self.currentFutureBookData['askVolume'], parsedOption['askVolume'])
        elif(lineItemType == TYPE_LINE_TRADED_VOLUME):
            if not self.futureFlag:
                self.currentBookData['total_traded_value'] = lineItems[6]
                self.currentBookData['total_traded_size'] = lineItems[8]
            else:
                self.currentFutureBookData['total_traded_value'] = lineItems[6]
                self.currentFutureBookData['total_traded_size'] = lineItems[8]
        elif(lineItemType == TYPE_LINE_BOOK_DATA_FUT):
            self.futureFlag = True

    def processLinesIntoInstruments(self):
        with open(self.fileName, "r") as ins:
            instruments = []
            for line in ins:
                inst = self.processLine(line)
                if inst is not None:
                    instruments.append(inst)
            return instruments


class DataSource(object):
    def __init__(self, folderName, instrumentIds, startDateStr, endDateStr):
        self.startDate = datetime.strptime(startDateStr, "%Y%m%d")
        self.endDate = datetime.strptime(endDateStr, "%Y%m%d")
        self.folderName = folderName
        self.instrumentIds = instrumentIds
        self.currentDate = self.startDate

    def getFileName(self, date):
        dateStr = date.strftime("%Y%m%d")
        return '%s/%s/data' % (self.folderName, dateStr)

    def emitInstrumentUpdate(self, holidays):
        while (self.currentDate <= self.endDate):
            allInstrumentUpdates = []
            fileName = self.getFileName(self.currentDate)
            if not os.path.isfile(fileName):
                continue
            expiryTime = get_exp_date(self.currentDate, holidays)
            fileHandler = InstrumentsFromFile(fileName=fileName, expiryTime=expiryTime)
            instrumentUpdates = fileHandler.processLinesIntoInstruments()
            allInstrumentUpdates = allInstrumentUpdates + instrumentUpdates
            groupedInstrumentUpdates = groupAndSortByTimeUpdates(allInstrumentUpdates)
            for timeOfUpdate, instrumentUpdates in groupedInstrumentUpdates:
                yield([timeOfUpdate, instrumentUpdates])
            self.currentDate = self.currentDate + timedelta(days=1)


def getvwap(stockData):
    bid_vol, ask_vol, bid_price, ask_price = stockData['bidVolume'], stockData['askVolume'], stockData['bidPrice'], stockData['askPrice']
    volume = (np.sum(bid_vol) + np.sum(ask_vol))
    if volume > 0:
        price = (np.sum(bid_price * ask_vol) + np.sum(ask_price * bid_vol)) / (volume)  # Calculated for a vol = 0.12353
    else:
        price = (np.sum(bid_price) + np.sum(ask_price)) / (len(bid_price))
    return price

def getbidp(stockData):
    bid_price=stockData['bidPrice']
    return np.max(bid_price)

def getaskp(stockData):
    ask_price=stockData['askPrice']
    return np.max(ask_price)

def get_totalv(stockData):
    total_value=stockData['total_traded_value']
    return total_value
    #print(total_value)

def get_totals(stockData):
    total_size=stockData['total_traded_size']
    return total_size



def writecsv(csv_dir, results, m):
    # results = results.sort_index(axis=0, ascending=False)
    print('writing %s%s.csv' % (csv_dir, m))
    fileName = '%s%s.csv' % (csv_dir, m)
    if os.path.exists(fileName):
        csv_file = open(fileName, 'a')
        results.to_csv(csv_file, header=False)
    else:
        csv_file = open(fileName, 'w ')
        results.to_csv(csv_file, header=True)
    csv_file.close()


if __name__ == "__main__":
    folderName = 'spare/local/cjain/NSEDATA/'
    fileName = 'stocklist'
    holiday_dates = ['20160706', '20160815', '20160905', '20160913', '20161011', '20161012', '20161031', '20161114', 
                '20161225', '20170101', '20170126', '20170224', '20170313', '20170404', '20170414', '20170501',
                '20170626', '20170815', '20170825', '20171002', '20171019', '20171020', '20171225', 
                '20180101', '20180126', '20180213', '20180302', '20180329', '20180330', '20180501', 
                '20180815', '20180822', '20180913', '20180920', '20181002', '20181018', '20181107', '20181225']

    dates =  next(os.walk(folderName))[1]
    dates.sort()
    print(dates)
    instrumentIds = []
    with open(fileName, "r") as f:
        for line in f:
            lineItems = line.split()
            instrumentIds.append(lineItems[0])

    for date in dates:
        all_data = {}
        startDateStr = date
        endDateStr = date
        for instrumentId in instrumentIds:
            all_data[instrumentId] = pd.DataFrame(index=[pd.date_range(startDateStr + ' 09:16:00', periods=375, freq='60s')],
                                                  columns=['stockVWAP', 'futureVWAP','bidPrice','askPrice', 'total_size', 'total_value'])

        dataParser = DataSource(folderName, instrumentIds, startDateStr, endDateStr)
        groupedInstrumentUpdates = dataParser.emitInstrumentUpdate(holiday_dates)
        for timeOfUpdate, instrumentUpdates in groupedInstrumentUpdates:
            print(timeOfUpdate)
            for instrumentUpdate in instrumentUpdates:
                instrumentId = instrumentUpdate['tradeSymbol']
                if timeOfUpdate in all_data[instrumentId].index:
                    stockData = instrumentUpdate['bookData']
                    futureData = instrumentUpdate['futureBookData']
                    stockData['bidPrice'] = stockData['bidPrice'] / 100.0
                    stockData['askPrice'] = stockData['askPrice'] / 100.0
                    futureData['bidPrice'] = futureData['bidPrice'] / 100.0
                    futureData['askPrice'] = futureData['askPrice'] / 100.0
                    all_data[instrumentId].loc[timeOfUpdate, 'stockVWAP'] = getvwap(stockData)
                    all_data[instrumentId].loc[timeOfUpdate, 'futureVWAP'] = getvwap(futureData)
                    all_data[instrumentId].loc[timeOfUpdate, 'bidPrice'] = getbidp(stockData)
                    all_data[instrumentId].loc[timeOfUpdate, 'askPrice'] = getaskp(stockData)
                    all_data[instrumentId].loc[timeOfUpdate, 'total_value'] = get_totalv(stockData)
                    all_data[instrumentId].loc[timeOfUpdate, 'total_size'] = get_totals(stockData)




        for instrumentId in instrumentIds:
            writecsv('stock_data_new/', all_data[instrumentId], instrumentId)
            #writecsv('parsedData/', futureData['askPrice'], instrumentId)



