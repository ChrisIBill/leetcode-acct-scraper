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
