# Simplilearn AI and Machine Learning Cheat Sheet

Study notes based on the documents in `simplilearn_certdocs/Applied_data_science_with_python` and `simplilearn_certdocs/Machine_learning`.

## How to use this sheet

- Read each section like a quick refresher, not like a textbook chapter.
- Focus on the code patterns, formulas, and "when to use" notes.
- Revisit the capstone checklist at the end before assignments or exams.

---

## 1. Course Roadmap

### Data science workflow

1. Define the problem.
2. Collect data.
3. Inspect and clean data.
4. Explore patterns with statistics and visualization.
5. Engineer useful features.
6. Train and validate models.
7. Interpret results.
8. Deploy, monitor, and improve.

### AI vs ML vs Deep Learning

- Artificial Intelligence: broader field of building systems that show intelligent behavior.
- Machine Learning: systems learn patterns from data.
- Deep Learning: ML based on multi-layer neural networks.

### Main Python stack from the course

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
```

- `NumPy`: arrays and fast numeric computing
- `pandas`: tables, cleaning, grouping, joins
- `matplotlib` / `seaborn` / `plotly`: charts
- `scikit-learn`: ML workflows and evaluation
- `scipy` / `statsmodels`: statistics and hypothesis tests

---

## 2. NumPy

### What NumPy gives you

- N-dimensional arrays
- fast vectorized operations
- broadcasting
- indexing and slicing
- math and statistics functions

### Create arrays

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([[1, 2], [3, 4]])
z = np.zeros((2, 3))
o = np.ones((3, 3))
r = np.arange(0, 10, 2)
l = np.linspace(0, 1, 5)
```

### Important attributes

```python
b.ndim     # number of dimensions
b.shape    # rows, columns
b.size     # total elements
b.dtype    # data type
```

### Common operations

```python
a + 10
a * 2
a ** 2
np.sqrt(a)
np.mean(a)
np.median(a)
np.std(a)
np.sum(a)
```

### Indexing and slicing

```python
arr = np.array([10, 20, 30, 40, 50])
arr[0]        # 10
arr[-1]       # 50
arr[1:4]      # 20,30,40
arr[::2]      # step slicing

m = np.array([[1, 2, 3], [4, 5, 6]])
m[0, 1]       # 2
m[:, 1]       # second column
m[1, :]       # second row
```

### Reshaping

```python
x = np.arange(1, 7)
x.reshape(2, 3)
x.flatten()
x.transpose()
```

### Cheat note

- Use NumPy when data is mostly numeric and shape matters.
- Prefer vectorized operations over Python loops.

---

## 3. Pandas

### Core data structures

- `Series`: one-dimensional labeled data
- `DataFrame`: two-dimensional labeled table

### Create a DataFrame

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Ana", "Bob", "Cara"],
    "age": [23, 31, 27],
    "city": ["NY", "LA", "NY"]
})
```

### First inspection steps

```python
df.head()
df.tail()
df.shape
df.columns
df.info()
df.describe()
df.dtypes
```

### Selecting data

```python
df["age"]                  # one column
df[["name", "age"]]        # multiple columns
df.loc[0, "name"]          # label based
df.iloc[0, 1]              # position based
df[df["age"] > 25]         # filtering
```

### Sort, rename, drop

```python
df.sort_values("age", ascending=False)
df.rename(columns={"age": "Age"})
df.drop(columns=["city"])
```

### Missing values

```python
df.isna().sum()
df.dropna()
df.fillna(0)
df["age"].fillna(df["age"].mean(), inplace=True)
```

### Grouping and aggregation

```python
df.groupby("city")["age"].mean()
df.groupby("city").agg({"age": ["mean", "max", "count"]})
```

### Merge, join, concat

```python
pd.concat([df1, df2], axis=0)
pd.merge(df1, df2, on="id", how="inner")
df1.join(df2, how="left")
```

### Date and time

```python
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day_name"] = df["date"].dt.day_name()
```

### Text data

```python
df["name"].str.lower()
df["email"].str.contains("@gmail.com")
df["text"].str.replace("old", "new")
df["full"] = df["first"] + " " + df["last"]
```

### Cheat note

- `loc` is label-based.
- `iloc` is integer-position-based.
- In pandas, most cleaning work is column-wise and vectorized.

---

## 4. Data Visualization

### Why visualize

- detect trends
- compare categories
- spot outliers
- check distributions
- communicate results quickly

### Matplotlib basics

```python
import matplotlib.pyplot as plt

