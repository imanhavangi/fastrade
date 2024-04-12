from binance.spot import Spot
import os
import csv
import datetime
import math
import time

api_key = "cyGsKJY8h8DVrim7YVFPBNzZ1vL7krfF6Byoo9ZOYvz5dnIU3LjAFDt4UNSNV8Tm" 
api_secret = "JuZSZyF7gZatYcdQpYWwXoCIwBEYdNDOqCMZTvIkco8WOIfXu8iYVf5z6unRVgW7"
client = Spot(api_key=api_key, api_secret=api_secret)
# Get account information
info = client.account()

cash = 0
riskpreval = 0
assets = ['BTC', 'BNB','ETH','XRP','DOGE','LINK','COMP','LPT','LDO','SOL','RNDR','SUSHI','SNX','OP','AVAX','AAVE','INJ','GRT','GMX']
safeAsset = 'USDT'
weights = [0.060387,0.087913,0.068746,0.096713,0.040282,0.052227,0.052104,0.036301,0.052466,0.053000,0.040018,0.028168,0.057930,0.029553,0.052711,0.050654,0.062039,0.058758,0.020030]
# print(sum(weights))
if sum(weights) != 1:
    raise Exception("Sum of weights is not 1")

interval = "1h"
floor_percent = 0.90
m = 4

def updateInfo():
    global info
    info = client.account()

def getLastPrice(symbol):
    updateInfo()
    return float(client.ticker_price(symbol+'USDT')['price'])

# print(getLastPrice('BTC'))
# for asset in assets:
#     print(asset)
#     print(getLastPrice(asset))

def getLastCount(symbol):
    updateInfo()
    for bal in info['balances']:
        if (bal['asset'] == symbol):
            return float(bal['free'])
        
# print(getLastCount('BTC'))

def getTotalValue():
    updateInfo()
    total_usd = 0
    for bal in info['balances']:
        if float(bal['free']) > 0:
            try:
                if (bal['asset'] in assets):
                    price = float(client.ticker_price(bal['asset']+'USDT')['price'])
                    count = float(bal['free'])
                    total_usd += price * count
                    # print(bal['asset'], " : " , price*count)
                elif (bal['asset'] == 'USDT'):
                    total_usd += float(bal['free'])
                    # print(bal['asset'], " : " , float(bal['free']))
            except:
                pass
    return total_usd

# print(getTotalValue())

def getCash():
    updateInfo()
    for bal in info['balances']:
        if bal['asset'] == 'USDT':
            return float(bal['free'])

print(getCash())

def getAllRiskyAssetsValue():
    updateInfo()
    total_usd = 0
    for bal in info['balances']:
        if float(bal['free']) > 0:
            try:
                if (bal['asset'] != 'USDT'):
                    price = float(client.ticker_price(bal['asset']+'USDT')['price'])
                    count = float(bal['free'])
                    total_usd += price * count
            except:
                pass
    return total_usd

# print(getAllRiskyAssetsValue())

def printLastStatus():
    updateInfo()
    total_usd = 0
    for bal in info['balances']:
        if float(bal['free']) > 0:
            try:
                if (bal['asset'] in assets):
                    price = float(client.ticker_price(bal['asset']+'USDT')['price'])
                    count = float(bal['free'])
                    total_usd += price * count
                    print(bal['asset'], " | price:" , price, " | count:", count, " | total:", price*count)
                elif (bal['asset'] == 'USDT'):
                    total_usd += float(bal['free'])
                    print(bal['asset'], " | total:" , float(bal['free']))
            except:
                pass
    print("final total: ", total_usd)
  
def getSells():
    updateInfo()
    total_usd = 0
    sells = []
    for bal in info['balances']:
        if float(bal['free']) > 1:
            if bal['asset'] != 'BNB' and bal['asset'] != 'USDT' and bal['asset'] != 'QISWAP':
                sells.append(bal['asset'])
    return sells

