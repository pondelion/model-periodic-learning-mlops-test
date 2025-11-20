from mplm.settings import settings
from mplm.utils.gcs import upload_file_to_gcs

local_csv_path = "db/model_eval_results.csv"
gcs_csv_path = settings.db_file_gcs.replace('.db', '.csv')
print(gcs_csv_path)
csv_url = upload_file_to_gcs(local_path=local_csv_path, gcs_path=gcs_csv_path, make_public=True)
print(csv_url)
