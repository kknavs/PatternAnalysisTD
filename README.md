# PatternAnalysisTD
##### Software solution for the thesis: Analyzing patterns of visiting tourist destinations based on publicly available data

*databaseEntities.py* - set properties that are important for interaction with database
- set the variable *selectedData* to one of possible option in class DataType. Make sure *ConnString* is valid (database is not created automatically) and server is running. 

In example postgressql is used and example for sqlite is present in comments, but sqlalchemy supports other databases as well: https://docs.sqlalchemy.org/en/latest/core/engines.html.

*LoadData.py* - load data from csv files and save to database, generate coocurrence graph.

*DrawGraph.py* - draw graph and find communities with Louvain or Infomap.

*GraphAnalysisOrange.py* - make analysis with Apriori algorithm.

NOTE: For thesis analysis on very big input file was done. The big files cannot be appended on github, so example with smaller csv will be added.
TODO: example with smaller csv file named 'test'
