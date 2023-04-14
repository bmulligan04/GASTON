# ISSUE: these functions use cell_type_labels rather than cell_type_df
# ie assumes each spot has a single gene, rather than potential doublets

from scipy.stats import mode
import numpy as np
import matplotlib.pyplot as plt

# assuming single cell type per spot
def bin_data(counts_mat, belayer_labels, belayer_depth, cell_type_labels, 
             num_bins=70, pseudocount=1, umi_threshold=500):
    
    idx_kept=np.where(np.sum(counts_mat,1) > umi_threshold)[0]
    pseudo_counts_mat=counts_mat+1
    exposure=np.sum(pseudo_counts_mat,axis=0)
    cmat=pseudo_counts_mat[idx_kept,:]
    
    unique_cell_types=np.unique(cell_type_labels)
    
    G,N=cmat.shape

    # BINNING (NEW)
    depth_min, depth_max=np.floor(np.min(belayer_depth))-0.5, np.ceil(np.max(belayer_depth))+0.5
    bins=np.linspace(depth_min, depth_max, num=num_bins+1)

    unique_binned_depths=np.array( [0.5*(bins[i]+bins[i+1]) for i in range(len(bins)-1)] )
    binned_depth_inds=np.digitize(belayer_depth, bins)-1 #ie [1,0,3,15,...]
    binned_depths=unique_binned_depths[binned_depth_inds]
    
    # remove bins not used
    unique_binned_depths=np.delete(unique_binned_depths,
                                   [np.where(unique_binned_depths==t)[0][0] for t in unique_binned_depths if t not in binned_depths])

    N_1d=len(unique_binned_depths)
    binned_count=np.zeros( (G, N_1d) )
    binned_exposure=np.zeros( N_1d )
    binned_labels=np.zeros(N_1d)
    # binned_cell_type_list=np.zeros((N_1d, len(unique_cell_types)))
    binned_cell_type_list=[-1 for i in range(N_1d)]
    
    binned_count_per_ct={ct: np.zeros( (G, N_1d) ) for ct in cell_type_labels}
    binned_exposure_per_ct={ct: np.zeros( N_1d ) for ct in cell_type_labels}

    map_1d_bins_to_2d={} # map b -> [list of cells in bin b]
    for ind, b in enumerate(unique_binned_depths):
        bin_pts=np.where(binned_depths==b)[0]

        binned_count[:,ind]=np.sum(cmat[:,bin_pts],axis=1)
        binned_exposure[ind]=np.sum(exposure[bin_pts])
        binned_labels[ind]= mode(belayer_labels[bin_pts],keepdims=False).mode
        binned_cell_type_list[ind]=cell_type_labels[bin_pts]
        map_1d_bins_to_2d[b]=bin_pts
        
        for ct in np.unique(cell_type_labels):
            ct_cells=np.where(cell_type_labels==ct)[0]
            ct_cells_bin = [t for t in ct_cells if t in bin_pts]
            
            binned_count_per_ct[ct][:,ind]=np.sum(cmat[:,ct_cells_bin],axis=1)
            binned_exposure_per_ct[ct][ind]=np.sum(exposure[ct_cells_bin])
        

    L=len(np.unique(belayer_labels))
    segs=[np.where(binned_labels==i)[0] for i in range(L)]

    to_return={}
    to_return['binned_depths']=binned_depths
    to_return['unique_binned_depths']=unique_binned_depths
    to_return['binned_count']=binned_count
    to_return['binned_exposure']=binned_exposure
    to_return['binned_labels']=binned_labels
    to_return['binned_cell_types']=binned_cell_type_list
    
    to_return['binned_count_per_ct']=binned_count_per_ct
    to_return['binned_exposure_per_ct']=binned_exposure_per_ct
    
    to_return['map_1d_bins_to_2d']=map_1d_bins_to_2d
    to_return['segs']=segs

    return to_return

def plot_gene_pwlinear(gene, pw_fit_dict, gene_labels, belayer_labels, belayer_depth, binning_output, 
                       cell_type=None, spot_threshold=0.25, pt_size=10, colors=None, linear_fit=True,
                       layer_list=None, ticksize=20, figsize=(7,3)):
    
    if cell_type is None:
        unique_binned_depths=binning_output['unique_binned_depths']
        binned_labels=binning_output['binned_labels']

        binned_count=binning_output['binned_count']
        binned_exposure=binning_output['binned_exposure']
        
        slope_mat, intercept_mat, _, _ = pw_fit_dict['all_cell_types']

        segs=binning_output['segs']
        L=len(segs)

        fig,ax=plt.subplots(figsize=figsize)

        if layer_list is None:
            layer_list=range(L)

        for seg in layer_list:
            pts_seg=np.where(binned_labels==seg)[0]
            if colors is not None:
                plt.scatter(unique_binned_depths[pts_seg],
                           np.log( (binned_count[gene,pts_seg]) / binned_exposure[pts_seg] ), c=colors[seg])
            else:
                plt.scatter(unique_binned_depths[pts_seg],
                           np.log( (binned_count[gene,pts_seg]) / binned_exposure[pts_seg] ))

            if linear_fit:
                slope=slope_mat[gene,seg]
                intercept=intercept_mat[gene,seg]
                # print(slope,intercept)

                plt.plot( unique_binned_depths[pts_seg], intercept + slope*unique_binned_depths[pts_seg], color='grey', alpha=1 )
        plt.xticks(fontsize=ticksize)
        plt.yticks(fontsize=ticksize)
    else:
        unique_binned_depths=binning_output['unique_binned_depths']
        binned_labels=binning_output['binned_labels']

        binned_count=binning_output['binned_count_per_ct'][cell_type]
        binned_exposure=binning_output['binned_exposure_per_ct'][cell_type]
        # binned_cell_type_mat=binning_output['binned_cell_type_mat']
        binned_cell_type_list=binning_output['binned_cell_types']

        # ct_ind=np.where(unique_cell_types==cell_type)[0][0]
        
        slope_mat, intercept_mat, _, _ = pw_fit_dict[cell_type]

        segs=binning_output['segs']
        L=len(segs)
        if layer_list is None:
            layer_list=range(L)

        fig,ax=plt.subplots(figsize=figsize)

        for seg in layer_list:
            pts_seg=np.where(binned_labels==seg)[0]
            pts_seg=[p for p in pts_seg if len(np.where(binned_cell_type_list[p]==cell_type)[0])/len(binned_cell_type_list[p]) > spot_threshold]
            
            
            # pts_seg=[p for p in pts_seg if binned_cell_type_mat[p,ct_ind] / binned_cell_type_mat[p,:].sum() > spot_threshold]

            if colors is not None:
                # plt.scatter(unique_binned_depths[pts_seg],
                #            np.log( (binned_count[gene,pts_seg]) / binned_exposure[pts_seg] ), c=colors[seg], s=pt_size)

                plt.scatter(unique_binned_depths[pts_seg],
                           np.log( (binned_count[gene,pts_seg]) / binned_exposure[pts_seg] ), c=colors[seg], s=pt_size)

            else:
                plt.scatter(unique_binned_depths[pts_seg],
                           np.log( (binned_count[gene,pts_seg]) / binned_exposure[pts_seg] ))

        if linear_fit:
            slope=slope_mat[gene,seg]
            intercept=intercept_mat[gene,seg]
            # print(slope,intercept)

            plt.plot( unique_binned_depths[pts_seg], intercept + slope*unique_binned_depths[pts_seg], color='grey', alpha=1 )
        plt.xticks(fontsize=ticksize)
        plt.yticks(fontsize=ticksize)
                       