plt.plot(x, y)
plt.title("Sales Trend")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.show()
```

### Common chart choices

- line plot: trends over time
- bar chart: category comparison
- scatter plot: relationship between two numeric variables
- histogram: distribution of one feature
- box plot: spread, quartiles, outliers
- heatmap: correlation or matrix intensity

### Seaborn shortcuts

```python
sns.lineplot(data=df, x="month", y="sales")
sns.barplot(data=df, x="region", y="sales")
sns.scatterplot(data=df, x="total_bill", y="tip", hue="sex")
sns.histplot(data=df, x="age", kde=True)
sns.boxplot(data=df, x="department", y="salary")
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="Blues")
```

### Plotly use case

- use when you want interactive charts
- useful for hover details and dashboards

```python
import plotly.express as px
fig = px.scatter(df, x="sales", y="profit", color="region")
fig.show()
```

### Cheat note

- Always label axes and title.
- For skewed data, histogram + box plot is a strong first pass.

---

## 5. Linear Algebra for Data Science

### Core pieces

- scalar: single value
- vector: ordered list of values
- matrix: 2D grid of values
- tensor: higher-dimensional extension

### Vector operations

```python
import numpy as np

v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])

np.dot(v1, v2)         # dot product
np.cross(v1, v2)       # cross product
np.linalg.norm(v1)     # vector norm
```

### Matrix operations

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

A + B
A - B
A * 2
A @ B
A.T
np.linalg.det(A)
np.linalg.matrix_rank(A)
np.eye(3)
```

### Why it matters in ML

- features are vectors
- datasets are matrices
- distance, projection, optimization, and dimensionality reduction all rely on linear algebra

---

## 6. Statistics Fundamentals

### Types of statistics

- descriptive statistics: summarize data
- inferential statistics: draw conclusions from samples

### Types of data

- categorical: labels or groups
- numerical: discrete or continuous

### Measures of central tendency

```python
import numpy as np
import statistics

mean = np.mean(data)
median = np.median(data)
mode = statistics.mode(data)
```

- mean: average
- median: middle value
- mode: most frequent value

### Measures of dispersion

- range = max - min
- variance = average squared spread
- standard deviation = square root of variance
- percentile = relative position in data
- quartiles split data into four parts
- IQR = Q3 - Q1

```python
np.var(data)
np.std(data)
np.percentile(data, 25)
np.percentile(data, 75)
```

### Distribution shape

- skewness: asymmetry
- kurtosis: tail heaviness / peakedness

### Cheat note

- mean is sensitive to outliers
- median is safer for skewed data
- standard deviation is only meaningful with the mean when scale and spread matter together

---

## 7. Probability and Distributions

### Probability basics

```text
P(Event) = favorable outcomes / total outcomes
0 <= P(Event) <= 1
```

### Important distributions from the course

- Bernoulli: one trial, success/failure
- Binomial: number of successes in n independent trials
- Poisson: number of events in a fixed interval
- Normal: symmetric bell-shaped distribution
- Uniform: all values equally likely in an interval

### Quick intuition

- Bernoulli: one coin flip
- Binomial: count heads in 10 flips
- Poisson: number of calls per hour
- Normal: heights or many natural measurements
- Uniform: random number from 0 to 1

### SciPy examples

```python
from scipy.stats import bernoulli, binom, poisson, norm, uniform

binom.pmf(k=3, n=10, p=0.5)
poisson.pmf(k=4, mu=3)
norm.cdf(1.96)
uniform.rvs(size=5)
```

### Cheat note

- PMF: discrete probabilities
- PDF: continuous density
- CDF: probability up to a value

---

## 8. Advanced Statistics and Hypothesis Testing

### Key terms

- population: full group
- sample: subset of the population
- parameter: population measure
- statistic: sample measure

### Hypothesis testing flow

1. State null hypothesis `H0`.
2. State alternative hypothesis `H1`.
3. Choose significance level `alpha` such as 0.05.
4. Select test statistic.
5. Compute p-value.
6. Reject or fail to reject `H0`.

### Errors

- Type I error: reject true null hypothesis
- Type II error: fail to reject false null hypothesis

