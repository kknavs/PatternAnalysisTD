# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

import snap.win.snap
from Database import fetchall_links_with_weight_threshold, get_destinations, get_destinations_id_asc, get_max_weight, \
    folder, DataType, selectedData
from FilterGraph import filter_add_link

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
#if selectedData == DataType.VIENNA:
#    multi = (maxWeight)/1700
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


# TODO: infomap
# https://github.com/mapequation/infomap
# v cygwinu: make na root-u, potem še v examples/python
# example: https://github.com/mapequation/infomap/blob/master/examples/python/infomap-examples.ipynb
# http://www.mapequation.org/code.html#Link-list-format

# On the main menu, choose File | Project Structure (or click projectStructure, or press Ctrl+Shift+Alt+S
#https://stackoverflow.com/questions/1811691/running-an-outside-program-executable-in-python
import subprocess
#subprocess.check_call(([r"c:\cygwin64\bin\python2.7.exe",
#                        "c:/Users\Karmen\Downloads\infomap-master\examples\python\example-simple.py"]))
# C:\Users\Karmen\Downloads\infomap-master\Infomap.exe


def load_infomap_graph(filters=None, save=False, consider_locations=True):

    # add all nodes
    #for d in get_destinations():
    #    G.AddNode(d.id)
    G = nx.Graph()
    if selectedData == DataType.SLO:
        minW_array = [150]#40, 300[i * multi for i in [1, 10, 20, 40, 60, 100, 120, 150, 180, 200, 270, 300]]
    else:
        minW_array = [50, 100, 120, 150, 200, 400, 800]
    maxW_array = [] #[i * multi for i in [400]]#[i * multi for i in [100, 300, 500, 700, 1000]]
    #if selectedData == DataType.VIENNA:
    #    maxW_array +=[ 1300, 1500]
    maxW_array.append(maxWeight+1)
    filters = {"subject_type": ["hotels"]} #, "user_travel_style":["Like a Local"]}
    if not save:
        minW_array = [10 * multi]
        #maxW_array = [maxWeight+100]
        maxW_array = [1300]
    for minW in minW_array:
        for maxW in maxW_array:
            if minW >= maxW:
                continue
            plt.clf()
            G.clear()
            txt_name = "/infomap/infomap_minW="+str(float(minW)/maxWeight)+"_maxW="+str(float(maxW)/maxWeight)+".net"
            with open(outputFolder+txt_name, 'w') as f:
                # add nodes and edges to txt and graph
                # A network in Pajek format
                """*Vertices 27
                1 "1"
                2 "2"
                3 "3"
                4 "4"
                ...
                *Edges 33
                1 2 1
                1 3 1
                1 4 1
                2 3 1
                ..."""
                for l in links:
                    if minW < l.weight < maxW:
                        nw = filter_add_link(l, filters)
                        #G.add_edge(l.destination1, l.destination2, weight=float(l.weight)/maxWeight)
                        if nw > 0:
                            G.add_edge(l.destination1, l.destination2, weight=float(nw)/maxW)
                if len(G.nodes()) == 0:
                    continue
                newline = str("\n")  # linux
                f.write(str("*Vertices ") + str(len(G.nodes()))+newline)
                c =1
                temp_v = {}
                for d in get_destinations_id_asc():
                    # G.add_node(d.destination)  # if all nodes added we have problems because of looping?
                    if d.destination in G.nodes(): # and not d.destination =='Ljubljana':
                        f.write(str(c)+str(' "'+d.destination+'"'+newline))
                        temp_v[d.destination] = c
                        c += 1  # must follow a consequitive order.
                        # f.write(str(d.id)+str(' "'+d.destination+'"'+newline))
                        #  Labels are quoted directly after the nodes identifier.
                f.write(str("*Edges ") + str(len(G.edges()))+newline)
                for l in G.edges():
                    #if minW < l.weight < maxW:
                        #if l.destination1 !='Ljubljana' and l.destination2 !='Ljubljana':
                    if True:
                            id1 = temp_v[l[0]]
                            id2 = temp_v[l[1]]
                            """
                            A link list is a minimal format to describe a network by only specifying a set of links:

                            # A network in link list format
                            1 2 1
                            1 3 1
                            2 3 2
                            3 5 0.5
                            ...
                            Each line corresponds to the triad source target weight which
                            """
                            e_weight =G[l[0]][l[1]]['weight']
                            f.write(str(str(id1)+' '+str(id2)+' '+str(e_weight)+newline))
                            #f.write(str(str(id1)+' '+str(id2)+' '+str(float(1)))+newline)
                            #f.write(str(str(id1)+' '+str(id2)+' '+str(1)+'\r\n'))
                            # we write edges in Link list format
            #./Infomap ninetriangles.net output/ -N 10 --tree --bftree
            import os
            out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolder+"/infomap" #+txt_name.replace(".txt", "_out.txt")
            # tt =outputFolder+'/ninetriangless.net'
            subprocess.check_call([r"c:/Users\Karmen\Downloads\infomap-master\Infomap.exe",
                                   outputFolder+txt_name,
                                   # outputFolder+'/ninetriangless.net',
                                 out_path, "-N 10",  "--overlapping", "--tree"])
            # --preferred-number-of-modules 4
            # --overlapping
            dict_groups = {}
            """Tree format
            The resulting hierarchy will be written to a file with the extension .tree (plain text file) and corresponds
             to the best hierarchical partition (shortest description length) of the attempts.
             The output format has the pattern:

            # Codelength = 3.48419 bits.
            1:1:1 0.0384615 "7" 6
            1:1:2 0.0384615 "8" 7
            1:1:3 0.0384615 "9" 8
            1:2:1 0.0384615 "4" 3
            1:2:2 0.0384615 "5" 4
            ...
            Each row (except the first one, which summarizes the result) begins with the
            multilevel module assignments of a node. The module assignments are colon separated from coarse to fine
            level, and all modules within each level are sorted by the total flow (PageRank) of the nodes they contain.
            Further, the integer after the last colon is the rank within the finest-level module, the decimal number is
            the amount of flow in that node, i.e. the steady state population of random walkers, the content within
            quotation marks is the node name, and finally, the last integer is the index of the node in
            the original network file."""
            with open(outputFolder+txt_name.replace('.net','.tree'), 'rU') as f: # Universal newline mode
                for line in f:
                    if line[0] != '#':
                        print line.strip()
                        l = line.strip().split('"')
                        print l
                        modules, flow_amount = l[0].strip().split(" ")
                        node_name = l[1]
                        # modules, flow_amount, node_name, ind = line.strip().split(" ")
                        #  too many values to unpack - presledki v imenih
                        #node_name = l[2][1:-1]
                        dict_groups[node_name] = float(modules.split(":")[0])

            for n in G.nodes():
                print n, dict_groups.get(n)

            pos = nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
            nx.draw_networkx_labels(G, pos, font_size=13, font_family='sans-serif', alpha=0.8)
            edgewidth = [d['weight']*10 for (u,v,d) in G.edges(data=True)]
            nx.draw_networkx_edges(G, pos, width=edgewidth, egdelist=G.edges, alpha=0.6)
            values = [dict_groups.get(node, 0.25) for node in G.nodes()]
            nx.draw_networkx_nodes(G,pos,
                                   node_color=values,
                                   cmap=plt.cm.Set1,
                                   node_size=350,
                                   alpha=0.9)
            #print "The modularity of the network is %f" % modularity
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder +
                         txt_name.replace(".net", " ".join("{}_{}".format(k, v) for k, v in filters.items())+".png"))

            txt_name = "/infomap/infomap_minW="+str(float(minW)/maxWeight)+"_maxW="+str(float(maxW)/maxWeight)+".net"
            out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolder+"/N10/infomap" #+txt_name.replace(".txt", "_out.txt")
            # tt =outputFolder+'/ninetriangless.net'
            modules = len(G.nodes())/2
            if modules > 10:
                modules = 10
            subprocess.check_call([r"c:/Users\Karmen\Downloads\infomap-master\Infomap.exe",
                               outputFolder+txt_name,
                               # outputFolder+'/ninetriangless.net',
                               out_path, "-N 10", "--preferred-number-of-modules "+unicode(modules), "--overlapping",  "--tree"])
            with open(outputFolder+"/N10"+txt_name.replace('.net','.tree'), 'rU') as f:  # Universal newline mode
                for line in f:
                    if line[0] != '#':
                        print line.strip()
                        l = line.strip().split('"')
                        print l
                        modules, flow_amount = l[0].strip().split(" ")
                        node_name = l[1]
                        # modules, flow_amount, node_name, ind = line.strip().split(" ")
                        #  too many values to unpack - presledki v imenih
                        #node_name = l[2][1:-1]
                        dict_groups[node_name] = float(modules.split(":")[0])
            for n in G.nodes():
                print n, dict_groups.get(n)
            pos = nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
            plt.clf()
            nx.draw_networkx_labels(G, pos, font_size=13, font_family='sans-serif', alpha=0.8)
            edgewidth = [d['weight']*10 for (u,v,d) in G.edges(data=True)]
            nx.draw_networkx_edges(G, pos, width=edgewidth, egdelist=G.edges, alpha=0.6)
            values = [dict_groups.get(node, 0.25) for node in G.nodes()]
            nx.draw_networkx_nodes(G,pos,
                                   node_color=values,
                                   cmap=plt.cm.Set1,
                                   node_size=350,
                                   alpha=0.9)
            #print "The modularity of the network is %f" % modularity
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder +"/N10"+
                            txt_name.replace(".net", " ".join("{}_{}".format(k, v) for k, v in filters.items())+".png"))
        # --preferred-number-of-modules 4
        # --overlapping
        dict_groups = {}
    plt.show()  # display