def convert(num, symbol):
    minx = 1
    if symbol == 'BTC':
        minx = 0.00001
    elif symbol == 'ETH':
        minx = 0.0001
    elif symbol == 'LINK' or symbol == 'SOL' or symbol == 'AVAX' or symbol == 'AAVE' or symbol == 'GMX':
        minx = 0.01
    elif symbol == 'BNB' or symbol == 'COMP' or symbol == 'LPT' or symbol == 'INJ':
        minx = 0.1
    else:
        minx = 1
    
    min_val = minx
    max_val = 100000.0
    step_size = minx
    num = math.floor(num / step_size) * step_size
    num = min(max_val, max(min_val, num))
    num = round(num, 6)
    return num

def placeOrder(symbol, amount):
    cash = getCash()
    temp = 0
    if amount == 0:
        return 0
    if abs(amount) < 2.5:
        return 0
    # amount = math.floor(amount * 100) / 100
    side = 'null'
    if amount > 0:
        side = 'BUY'
    elif amount < 0:
        side = 'SELL'
        
    if abs(amount) < 5:
        if side == 'SELL':
            temp = 5
            amount = -5
        else:
            amount = 5
            
        
    current_asset_price = getLastPrice(symbol)
    q = abs(amount) / current_asset_price
    q = convert(q, symbol)
    
    print("trade | side:", side, " | symbol:", symbol, " | q:", q, " | amount:", amount)

    if side == 'BUY':
        if cash < amount:
            return 0
        # cash = cash - q*current_asset_price*1.001
        # qty[symbol] = qty[symbol] + q
        order = client.new_order(
            symbol= symbol+'USDT',
            side='BUY',
            type='MARKET',
            quantity=q
        )
        print(order)
        # trades.append({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price})
        # save_trades_metrics({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price, 'amount': q*current_asset_price})
    elif side == 'SELL':
        if q > getLastCount(symbol):
            q = getLastCount(symbol)
        if q*current_asset_price >= 5:
            temp = q*current_asset_price
            # qty[symbol] = qty[symbol] - q
            # cash = cash + q*current_asset_price*0.999
            order = client.new_order(
                symbol= symbol+'USDT',
                side='SELL',
                type='MARKET',
                quantity=q
            )
            print(order)
            # trades.append({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price})
            # save_trades_metrics({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price, 'amount': q*current_asset_price})
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
        
def rebalance(risk_alloc, safe_alloc):
    multiPlaceOrder(risk_alloc - getAllRiskyAssetsValue())
    
cash = getCash()
cppi_value = cash
floor_value = cash * floor_percent
max_cppi_value = cash
t = 0

printLastStatus()
# sells = getSells()
# for sell in sells:
#     print(sell , " | " , getLastCount(sell))
#     client.new_order(
#         symbol= sell+'USDT',
#         side='SELL',
#         type='MARKET',
#         quantity= getLastCount(sell)
#     )
    

# while cppi_value > floor_value:
#     max_cppi_value = max(max_cppi_value, cppi_value)
#     floor_value = max_cppi_value*floor_percent
    
#     cushion = cppi_value - floor_value
    
#     riskAlloc = max(min(m*cushion, cppi_value), 0)
#     safeAlloc = cppi_value - riskAlloc
    
#     if t == 0:
#         rebalance(risk_alloc=riskAlloc, safe_alloc=safeAlloc)
#         time.sleep(30)
#         riskpreval = getAllRiskyAssetsValue()
#         t = 1
#     else:
#         if abs((getAllRiskyAssetsValue() - riskpreval) / riskpreval) > 0.005:
#             rebalance(risk_alloc=riskAlloc, safe_alloc=safeAlloc)
#             time.sleep(30)
#             riskpreval = getAllRiskyAssetsValue()
    
#     cppi_value = getTotalValue()
    
#     printLastStatus()
#     time.sleep(30)