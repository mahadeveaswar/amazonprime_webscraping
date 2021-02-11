import pandas as pd
import numpy as np
import seaborn as sns
import time
import matplotlib.pyplot as plt
from ast import literal_eval

tv_show_df = pd.read_csv('shows_data.csv')
tv_show_df = tv_show_df.drop(columns=['Unnamed: 0'])
tv_show_df['genre'] = tv_show_df['genre'].apply(literal_eval)
tv_show_df['content_advisory'] = tv_show_df['content_advisory'].apply(literal_eval)
# Based on imdb rating
tv_show_df['imdb_avg'] = round(tv_show_df.imdb_rating*2)/2

# Top 10 networks
net_df = tv_show_df.network.value_counts().nlargest(5).reset_index()
nw = sns.barplot(x='index',y='network',data=net_df)
nw.set_xticklabels(nw.get_xticklabels(),rotation=20)
plt.pause(3)
plt.close()

# imdb rating against Year
yr_imdb_df = tv_show_df.groupby(['start_year'])['imdb_avg'].agg('mean').nlargest(10).reset_index()
print(yr_imdb_df)

# viewer maturity against imdb rating
vm_imdb_df = tv_show_df.groupby(['viewer_maturity'])['imdb_avg'].agg('mean').nlargest(10).reset_index()
print(vm_imdb_df.loc[vm_imdb_df['imdb_avg']>0])

# top network against imdb rating
nw_imdb_df = tv_show_df.groupby(['network'])['imdb_avg'].agg('mean').nlargest(10).reset_index()
print(nw_imdb_df)

# avg_episode_runtime against imdb rating
aver_imdb_df = tv_show_df.groupby(['avg_episode_runtime'])['imdb_avg'].agg('mean').nlargest(10).reset_index()
print(aver_imdb_df)

# Viewer Maturity for shows
sns.countplot(x='viewer_maturity',data=tv_show_df)
plt.pause(3)
plt.close()

# Top 5 genres
genre_df = tv_show_df.copy()
genre_df = genre_df.explode('genre')
top5_gn_df = genre_df.groupby(['genre']).title.count().nlargest(5).reset_index()
sns.barplot(x='genre',y='title',data=top5_gn_df)
plt.pause(3)
plt.close()

# Shows count against year
top15_yr_df = tv_show_df.groupby(['start_year']).title.count().nlargest(15).reset_index()
top15_yr_df['count'] = top15_yr_df['title']
sns.barplot(x='start_year',y='count',data=top15_yr_df)
plt.pause(3)
plt.close()

# dropping the shows without rating
imdb_avg = tv_show_df['imdb_avg'].value_counts().iloc[1:]
ax = imdb_avg.plot(kind='bar')
ax.set_xlabel("imdb_approx_rating")
ax.set_ylabel("count")
plt.pause(3)
plt.close()

# genre & content advisory comparison
content_genre = genre_df.explode('content_advisory')
# top 5 content advisory
cg_df = content_genre.content_advisory.value_counts().nlargest(10).reset_index()
cg = sns.barplot(x='index',y='content_advisory',data=cg_df)
cg.set_xticklabels(cg.get_xticklabels(),rotation=30)
plt.pause(3)
plt.close()

# Content advisory against imdb rating
ca_imdb_df = content_genre.groupby(['content_advisory'])['imdb_avg'].agg('mean').nlargest(10).reset_index()
ca = sns.barplot(x='content_advisory',y='imdb_avg',data=ca_imdb_df)
ca.set_xticklabels(ca.get_xticklabels(),rotation=30)
plt.pause(3)
plt.close()