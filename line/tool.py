from datetime import datetime, timedelta
import pytz  # Import the pytz library for timezone handling

# Set the timezone you want to use
desired_timezone = pytz.timezone('Asia/Taipei')

# 判斷會有幾個 flex_message
def check_flex_message_count(count):
    # 取整數
    take_integer = count // 10
    # 取餘數 (備註: 4 % 10 = 4)
    take_remainder = count % 10

    # 小於10
    if count < 10:
        carousel_count = 1
    # 10的倍數(若有10個還是算一個flex_message)
    elif take_remainder == 0:
        carousel_count = take_integer
    # 大於10且不是10倍數
    else:
        carousel_count = take_integer + 1
    
    return carousel_count

# 取得本月最後一天日期
def last_day_of_this_month():
    today = datetime.now(desired_timezone)
    first_day_of_month = today.replace(day=1)
    first_day_of_next_month = (first_day_of_month + timedelta(days=32)).replace(day=1)
    last_day_of_month = first_day_of_next_month - timedelta(days=1)
    return last_day_of_month.day

# 取得下個月最後一天日期
def last_day_of_next_month():
    today = datetime.now(desired_timezone)
    first_day_of_month = today.replace(day=1)
    first_day_of_next_month = (first_day_of_month + timedelta(days=32)).replace(day=1)
    first_day_of_next_2month = (first_day_of_next_month + timedelta(days=32)).replace(day=1)
    last_day_of_next_month = first_day_of_next_2month - timedelta(days=1)
    return last_day_of_next_month.day

# 檢查可預約時段有沒有跳月
def reservation_period_check(today, period):
    last_day_of_month = last_day_of_this_month()
    if last_day_of_month - today >= period:
        calendar_count =  1
        last_day_of_reservation = today + period
    else:
        calendar_count = 2
        last_day_of_reservation = period - (last_day_of_month - today)
    
    # 回傳: 需要日曆的數量，最後一天的預約日期
    return calendar_count, last_day_of_reservation

#  datetime.now().weekday()
#  星期一 = 0, 星期二 = 1, ...星期日 = 6
weekday_index = {
        0: 1,
        1: 2,
        2: 3,
        3: 4,
        4: 5,
        5: 6,
        6: 0,
    }

# 本月日曆格式
def this_month_calendar_format():
    weekday_of_first_day = datetime.now(desired_timezone).replace(day=1).weekday()
    first_day_index = weekday_index[weekday_of_first_day]

    # 回傳: 首日的 index，本月最後一天日期
    return first_day_index, last_day_of_this_month()

# 下個月日曆格式
def next_month_calendar_format():
    first_day_of_next_month = datetime.now(desired_timezone).replace(day=1)
    weekday_of_first_day = (first_day_of_next_month + timedelta(days=32)).replace(day=1).weekday()
    first_day_index = weekday_index[weekday_of_first_day]
    
    # 回傳: 首日的 index，下個月最後一天日期
    return first_day_index, last_day_of_next_month()

week_name_change = {
    "星期一": 0,
    "星期二": 1,
    "星期三": 2,
    "星期四": 3,
    "星期五": 4,
    "星期六": 5,
    "星期日": 6,
}

# 取得輸入的 (年、月) 的下一個月的 (年、月)
def get_year_month_of_next_month(year, month):
    # 构造当前日期
    current_date = datetime(year, month, 1)
    
    # 加一个月
    next_month_date = current_date + timedelta(days=32)
    
    # 获取年份和月份
    next_year = next_month_date.year
    next_month = next_month_date.month
    
    return next_year, next_month

# 取得本月所有星期幾日期
# 若取 2024/5 所有星期一日期 return [6, 13, 20, 27]
def get_all_weekday_in_month(state, day_index):
    current_year = datetime.now(desired_timezone).year
    current_month = datetime.now(desired_timezone).month
    if state == "this month":
        # 获取当前年份和月份
        year = current_year
        month = current_month
    else:
        year, month = get_year_month_of_next_month(current_year, current_month)
    
    # 获取本月第一天的日期
    first_day_of_month = datetime(year, month, 1)
    
    # 找到本月第一个符合条件的日期
    if first_day_of_month.weekday() == day_index:
        days_list = [first_day_of_month]
    elif first_day_of_month.weekday() < day_index:
        days_to_add = day_index - first_day_of_month.weekday()
        days_list = [first_day_of_month + timedelta(days=days_to_add)]
    else:
        days_to_add = 7 - (first_day_of_month.weekday() - day_index)
        days_list = [first_day_of_month + timedelta(days=days_to_add)]
    
    # 循环找到剩余的符合条件的日期
    current_date = days_list[0]
    while current_date.month == month:
        current_date += timedelta(days=7)
        if current_date.month == month:
            days_list.append(current_date)
            
    reset_day_list = []
    
    # 打印结果
    for monday in days_list:
        reset_day_list.append(int(monday.strftime("%d")))
    
    return reset_day_list

day_index = week_name_change["星期一"]
reset_day_list = get_all_weekday_in_month("next month", day_index)
    
print(reset_day_list)

# ====================================
# can_reservation_list_event
# 把數字轉成時間 480 -> '08:00'
def parse_num_to_time(schedule_time):
    hour = schedule_time // 60
    minute = schedule_time % 60
    
    hour_modify = hour if hour >= 10 else f'0{hour}'
    minute_modify = minute if minute >= 10 else f'0{minute}'
    return f'{hour_modify}:{minute_modify}'
    
