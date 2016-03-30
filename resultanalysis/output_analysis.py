__author__ = 'Peeratham'
# https://bitbucket.org/hrojas/learn-pandas

# The usual preamble
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pymongo import MongoClient

output_dir = 'C:/Users/Peeratham/Dropbox/research_papers/smell_analysis/';

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
                u'Too Long Script', u'Uncommunicative Naming', u'Unreachable Code', u'Duplicate Code']
extra_attributes = [u'scriptCount']

freq = lambda item: len(item) if isinstance(item,list) else item
smell_freq = {smell:[freq(smell_record) for smell_record in reports_df[smell]] for smell in smell_names+extra_attributes}
smell_freq_reports_df = pd.DataFrame(smell_freq,reports_df.index.values)

# join smell report with project specific mastery score
smell_report_with_mastery = smell_freq_reports_df.join(mastery_scores_df)
# next combine with metadata
full_report_df = pd.concat([metadata_df, smell_freq_reports_df],axis=1)
# drop all with NaN, those that is failed to be parsed /analyzed
full_report_df = full_report_df.dropna(axis='index')
# drop where scriptCount = 0
full_report_df = full_report_df[full_report_df['scriptCount']>0]
# sorting by scriptCount
# meta_reports_df = meta_reports_df.sort_values(['scriptCount'], ascending=[0])

# histogram of smells found for each mastery group
# Parallel Coordinates for three different skill level


smell_occurrences = full_report_df[smell_names]
overall_smell_df = pd.DataFrame(smell_occurrences)

def write_latex(latex_str, file_name):
    fo = open(output_dir+file_name+'.tex', 'w')
    fo.seek(0)
    fo.write(latex_str)
    fo.truncate()
    fo.close()

###### table1 smell instance founds across all N projects (taken into account dropped records) #############
aggregate_smell_df = pd.DataFrame(smell_occurrences.sum(axis='index'), columns=['occurrences'])
print(aggregate_smell_df)
write_latex(aggregate_smell_df.to_latex(), 'table1');

# ax = aggregate_smell_df.plot(kind='bar', figsize=(8,12), color=current_palette, rot=0)
# for p in ax.patches:
#     ax.annotate(str(int(p.get_height())), (p.get_x()+p.get_width()/2., p.get_height(), ),ha='center', va='center', xytext=(0, 10), textcoords='offset points')
# plt.show()


###### table 2 percent of projects inflicted with each kind of smell #######################################
smell_exist_or_not_df = smell_occurrences.applymap(lambda count: 1 if count > 0 else 0)
aggregate_smelly_projects = smell_exist_or_not_df.sum(axis=0)
smell_exist_or_not_df_percent = aggregate_smelly_projects/len(smell_exist_or_not_df)
smell_exist_or_not_df_percent = smell_exist_or_not_df_percent.to_frame("Percentage of projects")
print(smell_exist_or_not_df_percent)

write_latex(smell_exist_or_not_df_percent.to_latex(), 'table2')
# aggregate_smelly_projects.plot(kind='bar', figsize=(8,12), color=current_palette, rot=0)
# plt.show()

###### table 3 percent of projects contains 1 type of smell, 2 ,3 ...
distict_smells_per_project = smell_occurrences.apply(lambda record: sum([1 if record[smell]>0 else 0 for smell in smell_names]),axis='columns')
distict_smells_per_project = distict_smells_per_project.value_counts().sort_index()
distict_smells_per_project /= distict_smells_per_project.sum()  #proportion
distict_smells_per_project.plot(kind='bar',figsize=(8,12), color=current_palette)
print(distict_smells_per_project)
distict_smells_per_project.show()







# ------------------------------------
print("===Average Smell found===")
print(smell_freq_reports_df.mean(axis=0))

print("===Max Smell found===")
print(smell_freq_reports_df.max(axis=0))

print(smell_freq_reports_df.describe())

print(metadata_df.describe())