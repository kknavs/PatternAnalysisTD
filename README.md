# PatternAnalysisTD
##### Software solution for the thesis: Analyzing patterns of visiting tourist destinations based on publicly available data

Use pip for installing necesarry libs/tools: 
$ pip install numpy networkx sqlalchemy matplotlib psycopg2 xlrd

*databaseEntities.py* - set properties that are important for interaction with database
- set the variable *selectedData* to one of possible option in class DataType. Make sure *ConnString* is valid (database is not created automatically) and server is running. 

In example postgressql is used and example for sqlite is present in comments, but sqlalchemy supports other databases as well: https://docs.sqlalchemy.org/en/latest/core/engines.html.

*LoadData.py* - load data from csv files and save to database, generate coocurrence graph.

*DrawGraph.py* - draw graph and find communities with Louvain or Infomap.
- in function *get_infomap_executable_path* change returned path to program that you built from Infomap source code: https://github.com/mapequation/infomap
 (with *make* on Unix type OS, on WIN it is more complicated - if you have Visual studio, this can be the simplest way). 

*GraphAnalysisOrange.py* - make analysis with Apriori algorithm.

NOTE: For thesis analysis on very big input file was done. The big files cannot be appended on github, so example with smaller csv file named 'test' has been added.
