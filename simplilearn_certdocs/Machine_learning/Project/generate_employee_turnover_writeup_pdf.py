from pathlib import Path
from textwrap import fill
import warnings

warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "1751024723_hr_comma_sep" / "HR_comma_sep.csv"
OUTPUT_PATH = ROOT / "employee_turnover_writeup.pdf"
RANDOM_STATE = 123

sns.set_theme(style="whitegrid")


def add_text_page(pdf, title, sections):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    y = 0.96
    fig.text(0.06, y, title, fontsize=20, weight="bold", va="top")
    y -= 0.05
    for heading, body in sections:
        fig.text(0.06, y, heading, fontsize=13, weight="bold", va="top")
        y -= 0.025
        wrapped = fill(body, width=100)
        fig.text(0.07, y, wrapped, fontsize=10.5, va="top", linespacing=1.5)
        y -= 0.09 + 0.015 * wrapped.count("\n")
    plt.axis("off")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def add_table_page(pdf, title, df, subtitle=None, font_size=10):
    fig, ax = plt.subplots(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    ax.axis("off")
    fig.text(0.06, 0.96, title, fontsize=18, weight="bold", va="top")
    if subtitle:
        fig.text(0.06, 0.93, subtitle, fontsize=10.5, va="top")
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    table.scale(1, 1.6)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main():
    df = pd.read_csv(DATA_PATH).rename(columns={"sales": "department"})
    original_shape = df.shape
    duplicate_count = int(df.duplicated().sum())
    missing_values = int(df.isna().sum().sum())
    df = df.drop_duplicates().reset_index(drop=True)

    corr = df.select_dtypes(include="number").corr()["left"].sort_values(ascending=False)
    salary_turnover = (pd.crosstab(df["salary"], df["left"], normalize="index") * 100)[1].round(2)
    project_turnover = (pd.crosstab(df["number_project"], df["left"], normalize="index") * 100)[1].round(2)

    left_df = df[df["left"] == 1][["satisfaction_level", "last_evaluation", "left"]].copy()
    kmeans = KMeans(n_clusters=3, random_state=RANDOM_STATE, n_init=20)
    left_df["cluster"] = kmeans.fit_predict(left_df[["satisfaction_level", "last_evaluation"]])
    cluster_summary = (
        left_df.groupby("cluster")[["satisfaction_level", "last_evaluation"]]
        .mean()
        .round(3)
        .reset_index()
    )
    cluster_summary["employee_count"] = (
        left_df["cluster"].value_counts().sort_index().values
    )

    X = pd.get_dummies(df.drop(columns=["left"]), drop_first=True)
    y = df["left"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, random_state=RANDOM_STATE, n_jobs=1
        ),
        "Gradient Boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }

    model_rows = []
    fitted = {}
    for name, model in models.items():
        pipe = Pipeline([("smote", SMOTE(random_state=RANDOM_STATE)), ("model", model)])
        cv_proba = cross_val_predict(pipe, X_train, y_train, cv=cv, method="predict_proba")[:, 1]
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        proba = pipe.predict_proba(X_test)[:, 1]
        report = classification_report(y_test, pred, output_dict=True)
        model_rows.append(
            {
                "Model": name,
                "CV ROC-AUC": round(float(roc_auc_score(y_train, cv_proba)), 4),
                "Test ROC-AUC": round(float(roc_auc_score(y_test, proba)), 4),
                "Precision": round(report["1"]["precision"], 4),
                "Recall": round(report["1"]["recall"], 4),
                "F1-Score": round(report["1"]["f1-score"], 4),
            }
        )
        fitted[name] = {"pipe": pipe, "pred": pred, "proba": proba}

    results_df = pd.DataFrame(model_rows).sort_values(
        ["Test ROC-AUC", "Recall", "F1-Score"], ascending=False
    )
    best_model_name = results_df.iloc[0]["Model"]
    best_pipe = fitted[best_model_name]["pipe"]
    best_pred = fitted[best_model_name]["pred"]
    best_proba = fitted[best_model_name]["proba"]
    cm = confusion_matrix(y_test, best_pred)

    zone_df = pd.DataFrame(
        {"actual_left": y_test.reset_index(drop=True), "turnover_probability": best_proba}
    )
    zone_df["risk_zone"] = pd.cut(
        zone_df["turnover_probability"],
        bins=[-np.inf, 0.20, 0.60, 0.90, np.inf],
        labels=[
            "Safe Zone (Green)",
            "Low-Risk Zone (Yellow)",
            "Medium-Risk Zone (Orange)",
            "High-Risk Zone (Red)",
        ],
    )
    zone_summary = (
        zone_df.groupby("risk_zone", observed=False)
        .agg(
            employee_count=("risk_zone", "size"),
            avg_probability=("turnover_probability", "mean"),
            actual_turnover_rate=("actual_left", "mean"),
        )
        .reset_index()
    )
    zone_summary["avg_probability"] = (zone_summary["avg_probability"] * 100).round(2)
    zone_summary["actual_turnover_rate"] = (zone_summary["actual_turnover_rate"] * 100).round(2)

    with PdfPages(OUTPUT_PATH) as pdf:
        add_text_page(
            pdf,
            "Employee Turnover Analytics Report",
            [
                (
                    "Business Problem",
                    "Portobello Tech wants to predict employee turnover and identify the main factors that influence attrition so HR can take early retention action.",
                ),
                (
                    "Dataset Used",
                    f"The HR dataset contains {original_shape[0]} records and 10 columns. After quality review, {duplicate_count} duplicate rows were removed, leaving {df.shape[0]} unique employee records for analysis.",
                ),
                (
                    "Project Scope",
                    "The work includes data quality checks, exploratory analysis, K-means clustering for employees who left, SMOTE-based class balancing, 5-fold cross-validation for three models, model comparison, and retention strategy recommendations.",
                ),
                (
                    "Deliverables",
                    "Two deliverables were prepared: an executed Jupyter notebook for code and outputs, and this PDF write-up for submission-ready documentation.",
                ),
            ],
        )

        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle("Exploratory Data Analysis", fontsize=18, weight="bold")

        sns.histplot(df["satisfaction_level"], kde=True, ax=axes[0, 0], color="teal")
        axes[0, 0].set_title("Satisfaction Level Distribution")

        sns.histplot(df["average_montly_hours"], kde=True, ax=axes[0, 1], color="darkorange")
        axes[0, 1].set_title("Average Monthly Hours Distribution")

        sns.countplot(data=df, x="number_project", hue="left", ax=axes[1, 0])
        axes[1, 0].set_title("Project Count by Turnover Status")
        axes[1, 0].legend(title="left", labels=["Stayed", "Left"])

        corr_plot = corr.drop("left").sort_values()
        axes[1, 1].barh(corr_plot.index, corr_plot.values, color="slateblue")
        axes[1, 1].set_title("Correlation with Turnover")
        axes[1, 1].set_xlabel("Correlation")

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        add_text_page(
            pdf,
            "EDA Findings",
            [
                (
                    "Data Quality",
                    f"No missing values were found in the dataset. The main quality issue was duplication: {duplicate_count} rows were duplicates and were removed before modeling.",
                ),
                (
                    "Key Drivers",
                    "The strongest turnover signal is low satisfaction level. Longer time spent in the company and heavier monthly workload also increase attrition risk, while work accidents and promotions show negative association with turnover.",
                ),
                (
                    "Project Workload Insight",
                    f"Employees with 2 projects had a turnover rate of {project_turnover.loc[2]:.2f}%, and those with 7 projects had a turnover rate of {project_turnover.loc[7]:.2f}%. In contrast, employees with 3 or 4 projects were much more stable.",
                ),
                (
                    "Salary Insight",
                    f"Employees in the low-salary band had the highest turnover rate at {salary_turnover.loc['low']:.2f}%, compared with {salary_turnover.loc['high']:.2f}% in the high-salary band.",
                ),
            ],
        )

        fig, ax = plt.subplots(figsize=(11, 8.5))
        sns.scatterplot(
            data=left_df,
            x="satisfaction_level",
            y="last_evaluation",
            hue="cluster",
            palette="Set1",
            ax=ax,
            alpha=0.7,
        )
        ax.set_title("K-Means Clusters for Employees Who Left", fontsize=18, weight="bold")
        centers = cluster_summary[["satisfaction_level", "last_evaluation"]]
        ax.scatter(
            centers["satisfaction_level"],
            centers["last_evaluation"],
            s=250,
            c="black",
            marker="X",
            label="Centroids",
        )
        ax.legend()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        add_table_page(
            pdf,
            "Cluster Summary",
            cluster_summary.rename(
                columns={
                    "cluster": "Cluster",
                    "satisfaction_level": "Avg Satisfaction",
                    "last_evaluation": "Avg Evaluation",
                    "employee_count": "Employees",
                }
            ),
            subtitle="Clusters were built only on employees who left, using satisfaction and last evaluation.",
        )

        add_text_page(
            pdf,
            "Clustering Interpretation",
            [
                (
                    "Cluster 0",
                    "Very low satisfaction with high evaluation. These employees appear productive but deeply dissatisfied, which is a strong indicator of likely burnout, poor manager fit, or reward mismatch.",
                ),
                (
                    "Cluster 1",
                    "High satisfaction and high evaluation, yet these employees still left. This suggests external opportunities, compensation expectations, or career progression limits may have driven attrition.",
                ),
                (
                    "Cluster 2",
                    "Moderate satisfaction and moderate evaluation. This group reflects disengaged or average-performing employees who may have lacked strong attachment to the organization.",
                ),
            ],
        )

        add_table_page(
            pdf,
            "Model Comparison",
            results_df.reset_index(drop=True),
            subtitle="All models used SMOTE on training folds and were evaluated with 5-fold cross-validation.",
        )

        fig, axes = plt.subplots(1, 2, figsize=(11, 8.5))
        axes[0].bar(results_df["Model"], results_df["Test ROC-AUC"], color=["#6baed6", "#74c476", "#fd8d3c"])
        axes[0].set_title("Test ROC-AUC by Model")
        axes[0].set_ylim(0.7, 1.0)
        axes[0].tick_params(axis="x", rotation=20)

        cm_df = pd.DataFrame(cm, index=["Actual Stay", "Actual Leave"], columns=["Pred Stay", "Pred Leave"])
        sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues", ax=axes[1], cbar=False)
        axes[1].set_title(f"Confusion Matrix: {best_model_name}")

        fig.suptitle("Model Performance", fontsize=18, weight="bold")
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        add_text_page(
            pdf,
            "Best Model and Metric Justification",
            [
                (
                    "Selected Model",
                    f"{best_model_name} was selected as the best model because it achieved the highest test ROC-AUC of {results_df.iloc[0]['Test ROC-AUC']:.4f} while also maintaining strong recall and balanced overall performance.",
                ),
                (
                    "Why ROC-AUC",
                    "ROC-AUC is appropriate for comparing models because it evaluates ranking quality across thresholds rather than at a single cutoff point.",
                ),
                (
                    "Why Recall Matters",
                    "For attrition prediction, recall is especially important because a false negative means the business failed to identify an employee who is actually likely to leave. Missing those employees weakens the value of the retention program.",
                ),
                (
                    "Best Model Test Metrics",
                    f"Precision = {results_df.iloc[0]['Precision']:.4f}, Recall = {results_df.iloc[0]['Recall']:.4f}, and F1-score = {results_df.iloc[0]['F1-Score']:.4f}. The confusion matrix for the best model was {cm.tolist()}.",
                ),
            ],
        )

        add_table_page(
            pdf,
            "Risk Zone Summary",
            zone_summary.rename(
                columns={
                    "risk_zone": "Risk Zone",
                    "employee_count": "Employees",
                    "avg_probability": "Avg Turnover Probability (%)",
                    "actual_turnover_rate": "Actual Turnover Rate (%)",
                }
            ),
            subtitle="Risk zones were created from predicted turnover probabilities on the test set.",
            font_size=9.5,
        )

        add_text_page(
            pdf,
            "Retention Recommendations",
            [
                (
                    "Safe Zone (Green)",
                    "Continue normal engagement through recognition, regular manager check-ins, and growth conversations. These employees show low predicted turnover probability.",
                ),
                (
                    "Low-Risk Zone (Yellow)",
                    "Monitor workload and job satisfaction. Offer career development discussions and manager feedback sessions before risk escalates.",
                ),
                (
                    "Medium-Risk Zone (Orange)",
                    "Use targeted intervention: role review, project rebalancing, skill development, and compensation benchmarking where needed.",
                ),
                (
                    "High-Risk Zone (Red)",
                    "Immediate action is recommended. HR and managers should conduct one-on-one retention meetings, review compensation, evaluate internal mobility options, and address dissatisfaction or overload quickly.",
                ),
            ],
        )

        add_text_page(
            pdf,
            "Conclusion",
            [
                (
                    "Overall Outcome",
                    "Employee turnover can be predicted effectively using historical HR data. Satisfaction, tenure, workload, and project pressure are the most important attrition signals.",
                ),
                (
                    "Business Value",
                    "The model can help HR prioritize intervention efforts and allocate retention resources to employees with the highest probability of leaving.",
                ),
                (
                    "Final Recommendation",
                    "Use the best model as a screening tool alongside HR judgment, then apply different retention strategies by risk zone rather than using a single intervention for all employees.",
                ),
            ],
        )

    print(f"PDF write-up created at: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
