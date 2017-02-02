# coding=utf-8
import snap
import pandas as pd
import geopandas as gp
from constants import index_seg
from constants import ftr_name_d_btw_cntr_SgAsEg, ftr_name_ud_bridge_SgAsEg, ftr_name_ud_btw_cntr_SgAsEg
from collections import defaultdict
import datetime
from utils import costs


def ftr_network_SgAsNd(path_segs, path_ftr_seg_as_node, directionality_column=None):
    from geom_helper import intxn_from_segs
    print 'begin ftr_network_SgAsNd'
    # ################################################### find intxn matrix from segments
    intxn_matrix = intxn_from_segs(path_segs, directionality_column=directionality_column)
    print 'got intxn_matrix'

    # ################################################### build SNAP Network
    edges = intxn_matrix.values
    nodes = pd.unique(edges.flatten())
    nodes_size = len(nodes)
    G = snap.TNGraph.New()
    for n in nodes:
        G.AddNode(int(n))
    for ein, eout in edges:
        G.AddEdge(int(ein), int(eout))
    UG = snap.ConvertGraph(snap.PUNGraph, G)
    print 'node size = {}, directed edges = {}, undirected edges = {}'.format(nodes_size, len([0 for e in G.Edges()]), len([0 for e in UG.Edges()]))

    # ################################################### get network features
    features = defaultdict(lambda: defaultdict(int))
    if directionality_column:
        ftr_directed_SgAsNd(G, features, nodes_size)
    ftr_undirected_SgAsNd(UG, features)

    df_ftr = pd.DataFrame.from_dict(features).T
    df_ftr.index.name = index_seg
    df_ftr.to_csv(path_ftr_seg_as_node)
    return df_ftr


def ftr_network_SgAsEg(path_segs, path_ftr_seg_as_edge, directionality_column=None):

    segs = gp.read_file(path_segs)
    segs.index.name = index_seg

    # ################################################### get nodes
    # get from/to point of each segment
    segs['f'] = segs.geometry.apply(lambda x: x.coords[0])
    segs['t'] = segs.geometry.apply(lambda x: x.coords[-1])
    # index nodes
    node2idx = {n: i for i,n in enumerate(pd.unique(segs[['f','t']].values.flatten()))}
    idx2node = {i: n for n,i in node2idx.items()}
    nodes = idx2node.keys()
    # indexize nodes in segments
    segs['f'] = segs.f.apply(lambda x: node2idx[x])
    segs['t'] = segs.t.apply(lambda x: node2idx[x])

    # ################################################### get edges
    edge2idx = defaultdict(list)

    for sidx, drtn, f, t in segs[[directionality_column, 'f', 't']].reset_index().values:
        if f == t:
            edge2idx[(f,t)].append(sidx)
            continue
        if drtn == 'B' or drtn == 2:
            edge2idx[(f,t)].append(sidx)
            edge2idx[(t,f)].append(sidx)
        elif drtn == 'FT' or drtn == 0:
            edge2idx[(f,t)].append(sidx)
        elif drtn == 'TF' or drtn == 1:
            edge2idx[(t,f)].append(sidx)

    edges = edge2idx.keys()
    print '# nodes = {}, # edges = {}'.format(len(nodes), len(edges))

    # ################################################### get Directed/Undirected Network
    G = snap.TNGraph.New()
    for n in nodes:
        G.AddNode(int(n))
    for ein, eout in edges:
        G.AddEdge(int(ein), int(eout))
    UG = snap.ConvertGraph(snap.PUNGraph, G)
    print 'node size = {}, directed edges = {}, undirected edges = {}'.format(
        len(nodes), len([0 for e in G.Edges()]), len([0 for e in UG.Edges()]))

    # ################################################### get features
    features = defaultdict(lambda: defaultdict(int))
    if directionality_column:
        ftr_directed_SgAsEg(G, features, edge2idx)
    ftr_undirected_SgAsEg(UG,features,edge2idx)

    df_ftr = pd.DataFrame.from_dict(features).T
    df_ftr.index.name = index_seg
    df_ftr.to_csv(path_ftr_seg_as_edge)
    return df_ftr


