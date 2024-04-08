import os
import csv
import yfinance as yf
import datetime
import math

cash = 10000
assets = ['BTC-USD', 'BNB-USD','ETH-USD','XRP-USD','DOGE-USD','LINK-USD','COMP5692-USD','LPT-USD','LDO-USD','SOL-USD','RNDR-USD','SUSHI-USD','SNX-USD','OP-USD','AVAX-USD','AAVE-USD','INJ-USD','GRT6719-USD']
# assets = ['BTC-USD', 'BNB-USD']
# assets = ['BTC-USD', 'BNB-USD']
safeAsset = 'USDT-USD'
cppi_value = cash
weights = [0.0999999999999998,0.17,0.07,0.05,0.02,0.07,0.05,0.05,0.04,0.03,0.08,0.03,0.05,0.00,0.07,0.07,0.03,0.02]
# weights = [0.5,0.5]
# print sum of all weights
print(sum(weights))
if sum(weights) != 1:
    raise Exception("Sum of weights is not 1")
# period
#period = "200d"
# Set start and end times (year, month, day, hour, minute)
start = '2022-12-01'
end = '2023-01-01'
start_ts = start
end_ts = end
interval = "1h"
riskpreval = 0

floor_percent = 0.90
floor_value = cash * floor_percent
m = 4
max_cppi_value = cash
position_value = None
savefile = 'cppi.csv'
tradesfile = 'trades.csv'
if os.path.exists(savefile):
    os.remove(savefile)
if os.path.exists(tradesfile):
    os.remove(tradesfile)
qty = {}
trades = []

for symbol in assets:
  qty[symbol] = 0
qty[safeAsset] = 0
  
if not os.path.exists(savefile):
    with open(savefile, 'w', newline='') as file:
        wr = csv.writer(file)
        #initialize the header
        header = ['cppi value', 'floor']
        wr.writerow(header)
if not os.path.exists(tradesfile):
    with open(tradesfile, 'w', newline='') as file:
        wr = csv.writer(file)
        #initialize the header
        header = ['side', 'symbol', 'q', 'price']
        wr.writerow(header)
  
  
# for simulate
timelaps = 0
length = 0
data_dict = {}

def getData():
    global length
    global data_dict
    
    ticker_data = yf.Ticker(safeAsset)
    
    # use period
    # ticker_df = ticker_data.history(period=period, interval=interval)
    # use timelaps
    ticker_df = ticker_data.history(start=start_ts, end=end_ts, interval=interval)
    
    data_dict[safeAsset] = ticker_df
    length = len(ticker_df)
    
    for asset in assets:
        ticker_data = yf.Ticker(asset)
        
        # use period
        # ticker_df = ticker_data.history(period=period, interval=interval)
        # use timelaps
        ticker_df = ticker_data.history(start=start_ts, end=end_ts, interval=interval)
        
        data_dict[asset] = ticker_df
        # print(len(ticker_df))
        length = min(length, len(ticker_df))
        
    print(length)
    return data_dict


# def getLastPrice(symbol):
#     data = getData()
#     last_price = data[symbol].iloc[-1]['Close']
#     return last_price

def getLastPrice(symbol):
    last_price = data[symbol].iloc[timelaps]['Close']
    return last_price
 
def getCash():
    return cash

def getTotalValue():
    total_value = 0
    total_value += getCash()
    twst = 0
    for symbol in assets:
        total_value += getLastPrice(symbol) * qty[symbol]
        # print (symbol, " : ", getLastPrice(symbol) , " : ", qty[symbol] , " : ", getLastPrice(symbol) * qty[symbol])
        twst += getLastPrice(symbol) * qty[symbol]
    total_value += getLastPrice(safeAsset) * qty[safeAsset]
    
    # print(total_value , " : ", getCash() , " : ", twst, " : ", getLastPrice(safeAsset) * qty[safeAsset])
    return total_value

def checkBudget(requiredCash:float):
    availableCash = getCash()
    if requiredCash > availableCash:
        raise Exception("Not enough available cash")

def checkqty(symbol, q):
    if q > qty[symbol]:
        raise Exception("Not enough available quantity")
    
def getAllRiskyAssetsValue():
    total_value = 0
    for symbol in assets:
        total_value += getLastPrice(symbol) * qty[symbol]
    return total_value

def getSafeAssetValue():
    return getLastPrice(safeAsset) * qty[safeAsset]

def placeOrder(symbol, amount):
    global cash
    temp = 0
    if amount == 0:
        return 0
    if abs(amount) < 2.5:
        return 0
    amount = math.floor(amount * 100) / 100 - 0.001
    # print('de:' , amount , " : " , symbol , ' : ', cash)
    side = 'null'
    if amount > 0:
        # checkBudget(amount)
        side = 'buy'
    elif amount < 0:
        side = 'sell'
        
    if abs(amount) < 5:
        if side == 'sell':
            temp = 5
            amount = -5
        else:
            amount = 5
            
        
    current_asset_price = getLastPrice(symbol)
    q = abs(amount) / current_asset_price
    # print('de1:' , amount , " : " , symbol , ' : ', q , " : ", cash , ' : ', side)
    

    if side == 'buy':
        if cash < amount:
            return 0
        cash = cash - q*current_asset_price*1.001
        qty[symbol] = qty[symbol] + q
        trades.append({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price})
        save_trades_metrics({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price, 'amount': q*current_asset_price})
    elif side == 'sell':
        # checkqty(symbol, q)
        # q = min(q, qty[symbol])
        if q > qty[symbol]:
            # temp = (q - qty[symbol]) * current_asset_price
            # temp = qty[symbol]*current_asset_price
            q = qty[symbol]
        if q*current_asset_price >= 5:
            temp = q*current_asset_price
            qty[symbol] = qty[symbol] - q
            cash = cash + q*current_asset_price*0.999
            trades.append({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price})
            save_trades_metrics({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price, 'amount': q*current_asset_price})
        else:
            temp = 0
    return temp
        