# 把數字轉成時間 '08:00' -> 480
def parse_time_to_num(schedule_time):
    num_list = schedule_time.split(':')
    hour = int(num_list[0]) * 60
    minute = int(num_list[1])
    return hour + minute

# 把時間轉成數字
# ['08:00', '09:30', '11:00'] -> [480, 570, 660]
def parse_time_list_to_num_list(data):
    output = list(map(parse_time_to_num, data))

    return output

# 把 "fix_time": "08,00,01,30,21,00" 轉成 ['08:00', '09:30', '11:00', ..., '20:00']
def parse_fix_time_to_time_list(admin_data, schedule_data):
    admin_can_reservation = admin_data.can_reservation_time.split(',')
    admin_start = int(admin_can_reservation[0]) * 60  + int(admin_can_reservation[1])
    admin_end = int(admin_can_reservation[2]) * 60  + int(admin_can_reservation[3])
    
    fix_time = schedule_data.get('fix_time').split(',')
    fix_start = int(fix_time[0]) * 60 + int(fix_time[1])
    fix_end = int(fix_time[4]) * 60 + int(fix_time[5])
    fix_interval = int(fix_time[2]) * 60 + int(fix_time[3])
    fix_time_cancel = schedule_data.get('fix_time_cancel')

    # 先判斷有無取消 fix_time
    if not fix_time_cancel:
        # 先把範圍內時間存進 list
        # time_num_list = [480, 570, 660, 750, 840, 930, 1020, 1110, 1200]
        time_num_list = []
        while True:
            if fix_start > fix_end:
                break
            time_num_list.append(fix_start)
            fix_start += fix_interval
    
        # 如果 fix_time 時間不在 admin_can_reservation 之內就刪除
        time_num_list = list(filter(lambda x: admin_start <= x <= admin_end, time_num_list))
        
        # 刪掉 fix_time_delete
        fix_time_delete = schedule_data.get('fix_time_delete').split(',') \
            if schedule_data.get('fix_time_delete') else []
        fix_time_delete_list = parse_time_list_to_num_list(fix_time_delete)
        time_num_list = list(filter(lambda x: x not in fix_time_delete_list, time_num_list))
    else:
        time_num_list = []
    
    # 增加 flex_time
    flex_time = schedule_data.get('flex_time').split(',') \
        if schedule_data.get('flex_time') else []
    flex_time_list = parse_time_list_to_num_list(flex_time)
    time_num_list.extend(flex_time_list)

    # 若是在今天的時段，會消除現在時間 + 當日顧客預約限制(admin.today_reservation_limit)前的預約
    today = datetime.now(desired_timezone).strftime("%Y/%m/%d")
    date = schedule_data.get('date').split(" ")[0]

    if today == date:
        admin_today_reservation_limit = int(admin_data.today_reservation_limit)
        today_time = datetime.now(desired_timezone).strftime("%H:%M").split(':')
        hour = int(today_time[0]) * 60
        minute = int(today_time[1])
        today_reservation_limit = hour + minute + admin_today_reservation_limit * 60
        time_num_list = list(filter(lambda x : x > today_reservation_limit, time_num_list))

    # 全部重新排列(由小到大)
    time_num_list.sort()
    
    # 轉成時間
    # ['08:00', '09:30', '11:00', '12:30', '14:00', '15:30', '17:00', '18:30', '20:00']
    output = list(map(parse_num_to_time, time_num_list))
    return output

# 解析指定預約
def parse_schedule(admin_data, schedule_data, common_data):
    # 先檢查是否有使用 common_setting
    if schedule_data.get('common_setting_id') == 0:
        data = schedule_data
    else:
        for common in common_data:
            if common['id'] == schedule_data.get('common_setting_id'):
                data = common
                # common_data 裡面沒有 date，要補加入
                data['date'] = schedule_data.get('date')
    
    output = parse_fix_time_to_time_list(admin_data, data)
    return output
      
# 預期輸出
# ['08:00', '10:30', '11:30', '12:00'] -> [['08:00', '10:30'], ['13:00']]
# ['08:00', '10:30', '11:30', '12:00', '13:00'] -> [['08:00', '10:30'], ['11:30', '12:00'], ['13:00', '']]
def parse_two_pair_list(time_list):
    two_pair_list = []
    two_pair = []
    time_list_count = len(time_list)
    
    for i, t in enumerate(time_list, start=1):
        two_pair.append(t)
        if i % 2 == 0:
            two_pair_list.append(two_pair)
            two_pair = []
        
        # 當為 time_list_count 基數個 且 i是最後一個
        if time_list_count % 2 != 0 and i == time_list_count:
            two_pair_list.append([t, ""])
            
    return two_pair_list


# flex_message
def text_bubble(text, size=None):
    if size:
        size = size
    elif len(text) <= 6:
        size = "nano"
    elif len(text) <= 8:
        size = "micro"
    elif len(text) <= 12:
        size = "deca"
    elif len(text) == 13:
        size = "hecto"
    else:
        size = "kilo"

    bubble = {
  "type": "bubble",
  "size": size,
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "wrap": True,
        "text": text,
        "color": "#000000"
      }
    ],
    "paddingTop": "md",
    "paddingBottom": "md"
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca",
      "separator": True,
      "separatorColor": "#b3b3b3"
    }
  }
}
    return bubble

def confirm_bubble(text):
    pass




