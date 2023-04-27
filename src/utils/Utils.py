import pandas
import numpy
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


ZERO_DATE = datetime.datetime(1970, 1, 1)


def launchDriver():
    return webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))


def closeDriver(driver):
    driver.close()


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


def greaterThanWeek(delta):
    return delta.days > 7


def greaterThanDay(delta):
    return delta.days > 1


def lessThanHour(delta):
    return delta.seconds < 3600


def expandNumber(numString: str):
    if numString.isnumeric():
        return numString
    numMap = {
        'K': 1000,
        'M': 1000000,
        'B': 1000000000,
    }

    if numString[-1] in numMap:
        return "{:.2e}".format(float(numString[:-1]) * numMap[numString[-1]])


def formatProblemSet(probsDict, time):
    print(probsDict)

    df = pandas.DataFrame.from_dict(
        probsDict['data']['problemsetQuestionList']['questions'])
    df = pandas.concat([df.drop(['stats'], axis=1), df['stats'].map(
        eval).apply(pandas.Series)], axis=1)
    df = pandas.concat([df.drop(['topicTags'], axis=1), pandas.DataFrame(
        df['topicTags'].map(lambda x: [y['name'] for y in x] if x else []))], axis=1)
    df.drop(['totalAccepted', 'totalSubmission',
            'titleSlug'], axis=1, inplace=True)
    df = df.rename(columns={'totalAcceptedRaw': 'totalAccepted',
                            'totalSubmissionRaw': 'totalSubmission',
                            'frontendQuestionId': 'problemNumber',
                            'paidOnly': 'isPremium',
                            'acRate': 'acceptanceRate'})
    df.insert(0, 'update-time', time)
    df.set_index('title', inplace=True)
    df['problemNumber'] = df['problemNumber'].astype(int)
    return df.to_dict(orient='index')
