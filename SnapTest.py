# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os

#import snap.win.snap
from Database import DataType, selectedData

# TESTING snap from:

# https://snap.stanford.edu/snappy/index.html
# https://github.com/mapequation/infomap/blob/master/examples/python/infomap-examples.ipynb
# https://github.com/mapequation/infomap/blob/master/examples/python/example-networkx.pysnap
# https://snap.stanford.edu/snappy/#download
# https://snap.stanford.edu/snappy/release/

"""Graph types in SNAP:
TUNGraph: undirected graph (single edge between an unordered pair of nodes)
TNGraph: directed graph (single directed edge between an ordered pair of nodes)

Network types in SNAP:
TNEANet: directed multigraph with attributes for nodes and edges

Prefix P in the class name stands for a pointer, while T means a type.
"""

# https://github.com/snap-stanford/snap-python/blob/master/examples/tneanet.py
# https://github.com/snap-stanford/snap-python/blob/master/test/test-2015-18a-attr.py

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

# TODO: CESNA?


def PrintGStats(s, Graph):
    '''
    Print graph statistics
    '''

    print "graph %s, nodes %d, edges %d, empty %s" % (
        s, Graph.GetNodes(), Graph.GetEdges(),
        "yes" if Graph.Empty() else "no")


# testing infomap - seems pretty random?
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
            draw_labels(G, pos)
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

# load_snap_graph()


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