import csv
import os
import pandas as pd
import numpy as np
from pymongo import MongoClient

from .Utils import validateSubmission, validateProblem
SUBMISSION_COLUMNS = ["link", "title", "runtime",
                      "language", "runtime-perf", "memory-perf"]
PROBLEM_COLUMNS = ["link", "number", "title",
                   "acceptance", "difficulty", "tags"]


def getDatabase():
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    return client['leetcode']


def getSubmissionsCollection():
    return getDatabase()['submissions']


def getProblemsCollection():
    return getDatabase()['problems']


def writeProblemsToDB(probsDict):
    db = getProblemsCollection()
    try:
        for prob in probsDict:
            print(prob)
            # if not validateProblem(prob):
            #     print("Invalid problem, skipping")
            #     continue
            db.update_one({"title": prob}, {
                "$set": probsDict[prob]}, upsert=True)
        # getProblemsCollection().insert_many(probsDict)
    except Exception as e:
        print("Error writing problems to DB")
        print(e)


def getProblemsLinksFromDB():
    return getProblemsCollection().distinct("link")


def writeSampleSubmissionsToDB(subsDict):
    print(subsDict)
    for i, n in enumerate(subsDict):
        print(i, n)
        db = getProblemsCollection()
        if db.find_one({"title": subsDict[n]}) is None:
            print("Problem not in DB, skipping")
            continue
        db.update_one({"title": subsDict[n], 'sample-submissions': {'$exists': False}}, {
            '$set': {'sample-submissions': n}})


def getProblemDataFromTitle(problemTitle):
    try:
        return getProblemsCollection().find_one(
            {"title": problemTitle})
    except Exception as e:
        print("Error getting problem from DB")
        print(e)
        return None


def getUserdataCollection():
    return getDatabase()['userdata']


def getUserdataFromDB(username):
    return getUserdataCollection().find_one({"_id": username})


def writeSubmissionsToDB(df):
    try:
        getSubmissionsCollection().insert_many(df.to_dict('records'))
    except Exception as e:
        print("Error writing submissions to DB")
        print(e)


def writeUserdataToDB(username, df):
    try:
        getUserdataCollection().update_one({"_id": username}, {
            "$push": df.to_dict('records')}, upsert=True)
    except Exception as e:
        print("Error writing userdata to DB")
        print(e)
