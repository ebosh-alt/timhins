import requestsimport datetimefrom typing import NamedTupleclass Result(NamedTuple):    from_whom: list = []    to: list = []    time: list = []class Time(NamedTuple):    hours: int    minutes: intclass Setting(NamedTuple):    hours: int    minutes: intdef get_time_trans(data: Result, wallet: str):    ind = data.to.index(wallet)    time = data.time[ind].split(" ")[1].split(":")    time = (int(time[0]), int(time[1]))    time_trans = Time(hours=int(time[0]), minutes=int(time[1]))    return time_transdef connect():    api_key = "X38NMTYXS9X3PDGI4VZFV8UP6F3B4R5ZE1"    contract_adress = "0xf3a3d1B89A70E291531ECB4a1299117f5dE44612".lower()    adress = "0x6336d922a96742e3E57306C4741E3dFCdc8D601f".lower()    url = f"https://api.polygonscan.com/api?module=account&action=tokentx&" \          f"address={contract_adress}&" \          f"startblock=0&endblock=99999999&page=1&offset=3000&sort=desc&apikey={api_key}"    data = requests.get(url=url)    return datadef check() -> bool | dict:    data = connect()    if data.status_code == 200:        data = data.json()        if data["message"] == 'No transactions found':            return False        else:            return data["result"]    else:        return Falsedef processing() -> Result:    data = check()    if data is not False:        data_tuple = Result()        for trans in data:            data_tuple.from_whom.append(trans["from"])            data_tuple.to.append(trans["to"])            ts = int(trans["timeStamp"])            time = datetime.datetime.fromtimestamp(ts).strftime('%Y.%m.%d %H:%M:%S')            data_tuple.time.append(time)            app_to_file(data=data_tuple)        return data_tupledef check_for_in_wallet(wallet: str, data: Result):    if wallet in data.to:        return True    else:        return Falsedef check_for_in_time(wallet: str, time: int):    data = processing()    if check_for_in_wallet(wallet=wallet, data=data):        time_trans = get_time_trans(data=data, wallet=wallet)        cur_time = Time(hours=int(datetime.datetime.now().strftime("%H")),                        minutes=int(datetime.datetime.now().strftime("%M")))        cur_time = cur_time.hours * 60 + cur_time.minutes        time_trans = time_trans.hours * 60 + time_trans.minutes        if cur_time - time_trans <= time:            return True    else:        return Falsedef app_to_file(data: Result = None):    if data is None:        data = processing()    txt = ""    for i in range(len(data.from_whom)):        txt += f"от кого: {data.from_whom[i]}\n" \               f"кому: {data.to[i]}\n" \               f"когда: {data.time[i]}\n\n"    with open("info_api.txt", "w+") as f:        f.write(txt)def polygon_scan(wallet: str, time: int):    setting = Setting(hours=time // 60, minutes=time % 60)    check = check_for_in_time(wallet=wallet,                              time=time)    if check:        return Trueif __name__ == "__main__":    polygon_scan(wallet="0x4d3e2bfd49d4f0aed702d4b2c4472ef485d06780",                     time=50)