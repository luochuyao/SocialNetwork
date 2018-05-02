# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import snap

from django.shortcuts import render
import networkx as nx
import matplotlib.pyplot as plt
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
# Create your views here.

process = 0

def getPic(filepath):
    G = nx.Graph()
    with open(filepath) as file:
        for line in file:
            head,tail = [str(x) for x in line.split()]
            G.add_edge(head,tail)
    plt.figure()
    nx.draw(G,node_color = 'r',with_labels=False,node_size = 10)
    savepath = 'static/images/network/network.png'
    plt.savefig(savepath)
    return savepath



def process_data(request):
    global process
    G1 = snap.LoadEdgeList(snap.PUNGraph, "data/network", 0, 1)
    most_modulitary=0
    all_edge_num= snap.CntUniqUndirEdges(G1)
    x = [i + 1 for i in range(all_edge_num-1)]
    y = []
    for i in range(all_edge_num-1):
        node1ID, node2ID, maxbetweeness = Max_betweenness(G1)
        deledge(G1, node1ID, node2ID)
        communities = all_components(G1)
        edge_num = snap.CntUniqUndirEdges(G1)
        mod=modularity(G1, communities, edge_num)
        if mod >=most_modulitary:
            most_modulitary=mod
            snap.SaveEdgeList(G1,"test.txt","Save as tab-separated list of edges")
        y.append(mod)
        process = i*100.0/all_edge_num
        print "progess:%f%%"%(process)
    mostG= snap.LoadEdgeList(snap.PUNGraph, "test.txt", 0, 1)
    picPath1 = "static/images/network/most_modularity.png"
    picPath2 = "static/images/network/modularity.png"
    draw_picture(mostG, "static/images/network/most_modularity.png")
    draw_line_chart(x, y,"static/images/network/modularity.png")

    return JsonResponse({'picPath1':picPath1,'picPath2':picPath2})

def show_progress(request):
    global process
    print("show progress")
    return JsonResponse (process, safe=False)

def test(request):

    return render(request,'test.html')






def home(request):

    path = 'None'
    currentPage = 'home'
    isGetFile = False
    isAnalysis = False
    if request.method == "POST":

        file = request.FILES["file"]
        path = 'data/network'
        with open(path, 'wb+')as destination:
            for chunk in file.chunks():
                destination.write(chunk)
            isGetFile = True
        networkPicPath = getPic(path)
        fsize = os.path.getsize(path)/ float(1024)
        filename = str(file)



        if isGetFile:
            currentPage = 'operation'
            G1 = snap.LoadEdgeList(snap.PUNGraph,path,0,1)

            edges = snap.CntUniqUndirEdges(G1)
            nodes = snap.CntNonZNodes(G1)
        else:
            pass
        return render(request,'home.html',{'path':path,'G1':G1,'networkPicPath':networkPicPath,'currentPage':currentPage,'fsize':fsize,'filename':filename,'isGetFile':isGetFile,'isAnalysis':isAnalysis,'edges':edges,'nodes':nodes})

    return render(request,'home.html',{'currentPage':currentPage,'isGetFile':isGetFile,'isAnalysis':isAnalysis})


def result_display(request):

    network_path = request.POST['network_path']
    G1 = snap.LoadEdgeList(snap.PUNGraph, network_path, 0, 1)
    MxWcc, WccV, NId, DegToCntV, Triads,CC,D,ED,lengthOfComponet,MxNodes,MxEdges,modularity,lengthOfCommunity = get_all_static_para(G1)

    return render(request,'result_display.html',{'MxWc': MxWcc, 'WccV': WccV, 'NId': NId, 'DegToCntV': DegToCntV,'Triads': Triads,
            'CC':CC,'D':D,'ED':ED,'lengthOfComponet':lengthOfComponet,"MxNodes":MxNodes,"MxEdges":MxEdges,"modularity":modularity,"lengthOfCommunity":lengthOfCommunity})