load_infomap_graph(save=True)

import community_louvain as Community
def draw_greedy(num, size, greedy=True):  # num_cliques, clique_size)
    G = nx.Graph()
    """for n1,n2 in [(0, 1), (1, 2), (2, 3), (0, 3),
                  (1, 4),
                  (4, 5), (5, 6), (6, 7), (4, 7),
                  (2, 8), (7, 8), (8, 9), (2, 9), (7, 9), (8, 9)]:
        G.add_edge(n1,n2)"""
    for n1,n2 in [(0, 1), (1, 2), (2, 3), (0, 3),
                  (1, 4),
                  (4, 5), (5, 6), (6, 7), (4, 7),
                  (2, 8), (7, 8), (8, 9), (2, 9), (7, 9), (8, 9)]:
        G.add_edge(n1,n2)
    #G = nx.ring_of_cliques(num, size)
    #G = nx.balanced_tree(2, 3)

    #nx.draw(G)
    pos = nx.spring_layout(G)
    nx.draw_networkx_edges(G, pos, G.edges())

    dict_groups = {}

    if greedy:
        dict_groups = Community.best_partition(G, None)
        #nx.draw(G,pos, node_size=700)
        print dict_groups
    else:
        txt_name = "/infomap_test.net"
        with open(outputFolder+txt_name, 'w') as f:
            # add nodes and edges to txt and graph
            # A network in Pajek format
            print G.edges()
            newline = str("\n")  # linux
            f.write(str("*Vertices ") + str(len(G.nodes()))+newline)
            c =1
            temp_v = {}
            for n in G.nodes():
                f.write(str(n)+str(' "'+str(n)+'"'+newline))
                temp_v[n] = c
                c += 1  # must follow a consequitive order.
            f.write(str("*Edges ") + str(len(G.edges()))+newline)
            for g in G.edges():
                f.write(str(str(g[0])+' '+str(g[1]))+newline)
        import os
        out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolder
        subprocess.check_call([r"c:/Users\Karmen\Downloads\infomap-master\Infomap.exe",
                               outputFolder+txt_name,
                               out_path, "-N 10", "--tree", "-z --zero-based-numbering"])
        # --preferred-number-of-modules 4
        # --overlapping
        with open(outputFolder+txt_name.replace('.net','.tree'), 'rU') as f: # Universal newline mode
            for line in f:
                if line[0] != '#':
                    print line.strip()
                    l = line.strip().split('"')
                    print l
                    modules, flow_amount = l[0].strip().split(" ")
                    node_name = int(l[1])
                    dict_groups[node_name] = float(modules.split(":")[0])

        for n in G.nodes():
            print n, dict_groups.get(n)

    values = [dict_groups.get(node, 0.25) for node in G.nodes()]
    nx.draw_networkx_nodes(G,pos,
                               node_color=values,
                               cmap=plt.cm.Set1,
                               node_size=350,
                               alpha=1.0)


    from networkx.algorithms import community as community_nx
    #groups = [partition.get(node, 0.25) for node in G.nodes()]
    #modulariry = community_nx.modularity(G, [])
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed')
    plt.axis('off')
    plt.show()

    #print "The modularity of the network is %f" % modularity


