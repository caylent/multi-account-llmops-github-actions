# Utility Functions

### This directory contains utility functions used throughout the project.

The metrics.py file provides functions for evaluating the performance of your predictions. Here's an example of how to use the 
compute_jaccard_score compute_sentence_bleu and compute_evaluation_metrics functions:

```
import os
from utils.metrics import compute_jaccard_score, compute_sentence_bleu, compute_evaluation_metrics

# Load your ground truth and predicted data
ground_truth = ["This is a sample ground truth sentence.", "Another ground truth sentence."]
predictions = ["This is a sample predicted sentence.", "Another predicted sentence."]

# Compute Jaccard similarity score
jaccard_score = compute_jaccard_score(ground_truth, predictions)
print(f"Jaccard similarity score: {jaccard_score}")

# Compute sentence-level BLEU score
bleu_score = compute_sentence_bleu(ground_truth, predictions)
print(f"Sentence-level BLEU score: {bleu_score}")

# Compute overall evaluation metrics
metrics = compute_evaluation_metrics(ground_truth, predictions)
print(f"Evaluation metrics: {metrics}")

```

In this example, we first import the necessary functions from the metrics.py file. Then, we define some sample ground truth and predicted data, which you would replace with your actual data.

Next, we call the  compute_jaccard_score function, passing in the ground truth and predicted data, and print the resulting Jaccard similarity score.

We then call the compute_sentence_bleu function, again passing in the ground truth and predicted data, and print the resulting sentence-level BLEU score.

Finally, we call the compute_evaluation_metrics function, passing in the ground truth and predicted data, and print the resulting evaluation metrics dictionary, which may include metrics like precision, recall, F1-score, and others.

Remember to replace the sample data with your actual ground truth and predicted data, and ensure that the file path to the metrics.py file is correct in your project structure.