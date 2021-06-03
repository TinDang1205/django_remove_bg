from nudenet import NudeClassifier

# initialize classifier (downloads the checkpoint file automatically the first time)

classifier = NudeClassifier()


def check_nude(path):
    return classifier.classify(path)[path]["unsafe"]
