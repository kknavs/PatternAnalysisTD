# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

import snap.win.snap
from Database import fetchall_links_with_weight_threshold, get_destinations, get_max_weight, \
    folder, DataType, selectedData

#from networkx.algorithms import community as community_nx

#The page http://www.swig.org/download.html has a specific download for Windows with a pre-built version of swig.exe.
##  You can download it and avoid the hassle of compiling swig by yourself.
#C:\Program Files\swigwin-3.0.12  sprem.
## environment variable to point to the "swig" 's executable which is under the root directory of swig
#https://github.com/snap-stanford/snap-python C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools
# C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\bin\nmake
#Developer Command Prompt for VS2012"
# https://stackoverflow.com/questions/4828388/cygwin-make-bash-command-not-found
# gcc in make python2-devel
# C:\Program Files\swigwin-3.0.12\Doc\Manual\snap\snap-python>nmake -f Makefile
# test swig: swig -version
# SNAP: exe iz C++ lahko naredimo z Visual studiem
# INFOMAP building with cygwin - cannot be run in normal cmd, with mingw + msys can be, but problems building:
# odstranj:
#extra_compile_args=['-DAS_LIB', '-Wno-deprecated-declarations']
#C:\MinGW\infomap-master\interfaces\python  - build faila

# INFOMAP: c:\cygwin64\bin\python2.7.exe  C:\Users\Karmen\Downloads\infomap-master\examples\python\example-simple.py

# https://snap.stanford.edu/snappy/index.html
# https://github.com/mapequation/infomap/blob/master/examples/python/infomap-examples.ipynb
# https://github.com/mapequation/infomap/blob/master/examples/python/example-networkx.pysnap
# https://snap.stanford.edu/snappy/#download
# https://snap.stanford.edu/snappy/release/
# import pip
# pip freeze
#['alabaster==0.7.9', 'babel==2.3.4', 'colorama==0.3.7', 'decorator==4.2.1', 'docutils==0.12', 'imagesize==0.7.1', 'jinja2==2.8', 'markupsafe==0.23', 'networkx==2.1', 'numpy==1.8.0', 'pbr==2.0.0', 'pip==9.0.1', 'psycopg2==2.7.4', 'pygments==2.1.3', 'pyparsing==2.2.0', 'python-dateutil==2.6.0', 'pytz==2016.7', 'requests==2.11.1', 'setuptools==20.10.1', 'six==1.10.0', 'snowballstemmer==1.2.1', 'sphinx==1.5a2', 'sqlalchemy==1.2.2', 'stevedore==1.21.0', 'virtualenv-clone==0.2.6', 'virtualenv==15.1.0', 'virtualenvwrapper==4.7.2', 'xlrd==1.1.0']
# pip install numpy networkx sqlalchemy matplotlib psycopg2 xlrd
# za postgres - psycopg2, decorator skupaj z networkx
"""Graph types in SNAP:
TUNGraph: undirected graph (single edge between an unordered pair of nodes)
TNGraph: directed graph (single directed edge between an ordered pair of nodes)

Network types in SNAP:
TNEANet: directed multigraph with attributes for nodes and edges

Prefix P in the class name stands for a pointer, while T means a type.
"""

# https://github.com/snap-stanford/snap-python/blob/master/examples/tneanet.py
# https://github.com/snap-stanford/snap-python/blob/master/test/test-2015-18a-attr.py


maxWeight = get_max_weight()
multi = maxWeight/1700.0
multi *= 1.1
outputFolder = folder + "/graphs"
links = fetchall_links_with_weight_threshold(1)
destinations_dict = dict()
ids_dict = dict()
for d in get_destinations():
    print d
    if d.destination not in destinations_dict:
        destinations_dict[d.destination] = d
        ids_dict[d.id] = d.destination
print len(destinations_dict)



def change_nodes_position(pos):
    for p in pos:
        d = destinations_dict[p]
        pos[p] = np.array([d.longitude, d.latitude])


# TODO: CESNA
def PrintGStats(s, Graph):
    '''
    Print graph statistics
    '''

    print "graph %s, nodes %d, edges %d, empty %s" % (
        s, Graph.GetNodes(), Graph.GetEdges(),
        "yes" if Graph.Empty() else "no")


