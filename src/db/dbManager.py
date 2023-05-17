import time
import pandas as pd
import numpy as np
import utils.leetcodeRequests as leetcodeRequests
from utils.Utils import formatProblemSet, formatSubmissionsJSON, getCurrentTime
from utils.dbHandler import getCollectionMetaData, getProblemDataFromTitle, getProblemsCollection, getSubmissionsCollection, getUserdataCollection, getUsersFromCollection, writeProblemsToDB

NUM_TO_SCRAPE = 100

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
    df, total_problems = formatProblemSet(probsDict, CURRENT_TIME)
    skip += NUM_TO_SCRAPE
    if total_problems < skip:
        skip = 0
    meta = {
        'current-scrape': skip,
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
    meta = getCollectionMetaData(getSubmissionsCollection())
    submissions = {}
    subsDict = {}
    for user in meta['tracked-users']:
        print(user)
        #handles remaking data for better handling
        userdata = leetcodeRequests.getUserSubmissionsJSON(user)
        userdata = userdata['data']['recentAcSubmissionList']
        subsDict.update({user: userdata})
        #subsDF.append(formatSubmissionsJSON(userdata, user))
        #@TODO
    return subsDict


def DBManager():
    # return updateProblemsSetCollection()
    # return updateUserDataCollection()
