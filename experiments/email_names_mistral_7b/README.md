# Project Title

Email Names Extraction

## Overview

This repository contains notebooks and utility scripts for preprocessing data, fine-tuning and evaluating the `Mistral-7B` large language model (LLM). It is structured to support experiments with different data processing techniques and model configurations.

### Notebooks

Files with the `nb_` deal with running jobs or operations to further fine-tune the model:
1. **`nb_train.ipynb`**
   - Outlines the preparation of training data and steps to fine-tune the `Mistral-7B` LLM.

2. **`nb_test.ipynb`**
   - Evaluates the performance of the finetuned `Mistral-7B` model against the test dataset.

### Utilities

Scripts with the `utils_` prefix support various backend operations, such as:
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

You may also be prompted to authenticate with Git, which will require additional steps:
- On a separate tab or window, go to [GitHub](https://github.com/)
- Login to your GitHub account if not already logged in
- Click on your profile icon on the top right
- Click on the **Settings** option
- Scroll all the way to the bottom, and click on the **Developer settings** option
- Click on **Personal access tokens > Tokens (classic)**
- Click on **Generate new token > Generate new token (classic)**
- Type a descriptive note for this token and enable all permission checkboxes
- Click on **Generate token**, then save the token value somewhere safe
   - e.g. 1Password
- This token value will be used as the password when authenticating via Git on SageMaker
- Go back to your SageMaker window/tab and enter your username and password (the token value)

### Usage
Navigate to the `experiments/email_names_mistral_7b` directory and launch the Jupyter Notebooks on AWS SageMaker to start experimenting with the data preprocessing, model training, and evaluations.