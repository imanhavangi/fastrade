import os
import csv
import yfinance as yf
import datetime
import math
import motor.motor_asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from models.backtest import BackTest
from models.backdata import BackData
from models.live import Live
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler



client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URI"])
db = client.myTestDB

app = FastAPI()
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# qty = {}
# trades = []
# data_dict = {}

def testcron(id):
    print(id)

scheduler = BackgroundScheduler()
liveScheduler = AsyncIOScheduler()
# scheduler.add_job(testcron, 'interval', args=["chi"] , seconds=5, id="job1")
scheduler.add_job(testcron, 'interval', args=["sih"] , seconds=10)
# scheduler.add_job(testcron, 'interval', "shi" , minutes=10)
scheduler.start()
liveScheduler.start()

backdata = BackData
livedata = Live

@app.post("/live")
async def live(backtest: BackTest):
    global livedata
    livedata = Live.from_backtest(backtest=backtest)

    print(livedata.toJSON())
    livedb = await db["lives"].insert_one(livedata.toJSON())
    liveScheduler.add_job(liveCycle, 'interval', seconds=int(livedata.interval), args=[livedb.inserted_id], id=str(livedb.inserted_id))
    # scheduler.add_job(testcron, 'interval', args=["chi"] , seconds=10)
    # scheduler.restart()
    return {"message": "Signup successful", "_id": str(livedb.inserted_id)}

    # while live.cppi_value > live.floor_value:
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

async def liveCycle(id):
    print(id)
    datalive = await db["lives"].find_one({"_id": id})
    live = Live(**datalive)
    # print(live)
    if live.cppi_value > live.floor_value:
        

@app.post("/backtest")
async def backTest(backtest: BackTest):
    global backdata
    backdata = BackData.from_backtest(backtest=backtest)
    getData()
    print(backdata.length)
    print(backdata.cppi_value)
    print(backdata.floor_value)


    while backdata.timelaps < backdata.length - 1 and backdata.cppi_value > backdata.floor_value:
        # print(backdata.timelaps)
        backdata.max_cppi_value = max(backdata.max_cppi_value, backdata.cppi_value)
        backdata.floor_value = backdata.max_cppi_value * backdata.floor_percent
        
        cushion = backdata.cppi_value - backdata.floor_value
        
        riskAlloc = max(min(backdata.m * cushion, backdata.cppi_value), 0)
        safeAlloc = backdata.cppi_value - riskAlloc
        if (backdata.timelaps < 50):
            print('gew: ' + str(riskAlloc) + ' : ' + str(safeAlloc))
        
        if backdata.timelaps == 0:
            rebalanceF(risk_alloc=riskAlloc, safe_alloc=safeAlloc)
            backdata.riskpreval = getAllRiskyAssetsValue()

        else:
            if (backdata.timelaps < 50):
                print(getAllRiskyAssetsValue() , " d|d ", backdata.riskpreval, " d|d ", backdata.changes_percent)
            if abs((getAllRiskyAssetsValue() - backdata.riskpreval) / backdata.riskpreval) > backdata.changes_percent:
                rebalance(risk_alloc=riskAlloc, safe_alloc = safeAlloc)
                backdata.riskpreval = getAllRiskyAssetsValue()
        
        # next
        backdata.timelaps = backdata.timelaps + 1
        
        # r_ret, s_ret = CheckPosition()
        # print('sw:', r_ret, ':', s_ret)
        s_ret = 0
        # cppi_value = riskAlloc*(1 + r_ret) + safeAlloc*(1 + s_ret)
        backdata.cppi_value = getTotalValue()
        # print("llla: ", getTotalValue() , ", ", backdata.timelaps )

        # print(qty)
        # save_cppi_metrics()

    return {"result": "Backtesting completed.", "balance": getTotalValue(), "trades": backdata.trades}


    # submitted_task = await db["tasks"].insert_one(task.toJSON())

    # data = task.toJSON()
    # data["_id"] = str(submitted_task.inserted_id)
    # for connection in websocket_connections.copy():
    #     try:
    #         # if connection[0] in task.assign_user_ids:
    #         await connection[1].send_json({"event": "new_task", "task": data})
    #     except WebSocketDisconnect:
    #         websocket_connections.remove(connection)
    # return {"message": "Task submitted successfully", "task": data}



