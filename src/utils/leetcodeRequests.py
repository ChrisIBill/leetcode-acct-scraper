import requests

URL = "https://leetcode.com/graphql"

PROBLEM_SET_HTTP_QUERY = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
        ) {
            total: totalNum
            questions: data {
                difficulty
                likes
                dislikes
                stats
                frontendQuestionId: questionFrontendId
                paidOnly: isPaidOnly
                title
                titleSlug
                topicTags {
                    name
                    id
                    slug
                }
            }
        }
    }"""

AC_SUBMISSIONS_HTTP_QUERY = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
        recentAcSubmissionList(username: $username, limit: $limit) {
            id
            title
            titleSlug
            timestamp
        }
    }"""


def getProblemSetQuestionListJSON(skip):
    if not 0 <= skip <= 2400:  # 2400 is the max
        raise ValueError("Skip must be in range 0-2400")
    variables = f"""{{
		    "categorySlug": "",
		    "filters": {{
		    	"orderBy": "FRONTEND_ID",
		    	"sortOrder": "DESCENDING"
		    }},
		    "limit": "100",
		    "skip": {skip}
	    }}"""
    return requests.get(URL, params={
        "query": PROBLEM_SET_HTTP_QUERY,
        "variables": variables,
    }).json()


def getUserSubmissionsJSON(username):
    variables = f"""{{
        "username": "{username}",
        "limit": "15"
    }}"""
    return requests.get(URL, params={
        "query": AC_SUBMISSIONS_HTTP_QUERY,
        "variables": variables,
    }).json()