def draw_test_di_graph(greedy=False):
    """G = nx.DiGraph(directed=True)
    G.add_edges_from(
        [('A', 'B'), ('C', 'B'), ('C', 'D'), ('A', 'D'), ('A', 'E'),
         ('F', 'E'), ('F', 'G'), ('H', 'G'), ('H', 'E')])

    val_map ={} #{'A': 1.0,'B': 1.0,'': 1.0,'C': 1.0,'D': 1.0    }

    values = [val_map.get(node, 0.25) for node in G.nodes()]

    nx.draw(G, cmap = plt.get_cmap('jet'), node_color = values)
    plt.show()"""
    G = nx.DiGraph()
    G.add_edges_from(
        [('0', '1'), ('2', '1'), ('2', '3'), ('0', '3'), ('0', '4'),
         ('5', '4'), ('5', '6'), ('7', '6'), ('7', '4')])
    #G = nx.ring_of_cliques(num, size)
    #G = nx.balanced_tree(2, 3)

    #nx.draw(G)
    pos = nx.spring_layout(G)
    nx.draw_networkx_edges(G, pos, G.edges())

    dict_groups = {}

    if greedy:
        dict_groups = Community.best_partition(G, None)
        #nx.draw(G,pos, node_size=700)
        print dict_groups
    else:
        txt_name = "/infomap_test.net"
        with open(outputFolder+txt_name, 'w') as f:
            # add nodes and edges to txt and graph
            # A network in Pajek format
            print G.edges()
            newline = str("\n")  # linux
            f.write(str("*Vertices ") + str(len(G.nodes()))+newline)
            c =1
            temp_v = {}
            for n in sorted(G.nodes()):
                f.write(str(n)+str(' "'+str(n)+'"'+newline))
                temp_v[n] = c
                c += 1  # must follow a consequitive order.
            f.write(str("*Edges ") + str(len(G.edges()))+newline)
            for g in G.edges():
                f.write(str(str(g[0])+' '+str(g[1]))+newline)
        import os
        out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolder
        subprocess.check_call([r"c:/Users\Karmen\Downloads\infomap-master\Infomap.exe",
                               outputFolder+txt_name,
                               out_path,"-d --directed", "-N 10", "--tree", "-z --zero-based-numbering"])
        # --preferred-number-of-modules 4
        # --overlapping
        with open(outputFolder+txt_name.replace('.net','.tree'), 'rU') as f: # Universal newline mode
            for line in f:
                if line[0] != '#':
                    print line.strip()
                    l = line.strip().split('"')
                    print l
                    modules, flow_amount = l[0].strip().split(" ")
                    node_name = int(l[1])
                    dict_groups[node_name] = float(modules.split(":")[0])

        for n in G.nodes():
            print n, dict_groups.get(n)

    values = [dict_groups.get(node, 0.25) for node in G.nodes()]
    nx.draw_networkx_nodes(G,pos,
                           node_color=values,
                           cmap=plt.cm.Set1,
                           node_size=350,
                           alpha=1.0)
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed')
    plt.axis('off')
    plt.show()


# draw_greedy(5, 4, True)
# draw_test_di_graph()