def getData():
    global backdata
    ticker_data = yf.Ticker(backdata.safe)
    
    # use period
    # ticker_df = ticker_data.history(period=period, interval=interval)
    # use timelaps
    ticker_df = ticker_data.history(start=backdata.start, end=backdata.end, interval=backdata.interval)
    
    backdata.data[backdata.safe] = ticker_df
    length = len(ticker_df)
    
    for asset in backdata.assets:
        ticker_data = yf.Ticker(asset.symbol)
        ticker_df = ticker_data.history(start=backdata.start, end=backdata.end, interval=backdata.interval)
        backdata.data[asset.symbol] = ticker_df
        # print(len(ticker_df))
        length = min(length, len(ticker_df))
    # print(backdata.data)
    backdata.length = length

# def getLastPrice(symbol):
#     data = getData()
#     last_price = data[symbol].iloc[-1]['Close']
#     return last_price

def getLastPrice(symbol):
    # print(symbol)
    # print(backdata.data)
    last_price = backdata.data[symbol].iloc[backdata.timelaps]['Close']
    return last_price
 
# def getCash():
#     return cash

def getTotalValue():
    total_value = 0
    total_value += backdata.cash
    twst = 0
    for asset in backdata.assets:
        total_value += getLastPrice(asset.symbol) * backdata.qty[asset.symbol]
        # print (symbol, " : ", getLastPrice(symbol) , " : ", qty[symbol] , " : ", getLastPrice(symbol) * qty[symbol])
        twst += getLastPrice(asset.symbol) * backdata.qty[asset.symbol]
    total_value += getLastPrice(backdata.safe) * backdata.qty[backdata.safe]
    
    # print(total_value , " : ", getCash() , " : ", twst, " : ", getLastPrice(backdata.safe) * qty[backdata.safe])
    return total_value

def checkBudget(requiredCash:float):
    availableCash = backdata.cash
    if requiredCash > availableCash:
        raise Exception("Not enough available cash")

def checkqty(symbol, q):
    if q > backdata.qty[symbol]:
        raise Exception("Not enough available quantity")
    
def getAllRiskyAssetsValue():
    total_value = 0
    for asset in backdata.assets:
        # if (backdata.timelaps < 50):
            # print(getLastPrice(asset.symbol) , " |asdsd| " , backdata.qty[asset.symbol])
        total_value += getLastPrice(asset.symbol) * backdata.qty[asset.symbol]
    return total_value

def getsafeAssetValue():
    return getLastPrice(backdata.safe) * backdata.qty[backdata.safe]

def placeOrder(symbol, amount):
    global backdata
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
    print('de1:' , amount , " : " , symbol , ' : ', q , " : ", backdata.cash , ' : ', side)
    

    if side == 'buy':
        print("asdasdasd")
        if backdata.cash < amount:
            return 0
        print("asdasdasd2")
        backdata.cash = backdata.cash - q*current_asset_price
        print("asdasdasd3  ", q)
        backdata.qty[symbol] = backdata.qty[symbol] + q*0.999
        print(backdata.qty)
        backdata.trades.append({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price})
        # save_trades_metrics({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price, 'amount': q*current_asset_price})
    elif side == 'sell':
        # checkqty(symbol, q)
        # q = min(q, qty[symbol])
        if q > backdata.qty[symbol]:
            # temp = (q - qty[symbol]) * current_asset_price
            # temp = qty[symbol]*current_asset_price
            q = backdata.qty[symbol]
        if q*current_asset_price >= 5:
            temp = q*current_asset_price
            backdata.qty[symbol] = backdata.qty[symbol] - q*1.001
            backdata.cash = backdata.cash + q*current_asset_price
            backdata.trades.append({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price})
            # save_trades_metrics({'side': side, 'symbol': symbol, 'q': q, 'price': current_asset_price, 'amount': q*current_asset_price})
        else:
            temp = 0
    return temp
        