### Confidence interval and margin of error

```text
confidence interval = estimate +/- margin of error
```

- higher confidence -> wider interval
- larger sample -> narrower interval

### Z vs T

- use Z-test when population std is known or sample is large
- use T-test when population std is unknown and sample is smaller

### Common tests from the notebooks

- one-sample t-test
- paired t-test
- two-sample t-test
- z-test
- chi-square test
- ANOVA / F-test

### Python patterns

```python
from scipy.stats import ttest_1samp, chi2_contingency
from statsmodels.stats.weightstats import ztest

ttest_1samp(sample, popmean=50)
ztest(sample, value=50)
chi2_contingency(contingency_table)
```

### P-value decision rule

- if `p < alpha`: reject `H0`
- if `p >= alpha`: fail to reject `H0`

### Cheat note

- "Fail to reject" does not prove `H0` is true.
- Statistical significance is not the same as business significance.

---

## 9. Data Wrangling

### Goal

Turn raw data into analysis-ready data.

### Typical workflow

1. Load data
2. inspect structure
3. fix missing values
4. remove duplicates
5. clean formats and types
6. handle outliers
7. reshape / join / aggregate

### Inspection

```python
df.head()
df.info()
df.describe()
df.duplicated().sum()
df.isnull().sum()
```

### Missing data handling

```python
df.dropna()
df.fillna(df.mean(numeric_only=True))
df["city"].fillna(df["city"].mode()[0], inplace=True)
```

### Duplicates

```python
df.duplicated().sum()
df.drop_duplicates(inplace=True)
```

### Outliers

- detect with box plot, IQR, z-score
- treat by capping, winsorizing, transforming, or removing

```python
from scipy.stats.mstats import winsorize

df["income_capped"] = winsorize(df["income"], limits=[0.05, 0.05])
```

### Binning

```python
df["age_group"] = pd.cut(df["age"], bins=[0, 18, 35, 60, 100])
```

### Aggregation

```python
df.groupby("region")["sales"].sum()
df.pivot_table(values="sales", index="region", columns="product", aggfunc="mean")
```

### Reshaping

```python
pd.melt(df, id_vars=["id"])
df.pivot(index="date", columns="product", values="sales")
```

### Cheat note

- Clean data before modeling.
- Always verify type conversions after importing CSV or Excel files.

---

## 10. Feature Engineering

### Purpose

Create better inputs so the model can learn better patterns.

### Common techniques from the course

- transformation
- scaling
- encoding
- hashing
- grouping / aggregation

### Transform skewed variables

```python
import numpy as np
from scipy.stats import boxcox

df["log_income"] = np.log1p(df["income"])
df["sqrt_income"] = np.sqrt(df["income"])
df["boxcox_income"], lam = boxcox(df["income"])
```

### Scaling

```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
df[["age", "income"]] = scaler.fit_transform(df[["age", "income"]])
```

### Encoding

```python
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df["gender_label"] = le.fit_transform(df["gender"])

one_hot = pd.get_dummies(df["city"], prefix="city")
df = pd.concat([df, one_hot], axis=1)
```

### Hashing

```python
import hashlib

def hash_text(text):
    return hashlib.md5(text.encode()).hexdigest()
```

### Group features

```python
region_sales = df.groupby("region")["sales"].transform("mean")
df["region_avg_sales"] = region_sales
```

### Cheat note

- Fit scalers and encoders on training data only.
- Feature engineering must avoid target leakage.

---

## 11. Machine Learning Workflow

### Standard pipeline

1. Define target variable.
2. Split data into train and test sets.
3. Preprocess features.
4. Train model.
5. Evaluate.
6. Tune hyperparameters.
7. Compare models.

### Train-test split

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

### Cross-validation

```python
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold

scores = cross_val_score(model, X, y, cv=5)
```

### General rule

- regression predicts numbers
- classification predicts classes
- clustering finds groups without labels

---

## 12. Regression

### What regression does

Predicts continuous values such as price, revenue, demand, or temperature.

### Main types covered

- simple linear regression
- multiple linear regression
- polynomial regression
- Lasso regression
- Ridge regression
- Elastic Net regression

