from mplm.db.crud import get_all_records_as_df
from mplm.db.session import get_session
from mplm.settings import settings
from mplm.utils.gcs import upload_file_to_gcs

df_record = get_all_records_as_df(db=get_session(db_path=settings.db_file)())
print(df_record)
local_csv_path = settings.db_file.replace('.db', '.csv')
gcs_csv_path = settings.db_file_gcs.replace('.db', '.csv')
df_record.to_csv(local_csv_path)
uploeded_gcs_path = upload_file_to_gcs(local_path=local_csv_path, gcs_path=gcs_csv_path, make_public=True)
print(f"Uploaded to {uploeded_gcs_path}")