def multiPlaceOrder(amount):
    temp = 0
    # totalTemp = 0
    for asset in backdata.assets:
        print(asset.weight)
        temp += placeOrder(asset.symbol, amount*(asset.weight/100))
        # amountT = amountT - (amount*weights[assets.index(asset)] - temp)
        # totalTemp = totalTemp + temp
    return temp
def rebalanceF(risk_alloc, safe_alloc):
    temp = 0
    if risk_alloc - getAllRiskyAssetsValue() > 0:
        temp = placeOrder(backdata.safe, safe_alloc - getsafeAssetValue())
        multiPlaceOrder(risk_alloc - getAllRiskyAssetsValue() + temp)
    else:
        price("place risk")
        temp = multiPlaceOrder(risk_alloc - getAllRiskyAssetsValue())
        placeOrder(backdata.safe, safe_alloc - getsafeAssetValue() + temp)
        
def rebalance(risk_alloc, safe_alloc):
    temp = 0
    
    # if position_value is None:
    if risk_alloc - getAllRiskyAssetsValue() > 0:
        # if backdata.safe is not None: 
        temp = placeOrder(backdata.safe, safe_alloc - getsafeAssetValue())
        # print(temp)
        multiPlaceOrder(temp)
        # multiPlaceOrder(risk_alloc + temp)
    else:
        temp = multiPlaceOrder(risk_alloc - getAllRiskyAssetsValue())
        # if backdata.safe is not None:
        placeOrder(backdata.safe, temp)
        # placeOrder(backdata.safe, safe_alloc + temp)
    # else:
    #     excess_risk_alloc = risk_alloc - position_value[0] 
    #     excess_safe_alloc = safe_alloc - position_value[1]

    #     if backdata.safe is not None:
    #         placeOrder(backdata.safe, excess_safe_alloc - getsafeAssetValue())  
    #     if abs(excess_risk_alloc) > 0:
    #         multiPlaceOrder(excess_risk_alloc - getAllRiskyAssetsValue())
            
def AvgEntryPrice(symbol):
    total_qty = 0
    total_cost = 0
    
    for trade in backdata.trades:
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
        value = getLastPrice(symbol)*backdata.qty[symbol]
    
    except Exception as e:
        pass

    return value, returns

def CheckPosition():
    global backdata
    totalValue = 0
    totalReterns = 0
    for asset in backdata.assets:
        value, returns = getPositionValue(asset.symbol)
        if value is not None:
            totalValue += value
            totalReterns += returns * value
    if totalValue is not None:
        totalReterns = totalReterns/totalValue
        if backdata.safe is not None:
            s_value, s_reterns = getPositionValue(backdata.safe)
            if s_value is not None:
                backdata.position_value.totalValue = totalValue
                backdata.position_value.s_value = s_value
                
        else:
            backdata.position_value.totalValue = totalValue
            backdata.position_value.s_value = 0
            # position_value = [totalValue, 0]
            s_reterns = 0
            
    elif backdata.safe is not None:
        s_value, s_reterns = getPositionValue(backdata.safe)
        if s_value is not None:
            backdata.position_value.totalValue = 0
            backdata.position_value.s_value = s_value
            # position_value = [0, s_value]
            totalReterns = 0
        
    else:
        backdata.position_value = None
        totalReterns = 0
        s_reterns = 0
    if totalReterns is None:
        totalReterns = 0
    if s_reterns is None:
        s_reterns = 0
    return totalReterns, s_reterns

# def save_cppi_metrics():
#     with open(savefile, 'a', newline='') as file:
#         wr = csv.writer(file)
#         wr.writerow([cppi_value, floor_value])
        
# def save_trades_metrics(trade):
#     with open(tradesfile, 'a', newline='') as file:
#         wr = csv.writer(file)
#         wr.writerow([trade['side'],trade['symbol'],trade['q'],trade['price'], trade['amount']])
        # wr.writerow([cash, qty[trade['symbol']]])
