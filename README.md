# GASTON

GASTON is an interpretable deep learning model for learning a _topographic map_ of a tissue slice from spatially resolved transcriptomics (SRT) data. Specifically, GASTON models gene expression topography by learning the _isodepth_, a 1-D coordinate that smoothly varies across a tissue slice.

<p align="center">
<img src="https://github.com/raphael-group/GASTON/blob/main/imgs/gaston_figure-github.png?raw=true" height=700/>
</p>

The isodepth and topographic map learned by GASTON have many downstream applications including
* identifying **spatial domains**,
* inferring **continuous gradients** and **discontinuous jumps** in gene expression,
* deriving maps of spatial variation in **cell type organization**,
* analyzing continuous gradients in the **tumor microenvironment**

<p align="center">
  <img src="https://github.com/raphael-group/GASTON/blob/main/imgs/gaston_figure-github2.png?raw=true" height=500/>
</p>

## Installation
First install conda environment from `environment.yml` file:

```
cd GASTON
conda env create -f environment.yml
```

Then install GASTON using pip.

```
conda activate gaston-package
pip install -e .
```

We will add GASTON to PyPI and Bioconda soon!

## Getting started

GASTON requires (1) an NxG gene expression matrix (e.g. UMI counts) and (2) an Nx2 spatial location matrix. 

Check out our [readthedocs](https://gaston.readthedocs.io/en/latest/index.html) and Jupyter notebook tutorial `tutorial.ipynb` for the cerebellum analysis. Note that due to Github size constraints, you have to download the counts matrix from [Google Drive](https://drive.google.com/drive/folders/1GiibZwhpzlur8C1hNHa1g7I4jsc1Gmn7?usp=sharing). 

We will add tutorials for the tumor and olfactory bulb analyses soon!

## Software dependencies
* torch
* matplotlib
* pandas
* scikit-learn
* numpy
* jupyterlab
* seaborn
* tqdm
* scipy
* scanpy

See full list in `environment.yml` file.
