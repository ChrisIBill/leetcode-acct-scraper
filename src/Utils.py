import datetime
import time

ZERO_DATE = datetime.datetime(1970, 1, 1)


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
    print("T1 time: ", t1)
    print("T2 time: ", t2)
    comp = t1 - t2
    print("Comp: ", comp)
    return comp


def test():
    time1 = getCurrentTime()
    print("Time1: ", time1)
    time.sleep(5)
    time2 = getCurrentTime()
    print("Time2: ", time2)
    return compareTimes(time2, time1)


print(test())
