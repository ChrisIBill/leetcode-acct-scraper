from src.utils.dbHandler import getProblemDataFromTitle


def handleNewSubmissions(submissionsDict):
    import pandas as pd
    profdf = pd.DataFrame.from_dict(submissionsDict, orient='index')
    for title in profdf['title'].values:
        problemData = getProblemDataFromTitle(title)
        if problemData is None:
            print("Problem not in DB, skipping")
            continue
