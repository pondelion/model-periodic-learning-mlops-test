import os

import pytest
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from mplm.db.base import Base
from mplm.db.crud import create_run_record
from mplm.db.session import get_engine, get_session


@pytest.fixture(scope="function")
def db_session():
    """インメモリSQLiteデータベースを使ったセッションのセットアップ"""
    engine = create_engine("sqlite:///:memory:", echo=True)  # インメモリSQLite
    Base.metadata.create_all(engine)  # テーブル作成

    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()

    yield db  # テストが終わったらセッションを閉じる

    db.close()  # テスト後にセッションを閉じる


# @pytest.fixture(scope="function")
# def db_session(tmp_path):
#     """一時的なSQLiteファイルを使ったセッションのセットアップ"""
#     db_file = tmp_path / "test.db"  # tmp_pathを使用して一時的なファイルを作成
#     engine = create_engine(f"sqlite:///{db_file}", echo=True)  # ディスク上のSQLite
#     Base.metadata.create_all(engine)  # テーブル作成

#     Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     db = Session()

#     yield db  # テストが終わったらセッションを閉じる

#     db.close()  # テスト後にセッションを閉じる

#     # テスト後にデータベースファイルを削除
#     if os.path.exists(db_file):
#         os.remove(db_file)


def test_create_run_record_valid(db_session: Session):
    """正常なレコードの作成をテスト"""
    record = create_run_record(
        db=db_session,
        dataset_summary="ds-summary",
        dataset_summary_code="summary-code",
        train_code="train-code",
        model_name="SomeClassifier",
        model_path="path/to/model",
        accuracy_val=0.95,
        accuracy_test=0.93,
        llm_name='gpt-oss:20b'
    )

    assert record.dataset_summary_code == "summary-code"
    assert record.train_code == "train-code"
    assert record.model_path == "path/to/model"
    assert record.accuracy_val == 0.95
    assert record.accuracy_test == 0.93


def test_create_run_record_missing_train_code(db_session: Session):
    """train_codeが欠けている場合のエラーチェック"""
    with pytest.raises(IntegrityError):  # IntegrityErrorが発生することを確認
        create_run_record(
            db=db_session,
            dataset_summary="ds-summary",
            dataset_summary_code="summary-code",
            train_code=None,  # train_codeがNone
            model_name="SomeClassifier",
            model_path="path/to/model",
            accuracy_val=0.95,
            accuracy_test=0.93
        )


def test_create_run_record_invalid_accuracy(db_session: Session):
    """accuracy_valやaccuracy_testが無効な値のとき"""
    with pytest.raises(sqlalchemy.exc.StatementError):  # StatementErrorが発生することを確認
        create_run_record(
            db=db_session,
            dataset_summary="ds-summary",
            dataset_summary_code="summary-code",
            train_code="train-code",
            model_name="SomeClassifier",
            model_path="path/to/model",
            accuracy_val="not-a-float",  # 無効な値
            accuracy_test=0.93
        )


def test_create_run_record_missing_accuracy(db_session: Session):
    """accuracy_valやaccuracy_testが欠けている場合"""
    with pytest.raises(IntegrityError):  # IntegrityErrorが発生することを確認
        create_run_record(
            db=db_session,
            dataset_summary="ds-summary",
            dataset_summary_code="summary-code",
            train_code="train-code",
            model_name="SomeClassifier",
            model_path="path/to/model",
            accuracy_val=None,  # accuracy_valがNone
            accuracy_test=None  # accuracy_testがNone
        )


def test_get_engine_and_session():
    """
    get_engine() と get_session() が正しく動作し、
    生成した Session で SQL が実行できることをテストする。

    テスト用 DB ファイルはテスト結果に関わらず必ず削除する。
    """

    test_db_path = "test_tmp_db.sqlite"

    # 念のため事前削除
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    try:
        # Engine 生成
        engine = get_engine(test_db_path)
        assert isinstance(engine, Engine)

        # Session 生成
        SessionLocal = get_session(test_db_path)
        session = SessionLocal()
        assert isinstance(session, Session)

        # SQL 実行できるか
        try:
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        finally:
            session.close()

        engine.dispose()

    finally:
        # --- テスト結果にかかわらず確実に削除 ---
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
