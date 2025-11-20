import pandas as pd

from mplm.db.crud import get_all_records_as_df
from mplm.db.session import get_session

SessionLocal = get_session()
session = SessionLocal()
df = get_all_records_as_df(session)
print(df)
print(df.columns.tolist())
df.to_csv('db/df_tmp.csv', index=False)
df2 = pd.read_csv("db/df_tmp.csv")
print(df2)