def multiPlaceOrder(amount):
    temp = 0
    # totalTemp = 0
    for asset in assets:
        temp += placeOrder(asset, amount*weights[assets.index(asset)])
        # amountT = amountT - (amount*weights[assets.index(asset)] - temp)
        # totalTemp = totalTemp + temp
    return temp
def rebalanceF(risk_alloc, safe_alloc):
    temp = 0
    if risk_alloc - getAllRiskyAssetsValue() > 0:
        temp = placeOrder(safeAsset, safe_alloc - getSafeAssetValue())
        multiPlaceOrder(risk_alloc - getAllRiskyAssetsValue() + temp)
    else:
        temp = multiPlaceOrder(risk_alloc - getAllRiskyAssetsValue())
        placeOrder(safeAsset, safe_alloc - getSafeAssetValue() + temp)
        
def rebalance(risk_alloc, safe_alloc):
    temp = 0
    
    # if position_value is None:
    if risk_alloc - getAllRiskyAssetsValue() > 0:
        # if safeAsset is not None: 
        temp = placeOrder(safeAsset, safe_alloc - getSafeAssetValue())
        # print(temp)
        multiPlaceOrder(temp)
        # multiPlaceOrder(risk_alloc + temp)
    else:
        temp = multiPlaceOrder(risk_alloc - getAllRiskyAssetsValue())
        # if safeAsset is not None:
        placeOrder(safeAsset, temp)
        # placeOrder(safeAsset, safe_alloc + temp)
    # else:
    #     excess_risk_alloc = risk_alloc - position_value[0] 
    #     excess_safe_alloc = safe_alloc - position_value[1]

    #     if safeAsset is not None:
    #         placeOrder(safeAsset, excess_safe_alloc - getSafeAssetValue())  
    #     if abs(excess_risk_alloc) > 0:
    #         multiPlaceOrder(excess_risk_alloc - getAllRiskyAssetsValue())
            
def AvgEntryPrice(symbol):
    total_qty = 0
    total_cost = 0
    
    for trade in trades:
        if trade['side'] == 'buy' and trade['symbol'] == symbol:
            total_qty += trade['q']
            total_cost += trade['q'] * trade['price']
            
    if total_qty == 0:
        return None
        # return 0
        
    return total_cost / total_qty

def getPositionValue(symbol):
    value, returns = None, None

    try:
        returns = getLastPrice(symbol)/AvgEntryPrice(symbol) - 1
        value = getLastPrice(symbol)*qty[symbol]
    
    except Exception as e:
        pass

    return value, returns

def CheckPosition():
    totalValue = 0
    totalReterns = 0
    for asset in assets:
        value, returns = getPositionValue(asset)
        if value is not None:
            totalValue += value
            totalReterns += returns * value
    if totalValue is not None:
        totalReterns = totalReterns/totalValue
        if safeAsset is not None:
            s_value, s_reterns = getPositionValue(safeAsset)
            if s_value is not None:
                position_value = [totalValue, s_value]
                
        else:
            position_value = [totalValue, 0]
            s_reterns = 0
            
    elif safeAsset is not None:
        s_value, s_reterns = getPositionValue(safeAsset)
        if s_value is not None:
            position_value = [0, s_value]
            totalReterns = 0
        
    else:
        position_value = None
        totalReterns = 0
        s_reterns = 0
    if totalReterns is None:
        totalReterns = 0
    if s_reterns is None:
        s_reterns = 0
    return totalReterns, s_reterns

def save_cppi_metrics():
    with open(savefile, 'a', newline='') as file:
        wr = csv.writer(file)
        wr.writerow([cppi_value, floor_value])
        
def save_trades_metrics(trade):
    with open(tradesfile, 'a', newline='') as file:
        wr = csv.writer(file)
        wr.writerow([trade['side'],trade['symbol'],trade['q'],trade['price'], trade['amount']])
        # wr.writerow([cash, qty[trade['symbol']]])

data = getData()
# print(data)
# sva data to a csv file
# for symbol in assets:
#     data[symbol].to_csv(symbol + '.csv')
# data[safeAsset].to_csv(safeAsset + '.csv')
# print(length)

while timelaps < length - 1 and cppi_value > floor_value:
    print(timelaps)
    max_cppi_value = max(max_cppi_value, cppi_value)
    floor_value = max_cppi_value*floor_percent
    
    cushion = cppi_value - floor_value
    
    riskAlloc = max(min(m*cushion, cppi_value), 0)
    safeAlloc = cppi_value - riskAlloc
    # print('gew: ' + str(riskAlloc) + ' : ' + str(safeAlloc))
    
    if timelaps == 0:
        rebalanceF(risk_alloc=riskAlloc, safe_alloc=safeAlloc)
        riskpreval = getAllRiskyAssetsValue()
    else:
        if abs((getAllRiskyAssetsValue() - riskpreval) / riskpreval) > 0.005:
            rebalance(risk_alloc=riskAlloc, safe_alloc=safeAlloc)
            riskpreval = getAllRiskyAssetsValue()
    
    # next
    timelaps = timelaps+1
    
    # r_ret, s_ret = CheckPosition()
    # print('sw:', r_ret, ':', s_ret)
    s_ret = 0
    # cppi_value = riskAlloc*(1 + r_ret) + safeAlloc*(1 + s_ret)
    cppi_value = getTotalValue()
    # print("llla: ", getTotalValue())
    # print(qty)
    save_cppi_metrics()