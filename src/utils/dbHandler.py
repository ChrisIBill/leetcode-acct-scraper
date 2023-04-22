import csv
import os
import pandas as pd
import numpy as np
from pymongo import MongoClient

from utils.Utils import validateSubmission, validateProblem
SUBMISSIONS_CSV = "submissions.csv"
PROBLEMS_CSV = "problems.csv"
SUBMISSION_COLUMNS = ["link", "title", "runtime",
                      "language", "runtime-perf", "memory-perf"]
PROBLEM_COLUMNS = ["link", "number", "title",
                   "acceptance", "difficulty", "tags"]


def getDatabase():
    MONGODB_URI = os.environ.get('MNGODB_URI')
    client = MongoClient(MONGODB_URI)
    return client['leetcode']


def getSubmissionsCollection():
    return getDatabase()['submissions']


def getProblemsCollection():
    return getDatabase()['problems']


def readSubmissionsFromDB():
    submissions = getSubmissionsCollection().find()
    return submissions


def getDataframeFromSubmissions():
    return pd.read_csv(SUBMISSIONS_CSV)


def writeSubmissionsToDB(df):
    try:
        getSubmissionsCollection().insert_many(df.to_dict('records'))
    except Exception as e:
        print("Error writing submissions to DB")
        print(e)


def writeProblemsToDB(df):
    try:
        getProblemsCollection().insert_many(df.to_dict('records'))
    except Exception as e:
        print("Error writing problems to DB")
        print(e)


# def readDictFromCSV(csv_file, csv_columns):
#     reader = csv.DictReader(csv_file, fieldnames=csv_columns)
#     dict_data = {}
#     for row in reader:
#         dict_data[row['link']] = [row[t] for t in csv_columns]
#     return dict_data


# def writeDictToCSV(csv_file, csv_columns, dict_data):
#     writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
#     for d in dict_data:
#         print(d)
#         print("Link objects")
#         for l in dict_data[d]:
#             print(l)
#         if len(dict_data[d]) != 5:
#             print("Weird length, skipping")
#             continue
#         writer.writerow(
#             {
#                 'link': d,
#                 'title': dict_data[d][0],
#                 'runtime': dict_data[d][1],
#                 'language': dict_data[d][2],
#                 'runtime-perf': dict_data[d][3],
#                 'memory-perf': dict_data[d][4],
#             })


# def readSubmissionsFromCSV():
#     csv_columns = ["link", "title", "runtime",
#                    "language", "runtime-perf", "memory-perf"]
#     with open(SUBMISSIONS_CSV, 'r') as csvfile:
#         submissionsDict = readDictFromCSV(csvfile, csv_columns)
#     return submissionsDict


# def writeSubmissionsToCSV(dict_data):
#     with open(SUBMISSIONS_CSV, 'w', newline='') as csvfile:
#         writeDictToCSV(csvfile, SUBMISSION_COLUMNS, dict_data)


# def appendSubmissionToCSV(dict_data):
#     with open(SUBMISSIONS_CSV, 'a', newline='') as csvfile:
#         writeDictToCSV(csvfile, SUBMISSION_COLUMNS, dict_data)


# def readProblemsFromCSV():
#     with open(PROBLEMS_CSV, 'r') as csvfile:
#         problemsDict = readDictFromCSV(csvfile, PROBLEM_COLUMNS)
#     return problemsDict


# def writeProblemsToCSV(dict_data):
#     with open(PROBLEMS_CSV, 'w', newline='') as csvfile:
#         writeDictToCSV(csvfile, PROBLEM_COLUMNS, dict_data)


# def appendProblemsToCSV(dict_data):
#     with open(PROBLEMS_CSV, 'a', newline='') as csvfile:
#         writeDictToCSV(csvfile, PROBLEM_COLUMNS, dict_data)
