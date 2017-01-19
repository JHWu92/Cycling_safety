# coding=utf-8
import snap
import pandas as pd
import geopandas as gp
from constants import index_seg
from constants import ftr_name_d_btw_cntr_SgAsEd, ftr_name_ud_bridge_SgAsEd, ftr_name_ud_btw_cntr_SgAsEd
from collections import defaultdict


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
        if drtn=='B' or drtn==2:
            edge2idx[(f,t)].append(sidx)
            edge2idx[(t,f)].append(sidx)
        elif drtn=='FT' or drtn==0:
            edge2idx[(f,t)].append(sidx)
        elif drtn=='TF' or drtn==1:
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
    ftr_undirected_SgAsEd(UG,features,edge2idx)

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
            features[sidx][ftr_name_d_btw_cntr_SgAsEd] += Edgesbd[edge]


def ftr_undirected_SgAsEd(UG, features, edge2idx):
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
            features[sidx][ftr_name_ud_btw_cntr_SgAsEd] += Edgesbud[edge]

    EdgeV = snap.TIntPrV()
    snap.GetEdgeBridges(UG, EdgeV)
    for edge in EdgeV:
        segidxs = get_segidxs_in_ug(edge.GetVal1(), edge.GetVal2())
        for sidx in segidxs:
            features[sidx][ftr_name_ud_bridge_SgAsEd] += 1


def ftr_network_SgAsNd(path_segs, path_ftr_seg_as_node, directionality_column=None, is_dird=False):
    from geom_helper import intxn_from_segs
    print '----segments as nodes network----'
    intxn_matrix = intxn_from_segs(path_segs, directionality_column=directionality_column)
    print 'got intxn_matrix'
    edges = intxn_matrix.values
    nodes = pd.unique(edges.flatten())
    features_SgAsNd = ftr_segs_as_nodes(nodes, edges, is_dird)
    print 'got ftr sgasnd'
    df_ftr = pd.DataFrame.from_dict(features_SgAsNd).T
    df_ftr.index.name = index_seg
    df_ftr.to_csv(path_ftr_seg_as_node)


def ftr_segs_as_nodes(nodes, edges, is_dird=False):
    # TODO: modify the feature name and function name, add SgAsNd
    # TODO: reconsider the function name, because processs of building network of SgAsNd and SgAsEg is quite different

    from collections import defaultdict
    nodes_size = len(nodes)
    G = snap.TNGraph.New()
    for n in nodes:
        G.AddNode(int(n))
    for ein, eout in edges:
        G.AddEdge(int(ein), int(eout))
    UG = snap.ConvertGraph(snap.PUNGraph, G)
    print 'node size = {}, directed edges = {}, undirected edges = {}'.format(nodes_size, len([0 for e in G.Edges()]), len([0 for e in UG.Edges()]))
    features = defaultdict(lambda: defaultdict(int))
    if is_dird:
        ftr_directed(G, features, nodes_size)
        print 'got ftr directed'
    ftr_undirected(UG, features)
    print 'got ftr undirected'
    return features


def ftr_directed(G, features, nodes_size):

    for NI in G.Nodes():
        nid = NI.GetId()
        features[nid]['d_in_deg'] = float(NI.GetInDeg())/(nodes_size-1)
        features[nid]['d_out_deg'] = float(NI.GetOutDeg())/(nodes_size-1)
        features[nid]['d_node_ecc'] = snap.GetNodeEcc(G, nid, True)
        features[nid]['d_clo_cntr'] = snap.GetClosenessCentr(G, nid, True, True)
        features[nid]['d_far_cntr'] = snap.GetFarnessCentr(G, nid, True, True)
    print 'a'
    Nodes = snap.TIntFltH()
    Edges = snap.TIntPrFltH()
    snap.GetBetweennessCentr(G, Nodes, Edges, 1.0, True)
    for nid in Nodes:
        features[nid]['d_btw_cntr'] = Nodes[nid]
    print 'between'
    PRankH = snap.TIntFltH()
    snap.GetPageRank(G, PRankH)
    for nid in PRankH:
        features[nid]['d_page_rank'] = PRankH[nid]
    print 'page'
    NIdHubH = snap.TIntFltH()
    NIdAuthH = snap.TIntFltH()
    snap.GetHits(G, NIdHubH, NIdAuthH)
    for nid in NIdHubH:
        features[nid]['d_hub_score'] = NIdHubH[nid]
    for nid in NIdAuthH:
        features[nid]['d_auth_score'] = NIdAuthH[nid]
    print 'his'

def ftr_undirected(UG, features):
    for NI in UG.Nodes():
        nid = NI.GetId()
        features[nid]['ud_deg_cntr'] = snap.GetDegreeCentr(UG, nid)
        features[nid]['ud_node_ecc'] = snap.GetNodeEcc(UG, nid, False)
        features[nid]['ud_clo_cntr'] = snap.GetClosenessCentr(UG, nid, True, False)
        features[nid]['ud_far_cntr'] = snap.GetFarnessCentr(UG, nid, True, False)
    print 'nodes'
    NIdEigenH = snap.TIntFltH()
    snap.GetEigenVectorCentr(UG, NIdEigenH)
    for nid in NIdEigenH:
        features[nid]['ud_eig_cntr'] = NIdEigenH[nid]
    print 'eigen'
    Nodes = snap.TIntFltH()
    Edges = snap.TIntPrFltH()
    snap.GetBetweennessCentr(UG, Nodes, Edges, 1.0, False)
    for nid in Nodes:
        features[nid]['ud_btw_cntr'] = Nodes[nid]
    print 'btw'
    PRankH = snap.TIntFltH()
    snap.GetPageRank(UG, PRankH)
    for nid in PRankH:
        features[nid]['ud_page_rank'] = PRankH[nid]
    print 'page ud'
    NIdHubH = snap.TIntFltH()
    NIdAuthH = snap.TIntFltH()
    snap.GetHits(UG, NIdHubH, NIdAuthH)
    for nid in NIdHubH:
        features[nid]['ud_hub_score'] = NIdHubH[nid]
    for nid in NIdAuthH:
        features[nid]['ud_auth_score'] = NIdAuthH[nid]
    print 'hit ud'
    ArtNIdV = snap.TIntV()
    snap.GetArtPoints(UG, ArtNIdV)
    for nid in ArtNIdV:
        features[nid]['ud_art_pt']=1
    print 'artpoint'
    EdgeV = snap.TIntPrV()
    snap.GetEdgeBridges(UG, EdgeV)
    for edge in EdgeV:
        features[edge.GetVal1()]['ud_bridge']+=1
        features[edge.GetVal2()]['ud_bridge']+=1


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
