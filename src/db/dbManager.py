import time
import pandas as pd
import numpy as np
import utils.leetcodeRequests as leetcodeRequests
from utils.Utils import formatProblemSet, getCurrentTime
from utils.dbHandler import getCollectionMetaData, getProblemDataFromTitle, getProblemsCollection, getUsersFromCollection, writeProblemsToDB


def handleNewSubmissions(submissionsDict):
    import pandas as pd
    profdf = pd.DataFrame.from_dict(submissionsDict, orient='index')
    for title in profdf['title'].values:
        problemData = getProblemDataFromTitle(title)
        if problemData is None:
            print("Problem not in DB, skipping")
            continue


def updateProblemsSetCollection():
    CURRENT_TIME = getCurrentTime()
    probsCollection = getProblemsCollection()
    meta = getCollectionMetaData(probsCollection)
    skip = meta['current-scrape']
    probsDict = leetcodeRequests.getProblemSetQuestionListJSON(skip)
    df = formatProblemSet(probsDict, CURRENT_TIME)
    meta = {
        'current-scrape': skip + 100,
        'last-update': CURRENT_TIME
    }
    writeProblemsToDB(df, meta)
    return df
    # get problems collection metadata
    # contains current-scrape: int,
    # if any sample-submissions for problems to be scraped, scrape them as well
    # call graphql api to get problems after current-scrape
    # update problems collection


def updateUserDataCollection():
    CURRENT_TIME = getCurrentTime()
    usernames = getUsersFromCollection()
    submissions = []
    for user in usernames:
        submissions.append(leetcodeRequests.getUserSubmissionsJSON(user))
        time.sleep(5)
    return submissions


def DBManager():
    # return updateProblemsSetCollection()
    return updateUserDataCollection()
