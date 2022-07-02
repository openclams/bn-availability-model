
# # plot impact of logloss with imbalanced datasets
# from sklearn.metrics import log_loss
# from matplotlib import pyplot
# from numpy import array
# # define an imbalanced dataset
# testy = [0 for x in range(100)] + [1 for x in range(10)]
# # loss for predicting different fixed probability values
# predictions = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
#
# losses = [log_loss(testy, [y for x in range(len(testy))]) for y in predictions]
# # plot predictions vs loss
# pyplot.plot(predictions, losses)
# pyplot.show()


# roc curve
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve
from matplotlib import pyplot
# generate 2 class dataset
X, y = make_classification(n_samples=1000, n_classes=2, random_state=1)
# split into train/test sets
trainX, testX, trainy, testy = train_test_split(X, y, test_size=0.5, random_state=2)
# fit a model
model = LogisticRegression()
model.fit(trainX, trainy)
# predict probabilities
probs = model.predict_proba(testX)
# keep probabilities for the positive outcome only
probs = probs[:, 1]
# calculate roc curve
fpr, tpr, thresholds = roc_curve(testy, probs)
# plot no skill
pyplot.plot([0, 1], [0, 1], linestyle='--')
# plot the roc curve for the model
pyplot.plot(fpr, tpr)
# show the plot
pyplot.show()
