import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
#import squarify as sq
import numpy
import matplotlib
import plotly.express as px



def premier_plot(path):
         con = sqlite3.connect(path)
         cur = con.cursor()
         command = f"""
         SELECT c.abs_count, s.building, s.surface
         FROM Samples s NATURAL JOIN Counts c
         """
         res = cur.execute(command)
         result = res.fetchall()
         con.commit()
         con.close()


         dict_city = {}
         for item in result :
                  name = item[1]
                  if name not in dict_city.keys():
                           dict_city[name] = float(item[0])
                  else :
                           dict_city[name] += float(item[0])

         df = pd.DataFrame({'Proportion':list(dict_city.values()),'Building_prelevement':list(dict_city.keys())})
         
         fig = px.bar(df,x='Building_prelevement',y='Proportion',title="Proportion d'individus en general dans chaque batiment.",color='Proportion',color_continuous_scale='rdylbu')

         return fig



#This plot display a bar plot to represent the environment of a building precisely
def update_plot(district,path):
    dict_fin={}
    
    
    if district == 'both' :
        selection_building = ('ekeley','porter')
    elif district == 'ekeley' :
        selection_building = ('ekeley','ekeley')
    elif district == 'porter' :
        selection_building = ('porter','porter')
            
    con = sqlite3.connect(path)
    cur = con.cursor()
    command = f"""
        SELECT c.abs_count, s.building, s.surface
        FROM Samples s NATURAL JOIN Counts c
        WHERE s.building = '{selection_building[0]}' OR s.building = '{selection_building[1]}'
    """
    res = cur.execute(command)
    result = res.fetchall()
    con.commit()
    con.close()
    
    dict_elem = {}
    
    for item in result :
        name = item[1]+'_'+item[2]
        if name not in dict_elem.keys() :
            dict_elem[name] = float(item[0])
        else :
            dict_elem[name] += float(item[0])
    
    dict_fin = dict(sorted(dict_elem.items(), key=lambda x:x[1]))
    
    df_barplot = pd.DataFrame({'lieu':[item for item in dict_fin.keys()] ,
                          'proportion':list(dict_fin.values())})
    
    fig = px.bar(df_barplot, x='lieu', y='proportion',color='proportion', color_continuous_scale='PuRd',
             title="Proportion individus retrouver dans chaque environnement.",labels={"lieu":"Environnement de prélévement","proportion":"Proportion"})
    return fig



#This plot display the treemap by building and by surface
import plotly.express as px
def treemap_plotly(district,place,path,plot):
    '''
    con1 = sqlite3.connect(path)
    
    cur1 = con1.cursor()
    command1 = f"""
        SELECT t.phylum, t.class, t._order
        FROM Taxa t NATURAL JOIN Counts NATURAL JOIN Samples s
        WHERE s.building = '{district}' AND s.surface = '{place}'
    """
    
    res1 = cur1.execute(command1)
    result1 = res1.fetchall()
    con1.commit()
    con1.close()

    dict_comptage = {}
    for item in result1:
        if item not in dict_comptage.keys():
            dict_comptage[item] = 1
        else :
            dict_comptage[item] += 1
            
    
    df_ply = pd.DataFrame({'phylum':[item[0] for item in result1],
                           'class':[item[1] for item in result1],
                           'order':[item[2] for item in result1],
                          'nb_indiv':[dict_comptage[item] for item in result1]})

    df_ply = df_ply.dropna()
    '''

    from sqlite3 import connect
    command1 = f"""
        SELECT t.phylum, t.class, t._order, SUM(c.abs_count) as count
        FROM Taxa t NATURAL JOIN Counts as c NATURAL JOIN Samples s
        WHERE s.building = 'ekeley' AND s.surface = 'door in'
        group by t.phylum, t.class, t._order
    """

    requete = pd.read_sql(command1,connect(path))
    
    if plot == 'treemap' :
        f = px.treemap(requete.fillna(''),path=['class','_order'],values='count',color='class')
    elif plot == 'sunburst' :
        f = px.sunburst(requete.fillna(''),path=['class','_order'],values='count',color='class')

    return f


def acp(color,path):
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    con =  sqlite3.connect(path)

    res = pd.read_sql("""
        SELECT c.rel_count, c.OTU_ID, c.SAMPLE_ID, s.gender, s.building, s.surface, s.floor
        FROM Counts c NATURAL JOIN Samples s
    """,con)

    df = res.pivot(index=['SAMPLE_ID','gender','building','surface', "floor"],values='rel_count',columns='OTU_ID')

    SS = StandardScaler()
    SS.fit(df)
    Xnorm = SS.transform(df)

    
    pca = PCA(n_components=3)
    pca.fit(df)

    X_pca = pca.transform(df)

    fig=px.scatter_3d(x=X_pca[:, 0], y=X_pca[:, 1],z=X_pca[:, 2],color= df.index.get_level_values(color))

    return fig

def heatmap(path) :
    from scipy.spatial.distance import euclidean
    con =  sqlite3.connect(path)

    res3 =pd.read_sql("""
    select *
    from Samples 
    """, con)


    count = pd.read_sql("""
    select rel_count, SAMPLE_ID, OTU_ID from Counts
    """, con)
    count = count.pivot(columns="SAMPLE_ID", index="OTU_ID", values = "rel_count")

    q=res3["SAMPLE_ID"].to_frame()
    qq=q.merge(q, how='cross')
    qq["distance"] = None

    for i, v in qq.iterrows():
        s1, s2 = v["SAMPLE_ID_x"], v["SAMPLE_ID_y"]
        qq.loc[i, "distance"] = euclidean(count[s1],count[s2])


    heatmap=qq.pivot(columns=["SAMPLE_ID_y"],index="SAMPLE_ID_x",values='distance')


    return px.imshow(heatmap,color_continuous_scale='inferno')