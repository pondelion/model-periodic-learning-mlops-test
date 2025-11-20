from unittest.mock import patch

import pytest

from mplm.chains.training_chain import fix_error_training_chain
from mplm.models.state import WorkflowState
from mplm.models.training import TrainExecutionResult
from mplm.services.data_loader import load_titanic_dataset
from mplm.services.training_executor import execute_training_code


def test_fix_error_training_chain_mock():
    """
    fix_error_training_chain のモック単体テスト
    - 前回失敗コードとエラーを渡す
    - LLM生成コードと実行結果をモック
    """
    df, metadata = load_titanic_dataset()
    failed_code = "FAKE_FAILED_CODE"
    training_errors = ["Some runtime error"]

    state: WorkflowState = {
        "df": df,
        "target_column": "survived",
        "previous_code": failed_code,
        "training_errors": training_errors,
        "retry_count": 0,
    }

    fake_fixed_code = "FAKE_FIXED_CODE"
    fake_result = TrainExecutionResult(
        llm_name=None,
        accuracy_val=0.95,
        accuracy_test=0.92,
        model_path=None,
        code=fake_fixed_code,
        model_name="FAKE_MODEL",
        model=None,
    )

    with patch(
        "mplm.chains.training_chain.generate_error_fixed_training_code",
        return_value=fake_fixed_code
    ) as mock_gen:
        with patch(
            "mplm.chains.training_chain.execute_training_code",
            return_value=fake_result
        ) as mock_exec:
            updated = fix_error_training_chain(state)

            # モック呼び出し確認
            mock_gen.assert_called_once_with(
                previous_code=failed_code,
                previous_error="\n".join(training_errors),
                target_column="survived",
                llm=None,
            )
            mock_exec.assert_called_once_with(
                df=df,
                code=fake_fixed_code,
                model_output_path=None,
            )

            # 状態確認
            assert updated["status"] == "ok"
            assert updated["training_result"] == fake_result
            assert updated.get("fixed_code") == fake_fixed_code
            assert updated["retry_count"] == 0

def test_fix_error_training_chain_failure():
    """
    fix_error_training_chain の失敗時テスト
    - generate_error_fixed_training_code は成功するが execute_training_code が失敗
    """
    df, metadata = load_titanic_dataset()
    failed_code = "FAKE_FAILED_CODE"
    training_errors = ["Some runtime error"]

    state: WorkflowState = {
        "df": df,
        "target_column": "survived",
        "previous_code": failed_code,
        "training_errors": training_errors,
        "retry_count": 0,
    }

    fake_fixed_code = "FAKE_FIXED_CODE"

    with patch(
        "mplm.chains.training_chain.generate_error_fixed_training_code",
        return_value=fake_fixed_code
    ):
        with patch(
            "mplm.chains.training_chain.execute_training_code",
            side_effect=RuntimeError("Execution failed")
        ):
            updated = fix_error_training_chain(state)

            assert updated["status"] == "failed"
            assert "Execution failed" in updated["training_errors"][-1]
            assert updated["previous_code"] == fake_fixed_code
            assert updated["retry_count"] == 1


def test_fix_error_training_chain_prod(request):
    """
    実際の Titanic データを使った本番テスト
    - 過去に失敗したコードとエラーを用意
    - LLMで修正版コード生成 → 実行
    """
    if not request.config.getoption("--run-prod-tests"):
        pytest.skip("本番 LLM テストは --run-prod-tests を指定したときのみ実行")

    df, metadata = load_titanic_dataset()
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
    with pytest.raises(Exception) as _:
        execute_training_code(df, failed_code)
    training_errors = [
        "Found unknown categories ['C106', 'C87', 'E12', 'A14', 'E25', 'D22', 'E10...",
        "cannot import name 'SimpleImputer' from 'sklearn.preprocessing'",
    ]

    state: WorkflowState = {
        "df": df,
        "target_column": "survived",
        "previous_code": failed_code,
        "training_errors": training_errors,
        "retry_count": 0,
    }

    from mplm.llm.client import get_llm
    llm = get_llm(temperature=0.7)
    state["llm"] = llm

    updated = fix_error_training_chain(state)
    print("training_errors:", updated["training_errors"])

    assert updated["status"] == "ok"
    tr = updated["training_result"]
    assert tr.accuracy_val is not None
    assert tr.accuracy_test is not None

    print("\n====== Training Result ======")
    print("accuracy_val:", tr.accuracy_val)
    print("accuracy_test:", tr.accuracy_test)
    print("model_name:", tr.model_name)
    print("model_path:", tr.model_path)
    print("fixed_code:", updated["fixed_code"])
    print("============================\n")
