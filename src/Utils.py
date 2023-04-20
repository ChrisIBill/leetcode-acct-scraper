import datetime
import time


def validateSubmission(sub):
    if not sub or len(sub) != 6:
        print("Invalid submission: ", sub)
        return False
    else:
        return True


def validateProblem(problem):
    if not problem or len(problem) != 5:
        print("Invalid problem: " + problem)
        return False
    else:
        return True


def reformatDataFrame(df):
    print(df.shape)
    print(df.columns)
    print(df.head())
    print(df.info())

# Time Management


def dateTimeFromStr(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def dateTimeToStr(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


def getCurrentTime():
    return datetime.datetime.now()


def compareTimes(t1, t2):
    t1_delta = datetime.timedelta(t1)
    t2_delta = datetime.timedelta(t2)
    print("T1 time: ", t1)
    print("T1 delta: ", t1_delta)
    print("T2 time: ", t2)
    print("T2 delta: ", t2_delta)
    return t1_delta - t2_delta


def test():
    time1 = getCurrentTime()
    print("Time1: ", time1)
    time.sleep(5)
    time2 = getCurrentTime()
    print("Time2: ", time2)
    return compareTimes(time2, time1)


print(test())
