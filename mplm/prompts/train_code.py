"""
LLM prompt template for generating training + evaluation code using scikit-learn.
"""

from langchain_core.prompts import PromptTemplate

# TRAIN_CODE_PROMPT = PromptTemplate.from_template(
#     """
# You are an expert ML engineer.

# Generate Python code that:

# 1. Uses three pandas DataFrames already provided in the execution environment:
#    - df_train
#    - df_val
#    - df_test

# 2. Performs preprocessing needed for sklearn models.

#    STRICT RULES TO PREVENT DATA LEAKAGE:
#    - Use `{target_column}` as the target column.
#    - DO NOT include the target column in the feature matrix.
#    - Fit preprocessing steps **ONLY on df_train**.
#    - Apply preprocessing to df_val and df_test **using transform only**.
#    - NEVER combine df_train/df_val/df_test at any stage.
#    - NEVER use df_val or df_test for model fitting.
#    - df_val is used only for optional hyperparameter tuning.
#    - df_test is used **only** for final evaluation metrics.

# 3. Selects and trains a classifier using ONLY scikit-learn (LLM must choose the model).

# 4. Computes accuracy for:
#    - validation dataset → accuracy_val
#    - test dataset → accuracy_test

# 5. Store the trained model instance in a variable named `model`.

# 6. Assign variables:
#    - accuracy_val
#    - accuracy_test

# Important:
# - df_train, df_val, df_test have ALREADY been split outside this code.
# - DO NOT perform any train/test splitting.
# - Write code that can run inside exec().
# - Use only sklearn models (e.g., LogisticRegression, RandomForestClassifier, etc.).
# - Do not save the model to disk; keep it in memory in `model`.
# - Write pure Python code only.

# Dataset summary:
# {dataset_summary}

# Previous training code execution error:
# {training_code_error}

# Output:
# Only Python code, and always wrap it inside a markdown python block like this:
# ```python
# # your code here
# ```
# Do NOT provide any explanation outside the code block.
# """
# )

# TRAIN_CODE_PROMPT = PromptTemplate.from_template(
#     """
# You are an expert ML engineer.

# Generate Python code that:

# 1. Uses three pandas DataFrames already provided:
#    - df_train
#    - df_val
#    - df_test

# 2. Performs preprocessing for sklearn models.

#    STRICT RULES TO PREVENT DATA LEAKAGE:
#    - Use `{target_column}` as the target column.
#    - DO NOT include the target column in the feature matrix.
#    - Fit preprocessing steps **ONLY on df_train**.
#    - Apply preprocessing to df_val and df_test **using transform only**.
#    - NEVER combine df_train/df_val/df_test at any stage.
#    - NEVER use df_val or df_test for model fitting.

# 3. Feature and preprocessing diversity:
#    - Consider multiple subsets of features and try different feature combinations across runs.
#    - Explore various preprocessing strategies for numeric features (e.g., StandardScaler, MinMaxScaler, SimpleImputer) and categorical features (e.g., OneHotEncoder, OrdinalEncoder).
#    - Ensure preprocessing choices are consistent with training/testing rules to prevent data leakage.

# 4. Model and hyperparameter diversity:
#    - Train a classifier using ONLY scikit-learn.
#    - Explore multiple models across runs (LogisticRegression, RandomForestClassifier, GradientBoostingClassifier, SVC, KNeighborsClassifier, etc.).
#    - Explore hyperparameters: regularization strength, number of estimators, max_depth, learning_rate, kernel types, etc.
#    - Vary models, features, and preprocessing combinations to maximize exploration diversity.

# 5. Compute accuracy for:
#    - validation dataset → accuracy_val
#    - test dataset → accuracy_test

# 6. Store the trained model in a variable named `model` and assign variables:
#    - accuracy_val
#    - accuracy_test

# Important:
# - df_train, df_val, df_test are already split.
# - Do not perform train/test splitting inside this code.
# - Write code that runs in exec().
# - Keep the model in memory; do not save to disk.
# - Use only sklearn models.
# - Pure Python code only.

# Dataset summary:
# {dataset_summary}

# Previous training code execution error (If any, NEVER output code that causes the following error):
# {training_code_error}

# Output:
# Only Python code, wrapped inside a markdown code block marker like this:
# ```python
# # your code here
# ```
# Do NOT provide any explanation outside the code block.
# """
# )


TRAIN_CODE_PROMPT = PromptTemplate.from_template(
    """
You are an expert ML engineer.

Generate Python code that:

1. Uses three pandas DataFrames already provided:
   - df_train
   - df_val
   - df_test

2. Performs preprocessing for sklearn models.

   STRICT RULES TO PREVENT DATA LEAKAGE:
   - Use `{target_column}` as the target column.
   - DO NOT include the target column in the feature matrix.
   - Fit preprocessing steps **ONLY on df_train**.
   - Apply preprocessing to df_val and df_test **using transform only**.
   - NEVER combine df_train/df_val/df_test at any stage.
   - NEVER use df_val or df_test for model fitting.

3. Feature and preprocessing diversity:
   - Consider multiple subsets of features and try different feature combinations across runs.
   - Explore various preprocessing strategies for numeric features (e.g., StandardScaler, MinMaxScaler, SimpleImputer) and categorical features (e.g., OneHotEncoder, OrdinalEncoder).
   - Ensure preprocessing choices are consistent with training/testing rules to prevent data leakage.

4. Model and hyperparameter diversity:
   - Train a classifier using ONLY scikit-learn.
   - Explore multiple models across runs.
   - Explore hyperparameters: regularization strength, number of estimators, max_depth, learning_rate, kernel types, etc.
   - Vary models, features, and preprocessing combinations to maximize exploration diversity.

5. Compute accuracy for:
   - validation dataset → accuracy_val
   - test dataset → accuracy_test

6. Store the trained model in a variable named `model` and assign variables:
   - accuracy_val
   - accuracy_test

Important:
- df_train, df_val, df_test are already split.
- Do not perform train/test splitting inside this code.
- Write code that runs in exec().
- Keep the model in memory; do not save to disk.
- Use only sklearn models.
- Pure Python code only.

Dataset summary:
{dataset_summary}

Previous training code execution error:
{training_code_error}

Output:
Only Python code, wrapped inside a markdown code block marker like this:
```python
# your code here
```
Do NOT provide any explanation outside the code block.
Before emitting the code block, read the previous execution error carefully and ensure you do NOT repeat the same mistake again.
"""
)


FIX_ERROR_CODE_PROMPT = PromptTemplate.from_template(
"""
You are an expert ML engineer.

Your task: Fix the provided Python training code to prevent errors.

Constraints / Required behavior:
1. Use these three pandas DataFrames: df_train, df_val, df_test.
2. Target column is: {target_column}.
   - DO NOT include the target column in the feature matrix.
3. Fit preprocessing only on df_train; apply transforms to df_val and df_test.
4. NEVER combine df_train/df_val/df_test for fitting.
5. Use only scikit-learn models.
6. Compute:
   - accuracy_val (on validation set)
   - accuracy_test (on test set)
7. Store the trained model in a variable named `model`.
8. Keep the model in memory; do not save to disk.
9. Write code that can run inside exec().
10. Pure Python code only.

Previous code (contain errors):
{previous_code}

Previous execution error:
***DO NOT REPEAT THIS ERROR!!***
{previous_error}

Output:
Only Python code, wrapped inside a markdown code block marker like this:
```python
# your fixed code here
```
Do NOT provide any explanation outside the code block.
Before emitting the code block, read the previous code and error carefully and ensure the same mistake does NOT happen again.
"""
)