def ftr_directed_SgAsEg(G, features, edge2idx):
    Nodesbd = snap.TIntFltH()
    Edgesbd = snap.TIntPrFltH()
    snap.GetBetweennessCentr(G, Nodesbd, Edgesbd, 1.0, True)
    for edge in Edgesbd:
        segidxs = edge2idx[(edge.GetVal1(), edge.GetVal2())]
        for sidx in segidxs:
            features[sidx][ftr_name_d_btw_cntr_SgAsEg] += Edgesbd[edge]


def ftr_undirected_SgAsEg(UG, features, edge2idx):
    # in ug, the directed edge is sorted
    def get_segidxs_in_ug(f, t):
        segidxs1 = edge2idx[(f,t)]
        segidxs2 = edge2idx[(t,f)]
        return list(set(segidxs1+segidxs2))

    Nodesbud = snap.TIntFltH()
    Edgesbud = snap.TIntPrFltH()
    snap.GetBetweennessCentr(UG, Nodesbud, Edgesbud, 1.0)
    for edge in Edgesbud:
        segidxs = get_segidxs_in_ug(edge.GetVal1(), edge.GetVal2())
        for sidx in segidxs:
            features[sidx][ftr_name_ud_btw_cntr_SgAsEg] += Edgesbud[edge]

    EdgeV = snap.TIntPrV()
    snap.GetEdgeBridges(UG, EdgeV)
    for edge in EdgeV:
        segidxs = get_segidxs_in_ug(edge.GetVal1(), edge.GetVal2())
        for sidx in segidxs:
            features[sidx][ftr_name_ud_bridge_SgAsEg] += 1


def ftr_directed_SgAsNd(G, features, nodes_size):
    from constants import (ftr_name_d_in_deg_SgAsNd, ftr_name_d_out_deg_SgAsNd, ftr_name_d_auth_score_SgAsNd,
                           ftr_name_d_btw_cntr_SgAsNd, ftr_name_d_clo_cntr_SgAsNd, ftr_name_d_far_cntr_SgAsNd,
                           ftr_name_d_hub_score_SgAsNd,ftr_name_d_node_ecc_SgAsNd, ftr_name_d_page_rank_SgAsNd)
    start_time = datetime.datetime.now()
    print 'begin ftr_directed_SgAsNd', costs(start_time)

    for NI in G.Nodes():
        nid = NI.GetId()
        features[nid][ftr_name_d_in_deg_SgAsNd] = float(NI.GetInDeg())/(nodes_size-1)
        features[nid][ftr_name_d_out_deg_SgAsNd] = float(NI.GetOutDeg())/(nodes_size-1)
        features[nid][ftr_name_d_node_ecc_SgAsNd] = snap.GetNodeEcc(G, nid, True)
        features[nid][ftr_name_d_clo_cntr_SgAsNd] = snap.GetClosenessCentr(G, nid, True, True)
        features[nid][ftr_name_d_far_cntr_SgAsNd] = snap.GetFarnessCentr(G, nid, True, True)
    print 'got features for nodes', costs(start_time)

    Nodes = snap.TIntFltH()
    Edges = snap.TIntPrFltH()
    snap.GetBetweennessCentr(G, Nodes, Edges, 1.0, True)
    for nid in Nodes:
        features[nid][ftr_name_d_btw_cntr_SgAsNd] = Nodes[nid]
    print 'got betweenness', costs(start_time)

    PRankH = snap.TIntFltH()
    snap.GetPageRank(G, PRankH)
    for nid in PRankH:
        features[nid][ftr_name_d_page_rank_SgAsNd] = PRankH[nid]
    print 'got page Rank', costs(start_time)

    NIdHubH = snap.TIntFltH()
    NIdAuthH = snap.TIntFltH()
    snap.GetHits(G, NIdHubH, NIdAuthH)
    for nid in NIdHubH:
        features[nid][ftr_name_d_hub_score_SgAsNd] = NIdHubH[nid]
    for nid in NIdAuthH:
        features[nid][ftr_name_d_auth_score_SgAsNd] = NIdAuthH[nid]
    print 'Got Hit score', costs(start_time)