def load_snap_graph(save=False, consider_locations=True):

    # add all nodes
    #for d in get_destinations():
    #    G.AddNode(d.id)

    G = nx.Graph()
    if selectedData == DataType.SLO:
        minW_array = [i * multi for i in [0, 10, 20, 40, 60, 100, 120, 150, 180, 200, 270, 300]]
    else:
        minW_array = [i * multi for i in [800]] #100, 120, 150, 200, 400]]
    maxW_array = [i * multi for i in [100, 200, 400, 600, 1000, 1300, 1500]]
    maxW_array.append(maxWeight)
    if not save:
        minW_array = [100]
        maxW_array = [maxWeight+100]
    for minW in minW_array:
        for maxW in maxW_array:
            if minW >= maxW:
                continue
            snap_G = snap.TUNGraph().New() #TUNGraph().New() #TNEANet().New()  # PROBLEM!
            #snap_G.AddIntAttrE('posWeight')
            #PrintGStats("DefaultConstructor:Graph", snap_G)
            plt.clf()
            G.clear()
            # add nodes and edges
            for l in links:
                if minW < l.weight < maxW:
                    nodes_ids = [x.GetId() for x in snap_G.Nodes()]
                    id1 = destinations_dict[l.destination1].id
                    id2 = destinations_dict[l.destination2].id
                    if id1 not in nodes_ids:
                        #destinations_dict[l.destination1] = d
                        snap_G.AddNode(id1)
                    if id2 not in nodes_ids:
                        #destinations_dict[l.destination1] = d
                        snap_G.AddNode(id2)
                    snap_G.AddEdge(id1, id2)#, l.id)
                    G.add_edge(l.destination1, l.destination2, weight=l.weight)
                    #snap_G.AddIntAttrDatE(l.id, l.weight, 'posWeight')

            PrintGStats("DefaultConstructor:Graph", snap_G)
            UGraph = snap_G# snap.ConvertGraph(snap.PUNGraph, G)
            PrintGStats("DefaultConstructor:UGraph", UGraph)

            pos = nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
            nx.draw_networkx_labels(G, pos, font_size=13, font_family='sans-serif', alpha=0.8)
            edgewidth = [d['weight']/float(maxWeight)*10 for (u,v,d) in G.edges(data=True)]
            nx.draw_networkx_edges(G, pos, width=edgewidth, egdelist=G.edges, alpha=0.6)
            CmtyV = snap.TCnComV()
            modularity = snap.Infomap(UGraph, CmtyV)
            c = 0
            dict_groups = {}
            for Cmty in CmtyV:
                print "Community: "
                for NI in Cmty:
                    dest = ids_dict.get(NI)
                    dict_groups[dest] = c
                    print str(NI)+" "+dest
                c += 1
            values = [dict_groups.get(node, 0.25) for node in G.nodes()]
            nx.draw_networkx_nodes(G,pos,
                                   node_color=values,
                                   cmap=plt.cm.Set1,
                                   node_size=350,
                                   alpha=0.9)
            print len(CmtyV)
            print "The modularity of the network is %f" % modularity
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/infomap/graph_infomap_minW="+str(minW)+"_maxW="+str(maxW)+"_modularity_"
                            + str(modularity) + ".png")
    plt.show()  # display

load_snap_graph()


def test():
    # create a graph PNGraph
    # G1 = snap.TNGraph.New()
    G = snap.TNEANet().New()  # .TUndirNet() # not good supported yet?
    G.AddStrAttrN('name')
    G.AddNode(1)
    G.AddStrAttrDatN(0, 'zero', 'name')
    G.AddNode(5)
    G.AddStrAttrDatN(0, 'zero2', 'name')
    G.AddEdge(1,5)
    G.AddFltAttrE('posWeight')
    it = G.BegEI()
    print it
    #print G.GetEI(1,5) #swig/python detected a memory leak of type 'TUndirNet::TEdgeI *', no destructor found.
    for x in G.Edges():
        G.AddFltAttrDatE(x.GetId(), float(x.GetId()*3+1), 'posWeight')
        print str(x.GetId())+ " "+str(G.GetFltAttrDatE(x.GetId(), 'posWeight'))
    #while it.HasNext():
    #    print it.Next()
    S = snap.TIntStrH()
    S.AddDat(0,"David")
    S.AddDat(2,"Emma")
    S.AddDat(3,"Jim")
    S.AddDat(5,"Sam")
    #snap.DrawGViz(G, snap.gvlDot, "gviz.png", "Graph", S)
    #UGraph = snap.GenRndGnm(snap.PUNGraph, 100, 1000)
    UGraph = snap.ConvertGraph(snap.PUNGraph, G)
    CmtyV = snap.TCnComV()
    modularity =  snap.Infomap(UGraph, CmtyV)
    for Cmty in CmtyV:
        print "Community: "
        for NI in Cmty:
            print NI
    print "The modularity of the network is %f" % modularity
    """
    G = snap.TNEANet()
    # convert to undirected graph
    #G7 = snap.ConvertGraph(snap.PUNGraph, G6)
    PrintGStats("DefaultConstructor:Graph", G)
    G.AddNode(1)
    G.AddNode(5)
    G.AddEdge(1,5)
    G.AddFltAttrE('posWeight')  # Add an edge attribute "weight"
    # Fill in the edge attributes
    #for x in G.Edges():
    #    G.AddFltAttrDatE(x.GetId(), float(x.GetId()*3+1), 'posWeight')
    """
    PrintGStats("DefaultConstructor:Graph", G)


#test()

