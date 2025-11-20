import pytest

from mplm.llm.client import get_llm
from mplm.models.training import TrainExecutionResult
from mplm.services.data_loader import load_titanic_dataset
from mplm.services.summary_generator import fixed_summary_logic, generate_summary_with_llm
from mplm.services.training_code_generator import generate_error_fixed_training_code, generate_training_code
from mplm.services.training_executor import execute_training_code

# ===============================
# モック用テスト
# ===============================

def test_execute_training_code_mock():
    # 1. データ取得
    df, metadata = load_titanic_dataset()

    # モック用にハードコードしたトレーニングコード
    mock_code = """
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np

# Define features and target
target = 'survived'
features = ['sex', 'age']

# Separate features and target
X_train = df_train[features]
y_train = df_train[target]
X_val = df_val[features]
y_val = df_val[target]
X_test = df_test[features]
y_test = df_test[target]

# Define preprocessing for numeric and categorical features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', ['age']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['sex'])
    ])

# Create a pipeline with preprocessing and classifier
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])

# Train the model
model.fit(X_train, y_train)

# Predict on validation set
y_val_pred = model.predict(X_val)
accuracy_val = accuracy_score(y_val, y_val_pred)

# Predict on test set
y_test_pred = model.predict(X_test)
accuracy_test = accuracy_score(y_test, y_test_pred)
"""

    result = execute_training_code(df=df, code=mock_code, model_output_path=None)
    print(f'[test_execute_training_code_mock] training result : {result}')

    assert isinstance(result, TrainExecutionResult)
    assert result.accuracy_val > 0.1
    assert result.accuracy_test > 0.1
    assert result.model_path is None
    assert result.code == mock_code

# ===============================
# 本番用テスト
# ===============================

def test_execute_training_code_prod(request):
    """本番データを使った execute_training_code テスト"""
    if not request.config.getoption("--run-prod-tests"):
        pytest.skip("本番テストは --run-prod-tests 指定時のみ実行")

    # 1. データ取得
    df, metadata = load_titanic_dataset()

    llm = get_llm(temperature=0.7)

    # 2. サマリー取得
    use_fixed_summary = False
    if use_fixed_summary:
        summary = fixed_summary_logic(df)
    else:
        summary = generate_summary_with_llm(df, 'not available', llm=llm)
    print("====================== generated summary code ==============================")
    print(summary.summary_code)
    print("====================== generated summary ==============================")
    print(summary.summary_text)
    print("============================================================================")

    # 3. 本番LLMでトレーニングコード生成
    target_column = 'survived'
    training_code_error = """
no error
"""
    code = generate_training_code(summary.summary_text, target_column, training_code_error=training_code_error, llm=llm)

    # 出力確認
    print("====================== generated training code ==============================")
    print(code)

    # 4. 実行
    result = execute_training_code(df=df, code=code, model_output_path=None)

    print("====================== execution result ==============================")
    print("accuracy_val:", result.accuracy_val)
    print("accuracy_test:", result.accuracy_test)
    print("model_name:", result.model_name)
    print("model_path:", result.model_path)
    print("============================================================================")

    assert isinstance(result, TrainExecutionResult)
    assert result.accuracy_val is not None
    assert result.accuracy_test is not None


def test_generate_error_fixed_training_code_prod(request):
    """本番LLMを使ったエラー修正版コード生成テスト"""
    if not request.config.getoption("--run-prod-tests"):
        pytest.skip("本番テストは --run-prod-tests 指定時のみ実行")

    # 1. データ取得
    df, metadata = load_titanic_dataset()
    target_column = "survived"

    # 2. 前回失敗したコード・エラー
    failed_code = failed_code = """import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

# Prepare target variables
def prepare_target(series):
    if series.dtype.name == 'category':
        return series.cat.codes
    else:
        return series.astype(int)

y_train = prepare_target(df_train['survived'])
y_val = prepare_target(df_val['survived'])
y_test = prepare_target(df_test['survived'])

# Feature subsets to explore
feature_subsets = [
    ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'cabin', 'embarked', 'boat', 'home.dest'],
    ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked', 'boat', 'home.dest'],  # drop cabin
    ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked', 'boat'],              # drop cabin, home.dest
]

# Preprocessing options
numeric_scalers = [None, StandardScaler(), MinMaxScaler()]
cat_encoders = [OneHotEncoder(handle_unknown='ignore'), OrdinalEncoder()]

# Models to try
models = [
    ('logreg', LogisticRegression(max_iter=1000, random_state=42)),
    ('rf', RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)),
    ('gb', GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=3, random_state=42))
]

best_val_acc = -np.inf
best_test_acc = None
best_model = None

for features in feature_subsets:
    X_train = df_train[features]
    X_val = df_val[features]
    X_test = df_test[features]

    # Identify numeric and categorical columns
    numeric_features = [col for col in features if X_train[col].dtype.kind in 'biufc']
    categorical_features = [col for col in features if X_train[col].dtype.kind in 'O']

    for num_scaler in numeric_scalers:
        num_steps = [('imputer', SimpleImputer(strategy='median'))]
        if num_scaler is not None:
            num_steps.append(('scaler', num_scaler))
        numeric_transformer = Pipeline(steps=num_steps)

        for cat_encoder in cat_encoders:
            cat_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', cat_encoder)
            ])

            transformers = []
            if numeric_features:
                transformers.append(('num', numeric_transformer, numeric_features))
            if categorical_features:
                transformers.append(('cat', cat_transformer, categorical_features))

            preprocessor = ColumnTransformer(
                transformers=transformers,
                remainder='drop'
            )

            for model_name, model in models:
                pipeline = Pipeline(steps=[
                    ('preprocessor', preprocessor),
                    ('classifier', model)
                ])

                pipeline.fit(X_train, y_train)

                y_val_pred = pipeline.predict(X_val)
                y_test_pred = pipeline.predict(X_test)

                val_acc = accuracy_score(y_val, y_val_pred)
                test_acc = accuracy_score(y_test, y_test_pred)

                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    best_test_acc = test_acc
                    best_model = pipeline

model = best_model
accuracy_val = best_val_acc
accuracy_test = best_test_acc
""".strip()
    error = """Found unknown categories ['C106', 'C87', 'E12', 'A14', 'E25', 'D22', 'E10...
cannot import name 'SimpleImputer' from 'sklearn.preprocessing'
"""

    # 3. LLM取得
    llm = get_llm(temperature=0.7)

    # 4. エラー修正版コード生成
    fixed_code = generate_error_fixed_training_code(
        previous_code=failed_code,
        previous_error=error,
        target_column=target_column,
        llm=llm,
    )

    print("====================== fixed training code ==============================")
    print(fixed_code)
    print("============================================================================")

    # 5. 実行して検証
    try:
        result = execute_training_code(df=df, code=fixed_code, model_output_path=None)
        print("====================== execution result ==============================")
        print("accuracy_val:", result.accuracy_val)
        print("accuracy_test:", result.accuracy_test)
        print("model_name:", getattr(result, "model_name", None))
        print("model_path:", getattr(result, "model_path", None))
        print("============================================================================")

        assert result.accuracy_val is not None
        assert result.accuracy_test is not None
    except Exception as e:
        pytest.fail(f"Execution of fixed training code failed: {e}")
