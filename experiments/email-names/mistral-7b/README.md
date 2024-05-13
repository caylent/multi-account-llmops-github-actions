# Project Title

Email Names Extraction

## Overview

This repository contains notebooks and utility scripts for preprocessing data, fine-tuning and evaluating the `Mistral-7B` large language model (LLM). It is structured to support experiments with different data processing techniques and model configurations.

### Repository Structure

- **`data/`**: Contains preprocessed and training data.
- **`notebooks/`**: Jupyter notebooks detailing the project's data preprocessing, model training, and evaluation.
- **`prompts/`**: Various versions of prompts used in training the model.
- **`utils/`**: Utility scripts for operations such as S3 data uploads, metric calculations, and model implementations.

### Notebooks

1. **`1.0-data-preprocess.ipynb`**
   - Focuses on preprocessing the raw data into a format suitable for training and creates a train/test split.
   
2. **`2.0-training-data-prep-and-model-finetuning.ipynb`**
   - Outlines the preparation of training data and steps to fine-tune the `Mistral-7B` LLM.

3. **`3.0-model-evaluation.ipynb`**
   - Evaluates the performance of the finetuned `Mistral-7B` model against the test dataset.

### Utilities

Scripts in the `utils/` directory support various backend operations, such as:
- Uploading data to AWS S3.
- Implementing custom metrics for model evaluation.
- Model class implementations for extended functionalities.

## Getting Started

Login to the Amazon SageMaker Studio and clone the repository to get started.

### Installation

Clone the repo:
```bash
git clone https://github.com/DragnetTech/LLMParsingModels.git

cd LLMParsingModels
```
### Usage
Navigate to the `experiments/email-names/mistral-7b/notebooks/` directory and launch the Jupyter Notebooks to start experimenting with the data preprocessing, model training, and evaluations.