def ftr_undirected_SgAsNd(UG, features):
    from constants import (ftr_name_ud_art_pt_SgAsNd, ftr_name_ud_auth_score_SgAsNd, ftr_name_ud_bridge_SgAsNd,
                           ftr_name_ud_clo_cntr_SgAsNd, ftr_name_ud_deg_cntr_SgAsNd, ftr_name_ud_eig_cntr_SgAsNd,
                           ftr_name_ud_far_cntr_SgAsNd, ftr_name_ud_hub_score_SgAsNd,ftr_name_ud_node_ecc_SgAsNd,
                           ftr_name_ud_btw_cntr_SgAsNd, ftr_name_ud_page_rank_SgAsNd)
    start_time = datetime.datetime.now()
    print 'begin ftr_undirected_SgAsNd', costs(start_time)

    for NI in UG.Nodes():
        nid = NI.GetId()
        features[nid][ftr_name_ud_deg_cntr_SgAsNd] = snap.GetDegreeCentr(UG, nid)
        features[nid][ftr_name_ud_node_ecc_SgAsNd] = snap.GetNodeEcc(UG, nid, False)
        features[nid][ftr_name_ud_clo_cntr_SgAsNd] = snap.GetClosenessCentr(UG, nid, True, False)
        features[nid][ftr_name_ud_far_cntr_SgAsNd] = snap.GetFarnessCentr(UG, nid, True, False)
    print 'got features for nodes', costs(start_time)

    NIdEigenH = snap.TIntFltH()
    snap.GetEigenVectorCentr(UG, NIdEigenH)
    for nid in NIdEigenH:
        features[nid][ftr_name_ud_eig_cntr_SgAsNd] = NIdEigenH[nid]
    print 'got eigen centrality', costs(start_time)

    Nodes = snap.TIntFltH()
    Edges = snap.TIntPrFltH()
    snap.GetBetweennessCentr(UG, Nodes, Edges, 1.0, False)
    for nid in Nodes:
        features[nid][ftr_name_ud_btw_cntr_SgAsNd] = Nodes[nid]
    print 'got btw centrality', costs(start_time)

    PRankH = snap.TIntFltH()
    snap.GetPageRank(UG, PRankH)
    for nid in PRankH:
        features[nid][ftr_name_ud_page_rank_SgAsNd] = PRankH[nid]
    print 'got page rank', costs(start_time)

    NIdHubH = snap.TIntFltH()
    NIdAuthH = snap.TIntFltH()
    snap.GetHits(UG, NIdHubH, NIdAuthH)
    for nid in NIdHubH:
        features[nid][ftr_name_ud_hub_score_SgAsNd] = NIdHubH[nid]
    for nid in NIdAuthH:
        features[nid][ftr_name_ud_auth_score_SgAsNd] = NIdAuthH[nid]
    print 'got hit score', costs(start_time)

    ArtNIdV = snap.TIntV()
    snap.GetArtPoints(UG, ArtNIdV)
    for nid in ArtNIdV:
        features[nid][ftr_name_ud_art_pt_SgAsNd]=1
    print 'got articulate point', costs(start_time)

    EdgeV = snap.TIntPrV()
    snap.GetEdgeBridges(UG, EdgeV)
    for edge in EdgeV:
        features[edge.GetVal1()][ftr_name_ud_bridge_SgAsNd]+=1
        features[edge.GetVal2()][ftr_name_ud_bridge_SgAsNd]+=1
    print 'got bridge', costs(start_time)


# ############################## Deprecated

# def ftr_for_dc(path_intxn, path_segs, path_ftr_seg_as_node):
#     the intersection file of open dc isn't that useful
#     from constants import index_seg
#     gpdf_segs = gp.read_file(path_segs)
#     df_intxn = pd.read_csv(path_intxn)
#     edges = df_intxn[['STREET1SEGID','STREET2SEGID']].values
#     nodes = pd.unique(edges.flatten())
#     features = ftr_segs_as_nodes(nodes, edges, True)
#     df_ftr = pd.DataFrame.from_dict(features).T
#     df_ftr.index.name = 'STREETSEGID'
#     df = gpdf_segs[['STREETSEGID']].reset_index().merge(df_ftr.reset_index())
#     df.columns = [index_seg] + list(df.columns[1:])
#     df.to_csv(path_ftr_seg_as_node)
#     return df
#
