import itertools
import os
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.random_projection import johnson_lindenstrauss_min_dim
from sklearn.metrics import confusion_matrix, multilabel_confusion_matrix , classification_report
import sys
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
process = 'Apply label to samples'
csv_files_path = "CSV_Files/"
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
labels = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
def LoadSamples(csvDir="",classStartAt=0):
    print('Loading samples...')
    samples = None
    for i, indir in enumerate(os.listdir(csvDir)):
        for j, infile in enumerate(os.listdir(csvDir+"/"+indir)):
            try:
                #get the letter
                letter = infile[0]
                print('Class', letter)
                print('Class label:', i)
                newSamples = np.genfromtxt(csvDir +indir+"/"+ infile, delimiter=',')
                if samples is None:
                    samples = newSamples
                else:
                    samples = np.concatenate((samples, newSamples), axis=0)
            except IOError as e:
                print(e, "ERROR - failed to convert '%s'" % infile)

    print("Sample load complete!")
    print("Number of bytes:",samples.nbytes)
    return samples[:,1:], np.ravel(samples[:,:1])

def DimensionReduce(X_data,y_data):
    #johnson lindenstrauss lemma computation for ideal minimum number of dimensions
    epsilon = .15 #permitted error %
    min_dim = johnson_lindenstrauss_min_dim(22344, eps=epsilon)
    # 5% error needs 33150 dimensions retained
    # 10% error = 8583, 15% = 3936, 35% = 853
    print('Minimum dimensions to retain',epsilon,'error:',min_dim)
    #LDA -- aims to model based off difference between classes... supervised dimension reduction (DR) will likely outperform unsupervised DR such as PCA.
    pca = PCA(n_components = min_dim)
    print("Beginning dimension reduction...")
    X_reduced = pca.fit_transform(X_data, y_data)
    print("Finished dimension reduction!")
    return X_reduced

def KNN(data, num_neighbors = 3):
    #split data
    X_train,  y_train, X_validate, y_validate, X_test, y_test = data
    neigh = KNeighborsClassifier(n_neighbors=num_neighbors)
    neigh.fit(X_train, y_train)
    val_score = neigh.score(X_validate,y_validate)
    print("Validation score:",val_score)

    y_pred = neigh.predict(X_test)
    y_true = y_test
    #print(len(letters))
    print("Classification Report:")
    print(classification_report(y_true, y_pred, target_names=letters, labels=labels))

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plot_confusion_matrix(cm, classes=letters)

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()



args = sys.argv

saveNames=["X_train_reduced.npy","y_train.npy","X_validation.npy","y_validation.npy","X_test.npy","y_test.npy"]

if('training.py' in args[0]):
    args = args[1:]

if len(args) == 2 and args[0] == "KNN":
    data = [X_train, y_train, X_validate, y_validate, X_test, y_test] = [None, None, None, None, None, None]
    print('Looking for data')
    for i, saveName in enumerate(saveNames):
        with open(args[1] + saveName, 'rb') as f:
            data[i] = np.load(f)
    print('starting KNN')
    KNN(data, num_neighbors=10)

elif len(args) == 2 and args[0] == 'DimReduce' and (args[1] == 'True' or args[1] == "False"):
    samples, labels = LoadSamples(csvDir=csv_files_path, classStartAt=0)
    # 70% train. Stratify keeps class distribution balanced
    X_train, X_test, y_train, y_test = train_test_split(samples, labels, test_size=.3, random_state=42,
                                                        stratify=labels)
    # 20% validation, 10% test
    X_validate, X_test, y_validate, y_test = train_test_split(X_test, y_test, test_size=.33, random_state=42,
                                                              stratify=y_test)

    # dimension reduction
    X_train_reduced = DimensionReduce(X_train, y_train)
    saveReducedData = True if args[1] == "True" else False
    data = [X_train, y_train, X_validate, y_validate, X_test, y_test]
    if saveReducedData:
        for i in range(len(saveNames)):
            print("Saving", saveNames[i], "...")
            with open(saveNames[i], 'wb') as f:
                np.save(f, data[i])
elif len(args) > 3:
    print("Too many arguments.")
    print("Please provide:")
    print("1) model  ---- (KNN, ...)")
    print("2) inpath ---- (relative to working directory, ending in /)")
else:
    print("Invalid arguments. Please view training.py for argument options.")