### Linear regression pattern

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
```

### Regression metrics

- MSE: penalizes large errors strongly
- RMSE: square root of MSE, easier to interpret
- MAE: average absolute error
- R2: proportion of variance explained

```text
RMSE = sqrt(MSE)
```

### Overfitting vs underfitting

- underfitting: model too simple, poor train and test performance
- overfitting: model too complex, great train but poor test performance

### Polynomial regression

```python
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)
```

### Regularization

- Lasso: can shrink some coefficients to zero
- Ridge: shrinks coefficients but rarely to zero
- Elastic Net: combination of L1 and L2

```python
from sklearn.linear_model import Lasso, Ridge, ElasticNet
```

### Cheat note

- Scale features for regularized models.
- Use cross-validation to choose regularization strength.

---

## 13. Classification

### What classification does

Predicts categories such as yes/no, fraud/not fraud, class A/B/C.

### Types from the course

- binary classification
- multiclass classification
- multilabel classification
- imbalanced classification

### Binary classification models covered

- logistic regression
- naive Bayes
- K-nearest neighbors
- decision tree
- support vector machine

### Logistic regression

```python
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression()
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
```

### Classification metrics

- accuracy = correct predictions / total predictions
- precision = TP / (TP + FP)
- recall = TP / (TP + FN)
- F1 = harmonic mean of precision and recall
- specificity = TN / (TN + FP)
- ROC-AUC measures ranking quality across thresholds

```python
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
```

### KNN intuition

- class is based on nearest points
- sensitive to scaling
- choose `k` carefully

### Naive Bayes intuition

- fast and simple
- assumes conditional independence
- useful for text and baseline models

### Decision tree intuition

- easy to interpret
- can overfit without pruning or depth control

### Multiclass classification

- one of many classes
- examples: species, customer segment, product category

### Multilabel classification

- one item can belong to multiple classes
- examples: image tags, article topics

### Imbalanced data handling

- oversampling
- undersampling
- SMOTE
- class weights
- precision-recall curve
- balanced ensembles

```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
```

### Cheat note

- For imbalanced data, accuracy alone can be misleading.
- Precision-recall is often more useful than ROC when positives are rare.

---

## 14. Ensemble Learning

### Main idea

Combine multiple models to get better performance than a single model.

### Categories

- parallel methods: models train independently
- sequential methods: models learn from previous errors

### Basic techniques

- voting
- averaging
- weighted averaging

### Voting classifier

```python
from sklearn.ensemble import VotingClassifier

ensemble = VotingClassifier(
    estimators=[
        ("lr", LogisticRegression()),
        ("dt", DecisionTreeClassifier()),
        ("svc", SVC(probability=True))
    ],
    voting="soft"
)
```

### Advanced methods

- bagging
- random forest
- boosting
- stacking

### Bagging

- trains many models on bootstrap samples
- reduces variance

### Boosting

- trains models sequentially
- later models focus on previous mistakes
- examples from notes: AdaBoost, Gradient Boosting, XGBoost, CatBoost

### Stacking

- predictions from base models become input to a meta-model

### Cheat note

- bagging is usually good for unstable learners like trees
- boosting can perform very well but may overfit noisy data if not tuned

---

## 15. Unsupervised Learning

### What it does

Learns structure from unlabeled data.

### Main areas from the course

- clustering
- dimensionality reduction
- association rule learning
- anomaly detection

### K-means clustering

```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(X)
```

- choose `k` using elbow method and silhouette score

### Hierarchical clustering

- builds nested clusters
- commonly visualized with dendrograms
- agglomerative: bottom-up
- divisive: top-down

### DBSCAN

- density-based clustering
- can detect noise points
- useful when clusters are irregular

### Silhouette score

- measures how well a point fits its cluster
- closer to 1 is better

```python
from sklearn.metrics import silhouette_score
silhouette_score(X, labels)
```

---

## 16. Dimensionality Reduction, Association Rules, and Anomaly Detection

### Why reduce dimensions

- faster training
- less noise
- easier visualization
- reduces multicollinearity

### PCA

- unsupervised feature extraction
- finds directions of maximum variance

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
```

### LDA

- supervised dimensionality reduction
- tries to separate classes well

```python
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
```

### t-SNE

- mainly for visualization of high-dimensional data
- preserves local neighborhoods

```python
from sklearn.manifold import TSNE
```

### Association rules

- finds items that occur together
- common in market basket analysis