def get_all_static_para(G):
    # Get largest WCC
    MxWcc = snap.GetMxWcc(G)
    MxNodes,MxEdges = MxWcc.GetNodes(),MxWcc.GetEdges()


    # Get WCC sizes
    WccV = snap.TIntPrV()
    snap.GetWccSzCnt(G, WccV)
    lengthOfComponet = WccV.Len()


    # Get node with max degree
    NId = snap.GetMxDegNId(G)

    # degree distribution. DegToCntV is a vector of tuple(node count, degree)
    DegToCntV = snap.TIntPrV()
    snap.GetInDegCnt(G, DegToCntV)
    # community detection of snap
    CmtyV=snap.TCnComV()
    modularity=snap.CommunityCNM(G,CmtyV)
    lengthOfCommunity = len(CmtyV)

    # # plot degree distribution
    import matplotlib.pyplot as plt
    node = []
    deg = []
    for item in DegToCntV:
        node.append(item.GetVal2())
        deg.append(item.GetVal1())
        # print "%d nodes with degree %d" % (item.GetVal2(), item.GetVal1())
    plt.figure()
    plt.plot(deg, node, 'g')
    plt.xlabel('Degree')
    plt.ylabel('Count')
    plt.title('The distribution of degree')
    plt.savefig('static/images/network/distributionOfDegree.png')
    # plt.show()


    # triads
    Triads = snap.GetTriads(G)

    # clustering coefficient
    CC = snap.GetClustCf(G)

    # calculate diameter
    D = snap.GetBfsFullDiam(G, 100)

    # calculate effective diameter
    ED = snap.GetBfsEffDiam(G, 100)


    # save information  of G into "fb-info.txt"
    # snap.PrintInfo(G, "fb Stats", "fb-info.txt", False)
    print("************************************************")
    print(MxWcc,WccV,NId,DegToCntV,Triads,MxNodes,MxEdges)
    print("************************************************")
    return MxWcc,WccV,NId,DegToCntV,Triads,CC,D,ED,lengthOfComponet,MxNodes,MxEdges,modularity,lengthOfCommunity
    # return {'MxWc': MxWcc, 'WccV': WccV, 'NId': NId, 'DegToCntV': DegToCntV, 'PRank': PRankH, 'Triad': Triads,
    #         'EigV': EigV, 'Corek': Corek, 'Cmty': CmtyV, 'modularity': modularity}


import snap
import matplotlib.pyplot as plt
import networkx as nx
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
def Max_betweenness(G):
    Nodes = snap.TIntFltH()
    Edges = snap.TIntPrFltH()
    snap.GetBetweennessCentr(G, Nodes, Edges, 1.0)
    maxbetweeness=0
    for edge in Edges:
        #print "edge: (%d, %d) centrality: %f" % (edge.GetVal1(), edge.GetVal2(), Edges[edge])
        if Edges[edge]>=maxbetweeness:
            maxedge=edge
            maxbetweeness=Edges[edge]
    return maxedge.GetVal1(),maxedge.GetVal2(),maxbetweeness
def deledge(G,node1ID,node2ID):
    G.DelEdge(node1ID,node2ID)
def all_components(G):
    communities=[]
    Components = snap.TCnComV()
    snap.GetSccs(G, Components)
    num=0
    #print "Component number:"+str(len(Components))
    for con in Components:
        num+=1
        #print str(num)+":"+str(con.Len())
        onecommunity=[]
        for i in con.NIdV:
            onecommunity.append(i)
        communities.append(onecommunity)
    return communities
def modularity(G,communities,m):
    summary=0
    comm_num=len(communities)
    for num in range(comm_num):
        for i in range(len(communities[num])):
            for j in range(len(communities[num])):
                Node1=G.GetNI(communities[num][i])
                Node2=G.GetNI(communities[num][j])
                if Node1.IsInNId(communities[num][j])==True:
                    aij=1
                else:
                    aij=0
                ki=Node1.GetInDeg()
                kj=Node2.GetInDeg()
                formula=aij-ki*kj*1.0/2/m
                summary+=formula
    modular=summary/2/m*1.0
    return modular
def draw_line_chart(x,y,file):
    plt.figure()
    plt.plot(x, y)
    plt.xlabel("deleted node")
    plt.ylabel("Modularity")
    plt.title("Community detection")
    plt.savefig(file)
    return
    #plt.show()
def draw_picture(G,file):
    Gp=nx.Graph()
    for EI in G.Edges():
        Gp.add_edge(EI.GetSrcNId(), EI.GetDstNId())
        #print "edge (%d, %d)" % (EI.GetSrcNId(), EI.GetDstNId())

    plt.figure()
    nx.draw(Gp,node_color='r',with_labels=False,node_size=10)
    plt.savefig(file)

def community_detection(G1,file1,file2,process):
    #G1 = snap.LoadEdgeList(snap.PUNGraph, "00.edges", 0, 1)
    most_modulitary=0
    all_edge_num= snap.CntUniqUndirEdges(G1)
    x = [i + 1 for i in range(all_edge_num-1)]
    y = []
    for i in range(all_edge_num-1):
        node1ID, node2ID, maxbetweeness = Max_betweenness(G1)
        deledge(G1, node1ID, node2ID)
        communities = all_components(G1)
        edge_num = snap.CntUniqUndirEdges(G1)
        mod=modularity(G1, communities, edge_num)
        if mod >=most_modulitary:
            most_modulitary=mod
            mostG=G1
        y.append(mod)
        process = i*100.0/all_edge_num
        print "progess:%f%%"%(process)
    draw_picture(mostG, file2)
    draw_line_chart(x, y,file1)


