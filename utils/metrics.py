import pandas as pd
import numpy as np
from nltk.translate.bleu_score import sentence_bleu
from sklearn.metrics import (accuracy_score, 
                             classification_report,
                             confusion_matrix)
import matplotlib.pyplot as plt
import seaborn as sns


class Evaluate():
    def __init__(self):
        pass
    
    def _string_to_set(self, X):
        result = [set(text.split()) for text in X]
        return result
        
    def _jaccard_simmilarity(self, X, Y):
        
        if (not isinstance(X, str)) or (not isinstance(Y, str)):
            return 0
        
        # List the unique words in a document
        X_words = set(X.split())
        Y_words = set(Y.split())
 
        # Find the intersection of words list of doc1 & doc2
        intersection = X_words.intersection(Y_words)

        # Find the union of words list of doc1 & doc2
        union = X_words.union(Y_words)

        # Calculate Jaccard similarity score
        # using length of intersection set divided by length of union set
        try:
            jaccard_similarity = float(len(intersection)) / len(union)
        except ZeroDivisionError:
            if len(intersection)==0:
                jaccard_similarity = 1
            else:
                print(intersection)
                raise

        return jaccard_similarity
        
    
    def compute_jaccard_score(self, X, Y):
        # Stack the arrays vertically to match the shape for apply_along_axis
        stacked_docs = np.vstack((X, Y))
       
        # Compute Jaccard similarity between corresponding documents 
        similarities = np.apply_along_axis(lambda x: self._jaccard_simmilarity(x[0], x[1]), axis=0, arr=stacked_docs)
        
        return similarities
    
    
    def _sentence_bleu(self, X, Y, weights):
        if (not isinstance(X, str)) or (not isinstance(Y, str)):
            return 0
        
        bleu = sentence_bleu([X], Y, weights)
        
        return bleu
    
    
    def compute_sentence_bleu(self, X, Y, weights=(0.5, 0.5)):
        # Stack the arrays vertically to match the shape for apply_along_axis
        stacked_docs = np.vstack((X, Y))
        
        # Compute Sentence Bleu between corresponding documents using
        bleu_scores = np.apply_along_axis(lambda x: self._sentence_bleu(x[0], x[1], weights), axis=0, arr=stacked_docs)
        
        return np.round(bleu_scores, 2 )


    def make_confusion_matrix(self, conf_matrix):
        categories = ["Person", "Non-Person"]
        
        evaluation_results = {}

        # matrix_labels = 
        group_names = ["True Neg","False Pos","False Neg","True Pos"]
        
        group_counts = ["{0:0.0f}".format(value) for value in
                conf_matrix.flatten()]

        group_percentages = ["{0:.2%}".format(value) for value in
                             conf_matrix.flatten()/np.sum(conf_matrix)]

        matrix_labels_data = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
          zip(group_names, group_counts, group_percentages)]
        
        matrix_labels = np.asarray(matrix_labels_data).reshape(2,2)


        #Accuracy is sum of diagonal divided by total observations
        accuracy  = np.trace(conf_matrix) / float(np.sum(conf_matrix))

        #Metrics for Binary Confusion Matrices
        precision = conf_matrix[1,1] / sum(conf_matrix[:,1])
        recall    = conf_matrix[1,1] / sum(conf_matrix[1,:])
        f1_score  = 2*precision*recall / (precision + recall)
        stats_text = "\n\nAccuracy={:0.3f}\nPrecision={:0.3f}\nRecall={:0.3f}\nF1 Score={:0.3f}".format(
            accuracy,precision,recall,f1_score)

        #Get default figure size if not set
        figsize = plt.rcParams.get('figure.figsize')
        
        
        # MAKE THE HEATMAP VISUALIZATION
        plt.figure(figsize=figsize)

        sns.heatmap(conf_matrix, annot=matrix_labels, fmt="", cmap="Blues", xticklabels=categories, yticklabels=categories)
        plt.ylabel('True label')
        # plt.xlabel('Predicted label')
        plt.xlabel('Predicted label' + stats_text)
        
        evaluation_results = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
        }
        return evaluation_results


        
    def compute_evaluation_metrics(self, y_true, y_pred):
        # evaluation_results = {}
        labels = ['Non-Person', 'Person']
        mapping = {'Non-Person': 1, 'Person': 0}
        def map_func(x):
            return mapping.get(x, 1)

        y_true = np.vectorize(map_func)(y_true)
        y_pred = np.vectorize(map_func)(y_pred)

        # Calculate accuracy
        accuracy = accuracy_score(y_true=y_true, y_pred=y_pred)
        print(f'Accuracy: {accuracy:.3f}')

        # Generate accuracy report
        unique_labels = set(y_true)  # Get unique labels

        for label in unique_labels:
            label_indices = [i for i in range(len(y_true)) 
                             if y_true[i] == label]
            label_y_true = [y_true[i] for i in label_indices]
            label_y_pred = [y_pred[i] for i in label_indices]
            accuracy = accuracy_score(label_y_true, label_y_pred)
            print(f'Accuracy for label {label}: {accuracy:.3f}')
        
        
        # Generate confusion matrix
        conf_matrix = confusion_matrix(y_true=y_true, y_pred=y_pred, labels=[0, 1])
        
        evaluation_results = self.make_confusion_matrix(conf_matrix)
        return evaluation_results