Key measures:

- support: how often itemset appears
- confidence: how often rule is correct
- lift: strength of rule beyond random chance

```python
from mlxtend.frequent_patterns import apriori, association_rules
```

### Anomaly detection

- finds rare or unusual patterns

```python
from sklearn.ensemble import IsolationForest

iso = IsolationForest(random_state=42)
pred = iso.fit_predict(X)
```

---

## 17. Recommendation Systems

### Goal

Suggest items users are likely to prefer.

### Main types from the course

- collaborative filtering
- content-based filtering
- hybrid systems

### Collaborative filtering

- uses user-item interactions
- user-based: similar users
- item-based: similar items
- model-based: matrix factorization such as SVD

### Cosine similarity

```python
from sklearn.metrics.pairwise import cosine_similarity
```

- larger cosine similarity means more similar behavior or items

### SVD pattern

```python
from scipy.sparse.linalg import svds
```

- factorizes user-item matrix into lower-dimensional components
- useful for latent preferences

### Content-based filtering

- recommends items similar to what the user liked before
- based on item features instead of only ratings

### Hybrid filtering

- combines collaborative and content-based methods
- usually stronger in real systems

### Evaluation ideas

- RMSE for rating prediction
- hit rate / top-N relevance for ranking style systems

---

## 18. Lab, Project, and Capstone Pattern

### Repeated project structure in the docs

1. Understand the business problem.
2. Load the dataset.
3. Inspect columns and data quality.
4. Clean missing values and duplicates.
5. Explore patterns visually.
6. Engineer useful features.
7. Train an appropriate model.
8. Evaluate with the right metric.
9. Summarize findings in plain language.

### When doing a capstone, ask these first

- What is the target variable?
- Is this regression, classification, clustering, or recommendation?
- Are classes balanced?
- Do I need scaling?
- Are there missing values or outliers?
- Which metric matches the business goal?

### Fast checklist before submitting

- no obvious null handling mistakes
- no data leakage
- train/test split done correctly
- metric matches problem type
- charts are labeled
- conclusion explains business meaning

---

## 19. Quick Problem-to-Tool Map

### If your problem is...

- Predict sales or price -> regression
- Predict churn or fraud -> classification
- Group similar customers -> clustering
- Reduce many features -> PCA or LDA
- Recommend movies or products -> recommendation system
- Find rare suspicious cases -> anomaly detection
- Clean messy real-world data -> pandas + data wrangling

### If your data issue is...

- missing values -> `fillna()`, imputation
- duplicate rows -> `drop_duplicates()`
- skewed numeric feature -> `log1p`, `sqrt`, `boxcox`
- categorical text labels -> encoding
- too many features -> PCA / feature selection
- class imbalance -> SMOTE / class weighting / PR curve

---

## 20. Must-Remember Formulas

```text
Mean = sum(x) / n
Range = max - min
Variance = average squared deviation from the mean
Standard deviation = sqrt(variance)
IQR = Q3 - Q1
Probability = favorable / total
Accuracy = (TP + TN) / total
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 * Precision * Recall / (Precision + Recall)
RMSE = sqrt(MSE)
R2 = explained variance ratio
```

---

## 21. Exam and Revision Tips

- Know the difference between `loc` and `iloc`.
- Know when to use mean vs median.
- Know the difference between regression and classification.
- Know why scaling matters for KNN, SVM, and regularized models.
- Know why accuracy can fail on imbalanced datasets.
- Know the difference between bagging and boosting.
- Know the difference between PCA and LDA.
- Know the difference between collaborative and content-based recommendations.

---

## 22. Minimal End-to-End ML Skeleton

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

df = pd.read_csv("data.csv")

X = df.drop(columns=["target"])
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

pipe = Pipeline([
    ("scale", StandardScaler()),
    ("model", LogisticRegression())
])

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)

print(classification_report(y_test, y_pred))
```

---

## 23. Final Memory Hooks

- NumPy = arrays
- pandas = tables
- seaborn = easy plots
- statistics = summarize data
- probability = uncertainty
- hypothesis testing = evidence for decisions
- wrangling = clean before modeling
- feature engineering = improve inputs
- regression = predict numbers
- classification = predict labels
- clustering = find hidden groups
- ensemble = combine models
- recommendation = personalize choices

