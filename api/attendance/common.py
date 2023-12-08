from datetime import datetime, time, date


def time_diff(time1, time2):  # time2 - time1
    fulldate_time1 = datetime(100, 1, 1, time1.hour, time1.minute, time1.second)
    fulldate_time2 = datetime(100, 1, 1, time2.hour, time2.minute, time2.second)
    result = (fulldate_time2 - fulldate_time1)
    result = result.seconds
    result_hour = int(result / 3600)
    result_minute = int((result % 3600) / 60)
    result_second = int(result % 60)
    return time(result_hour, result_minute, result_second)


def cal_workTime(last_attendance):
    work_time = time_diff(last_attendance.attendanceTime, last_attendance.offworkTime)
    if last_attendance.attendanceTime <= time(12, 30, 0) and last_attendance.offworkTime.time() < time(6, 0, 0):  # 0시 이후~오전 6시 이전 퇴근
        work_time = time_diff(time(1, 0, 0), work_time)
    elif last_attendance.attendanceTime <= time(12, 30, 0) and last_attendance.offworkTime.time() >= time(13, 30, 0):
        work_time = time_diff(time(1, 0, 0), work_time)
    return work_time


def cal_workTime_check(last_attendance): #근무시간 8시간 이상인지 체크 후, 지각 None처리
    if last_attendance.workTime.replace(second=0, microsecond=0) >= time(8,0,0):
        last_attendance.latenessTime = None


def DayOfTheWeek(year, month, day):
    return date(year, month, day).weekday()


def cal_workTime_holiday(last_attendance):
    work_time = time_diff(last_attendance.attendanceTime, last_attendance.offworkTime)
    return work_time


def cal_earlyleaveTime(last_attendance):
    if last_attendance.workTime >= time(8, 0, 0):
        return None
    else:
        return time_diff(last_attendance.workTime, time(8, 0, 0))


def cal_extendTime(last_attendance):
    if last_attendance.workTime.replace(second=0, microsecond=0) > time(8,0,0): #근무시간이 8시간 초과인 경우 -> 연장근무 처리
        return time_diff(time(8,0,0),last_attendance.workTime)

