__author__ = 'Peeratham'
# https://bitbucket.org/hrojas/learn-pandas

# The usual preamble
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pymongo import MongoClient



def score(mastery_report):
    total = 0
    for concept in mastery_report.keys():
        total+=mastery_report[concept]
    return total


# map metadata[projectID] => creatorName
# score(creators_df[creatorName]) =?

# style and color setting
sns.set()
current_palette = sns.color_palette()

# database configuration
db = MongoClient()['test']
metadata_df = pd.DataFrame(list(db['metadata'].find()))
metadata_df = metadata_df.set_index(['_id'], drop=True)
reports_df = pd.DataFrame(list(db['reports'].find()))
reports_df = reports_df.set_index(['_id'], drop=True)
creators_df = pd.DataFrame(list(db['creators'].find()))

# Master score
mastery_reports = reports_df['Mastery Level']
mastery_scores = {'mastery_score': pd.Series([score(record) for record in mastery_reports.values], mastery_reports.index)}
mastery_scores_df = pd.DataFrame(mastery_scores)

# Smell Result
# all available analysis: reports_df.columns.values
smell_names = [ u'BroadCastWorkaround', u'Too Broad Variable Scope',
                u'Too Long Script', u'Uncommunicative Naming', u'Unreachable Code', u'Duplicate Code',
                u'scriptCount']

freq = lambda item: len(item) if isinstance(item,list) else item
smell_freq = {smell:[freq(smell_record) for smell_record in reports_df[smell]] for smell in smell_names}
smell_freq_reports_df = pd.DataFrame(smell_freq,reports_df.index.values)

# join smell report with project specific mastery score
smell_report_with_mastery = smell_freq_reports_df.join(mastery_scores_df)
# next combine with metadata
meta_reports_df = pd.concat([metadata_df, smell_freq_reports_df],axis=1)
# drop all with NaN, those that is failed to be parsed /analyzed
meta_reports_df = meta_reports_df.dropna(axis='index')
# drop trivial project where script < 1 : some project is only a drawing
meta_reports_df = meta_reports_df.dropna(axis='index')
# drop where scriptCount = 0
meta_reports_df = meta_reports_df[meta_reports_df['scriptCount']>0]
# sorting by scriptCount
meta_reports_df = meta_reports_df.sort_values(['scriptCount'], ascending=[0])

# histogram of smells found for each mastery group
# Parallel Coordinates for three different skill level




print("===Average Smell found===")
print(smell_freq_reports_df.mean(axis=0))

print("===Max Smell found===")
print(smell_freq_reports_df.max(axis=0))

print(smell_freq_reports_df.describe())

print(metadata_df.describe())

only_smells_and_id_df = meta_reports_df[smell_names]
overall_smell_df = pd.DataFrame(only_smells_and_id_df)


aggregate_smell_df = pd.DataFrame(only_smells_and_id_df.sum(axis='index'), columns=['frequency'])
print(aggregate_smell_df.columns.values)
print(aggregate_smell_df)
ax = aggregate_smell_df.plot(kind='bar', figsize=(8,12), color=current_palette, rot=0)
for p in ax.patches:
    ax.annotate(str(int(p.get_height())), (p.get_x()+p.get_width()/2., p.get_height(), ),ha='center', va='center', xytext=(0, 10), textcoords='offset points')
plt.show()


# frequency of distinct code smell exists in each project
def unique_count(row):
    unique = [1 if row[col]>0 else 0 for col in smell_names]
    return sum(unique)

unique_smell_cnt = only_smells_and_id_df.apply(unique_count,axis='columns')
unique_smell_cnt = unique_smell_cnt.value_counts().sort_index()
unique_smell_cnt /= unique_smell_cnt.sum()  #proportion
unique_smell_cnt.plot(kind='bar',figsize=(8,12), color=current_palette)
unique_smell_cnt.show()