def intro():

    # create a graph PNGraph
    G1 = snap.TNGraph.New()
    G1.AddNode(1)
    G1.AddNode(5)
    G1.AddNode(32)
    G1.AddEdge(1,5)
    G1.AddEdge(5,1)
    G1.AddEdge(5,32)
    print "G1: Nodes %d, Edges %d" % (G1.GetNodes(), G1.GetEdges())

    # create a directed random graph on 100 nodes and 1k edges
    G2 = snap.GenRndGnm(snap.PNGraph, 100, 1000)
    print "G2: Nodes %d, Edges %d" % (G2.GetNodes(), G2.GetEdges())

    # traverse the nodes
    for NI in G2.Nodes():
        print "node id %d with out-degree %d and in-degree %d" % (
            NI.GetId(), NI.GetOutDeg(), NI.GetInDeg())
    # traverse the edges
    for EI in G2.Edges():
        print "edge (%d, %d)" % (EI.GetSrcNId(), EI.GetDstNId())

    # traverse the edges by nodes
    for NI in G2.Nodes():
        for Id in NI.GetOutEdges():
            print "edge (%d %d)" % (NI.GetId(), Id)


    # generate a network using Forest Fire model
    G3 = snap.GenForestFire(1000, 0.35, 0.35)
    print "G3: Nodes %d, Edges %d" % (G3.GetNodes(), G3.GetEdges())

    # save and load binary
    FOut = snap.TFOut("test.graph")
    G3.Save(FOut)
    FOut.Flush()
    FIn = snap.TFIn("test.graph")
    G4 = snap.TNGraph.Load(FIn)
    print "G4: Nodes %d, Edges %d" % (G4.GetNodes(), G4.GetEdges())

    # save and load from a text file
    snap.SaveEdgeList(G4, "test.txt", "Save as tab-separated list of edges")
    G5 = snap.LoadEdgeList(snap.PNGraph, "test.txt", 0, 1)
    print "G5: Nodes %d, Edges %d" % (G5.GetNodes(), G5.GetEdges())

    # generate a network using Forest Fire model
    G6 = snap.GenForestFire(1000, 0.35, 0.35)
    print "G6: Nodes %d, Edges %d" % (G6.GetNodes(), G6.GetEdges())
    # convert to undirected graph
    G7 = snap.ConvertGraph(snap.PUNGraph,G6)
    print "G7: Nodes %d, Edges %d" % (G7.GetNodes(), G7.GetEdges())
    # get largest weakly connected component of G
    WccG = snap.GetMxWcc(G6)
    # get a subgraph induced on nodes {0,1,2,3,4,5}
    SubG = snap.GetSubGraph(G6, snap.TIntV.GetV(0,1,2,3,4))
    # get 3-core of G
    Core3 = snap.GetKCore(G6, 3)
    # delete nodes of out degree 10 and in degree 5
    snap.DelDegKNodes(G6, 10, 5)
    print "G6a: Nodes %d, Edges %d" % (G6.GetNodes(), G6.GetEdges())

    # generate a Preferential Attachment graph on 1000 nodes and node out degree of 3
    G8 = snap.GenPrefAttach(1000, 3)
    print "G8: Nodes %d, Edges %d" % (G8.GetNodes(), G8.GetEdges())
    # vector of pairs of integers (size, count)
    CntV = snap.TIntPrV()
    # get distribution of connected components (component size, count)
    snap.GetWccSzCnt(G8, CntV)
    # get degree distribution pairs (degree, count)
    snap.GetOutDegCnt(G8, CntV)
    # vector of floats
    EigV = snap.TFltV()
    # get first eigenvector of graph adjacency matrix
    snap.GetEigVec(G8, EigV)
    # get diameter of G8
    snap.GetBfsFullDiam(G8, 100)
    # count the number of triads in G8, get the clustering coefficient of G8
    snap.GetTriads(G8)
    snap.GetClustCf(G8)


def intro2():
    UGraph = snap.GenRndGnm(snap.PUNGraph, 100, 1000)
    PrintGStats("DefaultConstructor:Graph", UGraph)
    CmtyV = snap.TCnComV()
    #modularity = snap.CommunityGirvanNewman(UGraph, CmtyV)
    modularity =  snap.Infomap(UGraph, CmtyV)
    for Cmty in CmtyV:
        print "Community: "
        for NI in Cmty:
            print NI
    print "The modularity of the network is %f" % modularity


def test_snap():
    status = False
    try:
        import platform
        print platform.architecture()
        import snap.win.snap
        version = snap.Version
        i = snap.TInt(5)
        if i == 5:
            status = True

    except Exception, ex:
        print ex
        pass

    if status:
        print "SUCCESS, your version of Snap.py is %s" % (version)
    else:
        print "*** ERROR, no working Snap.py was found on your computer"

    test()


# TODO: infomap
# https://github.com/mapequation/infomap
# v cygwinu: make na root-u, potem še v examples/python
# example: https://github.com/mapequation/infomap/blob/master/examples/python/infomap-examples.ipynb
# http://www.mapequation.org/code.html#Link-list-format

# On the main menu, choose File | Project Structure (or click projectStructure, or press Ctrl+Shift+Alt+S
#https://stackoverflow.com/questions/1811691/running-an-outside-program-executable-in-python
import subprocess
subprocess.check_call(([r"c:\cygwin64\bin\python2.7.exe",
                        "c:/Users\Karmen\Downloads\infomap-master\examples\python\example-simple.py"]))
