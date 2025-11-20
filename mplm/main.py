"""
Entry point for automated Titanic model training agent.
"""

from pprint import pprint

from mplm.agent.automatic_model_build_agent import build_workflow, save_run_to_db
from mplm.db.base import init_db
from mplm.db.crud import get_all_records_as_df
from mplm.db.download_db_file import download_db_from_gcs_if_exists
from mplm.db.session import get_engine, get_session
from mplm.models.state import WorkflowState
from mplm.services.data_loader import load_titanic_dataset
from mplm.settings import settings
from mplm.utils.gcs import upload_file_to_gcs
from mplm.utils.logger import get_logger
from mplm.utils.visualization import plot_accuracy_summary

# from mplm.llm.client import get_llm

logger = get_logger(__name__)


def print_workflow_state(state: WorkflowState):
    """
    Nicely print the WorkflowState while omitting large/unnecessary fields:
    df, metadata, llm, fixed_code
    """
    display_state = {}

    for key, value in state.items():
        if key in {"df", "metadata", "llm", "previous_code", "fixed_code"}:
            continue
        elif key == "summary_result" and value is not None:
            display_state[key] = {
                "summary_text": value.summary_text,
                "summary_code": value.summary_code,
            }
        elif key == "training_result" and value is not None:
            display_state[key] = {
                "accuracy_val": value.accuracy_val,
                "accuracy_test": value.accuracy_test,
                "model_name": value.model_name,
                "model_path": value.model_path,
                "train_code": value.code,
            }
        else:
            display_state[key] = value

    pprint(display_state, width=120)


def main():
    settings.print_settings()
    local_db_path = settings.db_file
    gcs_db_path = settings.db_file_gcs
    logger.info("Download DB file from GCS...")
    download_db_from_gcs_if_exists(
        local_db_path=local_db_path,
        gcs_db_path=gcs_db_path,
    )

    logger.info("Initializing DB...")
    init_db(get_engine())

    logger.info("Loading Titanic dataset...")
    df, metadata = load_titanic_dataset()

    # llm = get_llm(temperature=2.0)

    state: WorkflowState = {
        "df": df,
        "target_column": "survived",
        "metadata": metadata,
        "retries": 0,
        # "llm": llm,
    }

    logger.info("Running workflow...")
    workflow = build_workflow(max_retry=4)
    final_state = workflow.invoke(state, debug=False)

    print_workflow_state(final_state)

    if final_state['status'] == "ok":
        logger.info("Workflow completed succesfully. Saving results...")
        save_run_to_db(final_state)

        logger.info("Uploading db file to GCS")
        uploeded_gcs_path = upload_file_to_gcs(local_path=local_db_path, gcs_path=gcs_db_path)
        logger.info(f"Uploaded to {uploeded_gcs_path}")

        logger.info("Exporting to csv file and uploading to GCS")
        df_record = get_all_records_as_df(db=get_session(db_path=local_db_path)())
        local_csv_path = local_db_path.replace('.db', '.csv')
        gcs_csv_path = gcs_db_path.replace('.db', '.csv')
        df_record.to_csv(local_csv_path)
        csv_url = upload_file_to_gcs(local_path=local_csv_path, gcs_path=gcs_csv_path, make_public=True)
        logger.info(f"Uploaded ({len(df_record)} records). Can be accessed at {csv_url}")

        logger.info("Creating accuracy summary figure and uploading to GCS")
        local_fig_path = local_db_path.replace('.db', '.png')
        gcs_fig_path = gcs_db_path.replace('.db', '.png')
        plot_accuracy_summary(df_record, output_filepath=local_fig_path)
        fig_url = upload_file_to_gcs(local_path=local_fig_path, gcs_path=gcs_fig_path, make_public=True)
        logger.info(f"Uploaded. Can be accessed at {fig_url}")
    else:
        logger.error("Workflow failed")

    logger.info("All done.")


if __name__ == "__main__":
    main()
