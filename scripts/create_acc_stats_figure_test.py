import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter

from mplm.db.crud import get_all_records_as_df
from mplm.db.session import get_session
from mplm.settings import settings

df = get_all_records_as_df(db=get_session(db_path=settings.db_file)())

# 日付順にソート
df = df.sort_values("created_at")

sns.set(style="whitegrid", palette="pastel", font_scale=1.1)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))  # 2行2列

# --- Validation Accuracy 時系列 ---
sns.lineplot(
    data=df,
    x="created_at",
    y="accuracy_val",
    hue="llm_name",
    marker="o",
    ax=axes[0, 0]
)
axes[0, 0].set_title("Validation Accuracy over Time")
axes[0, 0].set_ylabel("accuracy_val")
axes[0, 0].set_xlabel("")
axes[0, 0].legend(title="LLM Name", bbox_to_anchor=(1.05, 1), loc="upper left")
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))  # 表示は日付のみ

# --- Test Accuracy 時系列 ---
sns.lineplot(
    data=df,
    x="created_at",
    y="accuracy_test",
    hue="llm_name",
    marker="o",
    ax=axes[0, 1]
)
axes[0, 1].set_title("Test Accuracy over Time")
axes[0, 1].set_ylabel("accuracy_test")
axes[0, 1].set_xlabel("")
axes[0, 1].legend().remove()
axes[0, 1].tick_params(axis='x', rotation=45)
axes[0, 1].xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))

# --- 分布 ---
sns.histplot(df, x="accuracy_val", hue="llm_name", multiple="stack", kde=True, ax=axes[1, 0], bins=70)
axes[1, 0].set_title("Validation Accuracy Distribution")
axes[1, 0].set_xlabel("accuracy_val")
axes[1, 0].set_ylabel("Count")
sns.move_legend(axes[1, 0], title="LLM Name", loc="upper left", bbox_to_anchor=(1.05, 1))

sns.histplot(df, x="accuracy_test", hue="llm_name", multiple="stack", kde=True, ax=axes[1, 1], bins=70)
axes[1, 1].set_title("Test Accuracy Distribution")
axes[1, 1].set_xlabel("accuracy_test")
axes[1, 1].set_ylabel("Count")
axes[1, 1].legend().remove()

plt.tight_layout()
plt.savefig("accuracy_summary.png", dpi=150)
plt.close()
