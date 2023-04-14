import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils
import torch.distributions
import numpy as np

device = 'cuda' if torch.cuda.is_available() else 'cpu'

##################################################################################
# Neural network class
# Inputs: 
#   G: number of genes/features
#   S_hidden_list: list of hidden layer sizes for f_S 
#                  (e.g. [50] means f_S has one hidden layer of size 50)
#   A_hidden_list: list of hidden layer sizes for f_A 
#                  (e.g. [10,10] means f_A has two hidden layers, both of size 10)
#   activation_fn: activation function
##################################################################################

class SpatialNN(nn.Module):
    """
    Neural network class. Has two attributes: 
    (1) spatial embedding f_S : R^2 -> R, and 
    (2) expression function f_A : R -> R^G. 
    Each of these is parametrized by a neural network.
    
    Parameters
    ----------
    G
        number of genes/features
    S_hidden_list
        list of hidden layer sizes for f_S 
        (e.g. [50] means f_S has one hidden layer of size 50)
    A_hidden_list
        list of hidden layer sizes for f_A 
        (e.g. [10,10] means f_A has two hidden layers, both of size 10)
    activation_fn
        activation function for neural network
    """
    
    def __init__(
        self, 
        G, 
        S_hidden_list, 
        A_hidden_list,
        activation_fn=nn.ReLU(),
    ):
        super(SpatialNN, self).__init__()
        
        # create spatial embedding f_S
        S_layer_list=[2] + S_hidden_list + [1]
        S_layers=[]
        for l in range(len(S_layer_list)-1):
            S_layers.append(nn.Linear(S_layer_list[l], S_layer_list[l+1]))

            if l != len(S_layer_list)-2:
                S_layers.append(activation_fn)
                
        self.spatial_embedding=nn.Sequential(*S_layers)
        
        # create expression function f_A
        A_layer_list=[1] + A_hidden_list + [G]
        A_layers=[]
        for l in range(len(A_layer_list)-1):
            A_layers.append(nn.Linear(A_layer_list[l], A_layer_list[l+1]))

            if l != len(A_layer_list)-2:
                A_layers.append(activation_fn)
            
        self.expression_function=nn.Sequential(*A_layers)

    def forward(self, x):
        z = self.spatial_embedding(x) # relative depth
        return self.expression_function(z)

##################################################################################
# Train NN
# Inputs: 
#   spatial_nn_model: SpatialNN object
#   S: torch Tensor (N x 2) containing spot locations
#   A: torch Tensor (N x G) containing features
#   epochs: number of epochs to train
#   batch_size: batch size



#   A_hidden_list: list of hidden layer sizes for f_A 
#                  (e.g. [10,10] means f_A has two hidden layers, both of size 10)
#   activation_fn: activation function
##################################################################################
    
def train(S, A, 
          spatial_nn_model=None, S_hidden_list=None, A_hidden_list=None, activation_fn=nn.ReLU(),
          epochs=1000, batch_size=None, 
          checkpoint=100, SAVE_PATH=None, loss_reduction='mean',
          optim='sgd', lr=1e-3, weight_decay=0, momentum=0, seed=0):
    """
    Train a SpatialNN from scratch
    
    Parameters
    ----------
    spatial_nn_model
        SpatialNN object
    S
        torch Tensor (N x 2) containing spot locations
    A
        torch Tensor (N x G) containing features
    epochs
        number of epochs to train
    batch_size
        batch size of neural network
    checkpoint
        save the current NN when the epoch is a multiple of checkpoint
    SAVE_PATH
        folder to save NN at checkpoints
    loss_reduction
        either 'mean' or 'sum' for MSELoss
    optim
        optimizer to use (currently supports either 'sgd' or 'adam')
    lr
        learning rate for the optimizer
    weight_decay
        weight decay parameter for optimizer
    momentum
        momentum parameter, if using SGD optimizer
    """
    torch.manual_seed(seed)
    N,G=A.shape
    
    if spatial_nn_model == None:
        spatial_nn_model=SpatialNN(A.shape[1], S_hidden_list, A_hidden_list, activation_fn=activation_fn)
    
    if optim=='sgd':
        opt = torch.optim.SGD(spatial_nn_model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
    elif optim=='adam':
        opt = torch.optim.Adam(spatial_nn_model.parameters(), lr=lr, weight_decay=weight_decay)
    
    loss_list=np.zeros(epochs)

    loss_function=torch.nn.MSELoss(reduction=loss_reduction)
    
    for epoch in range(epochs):
        if epoch%checkpoint==0:
            print(f'epoch: {epoch}')
            if SAVE_PATH is not None:
                torch.save(spatial_nn_model, SAVE_PATH + f'model_epoch_{epoch}.pt')
        
        if batch_size is not None:
            # take non-overlapping random samples of size batch_size
            permutation = torch.randperm(N)
            for i in range(0, N, batch_size):
                opt.zero_grad()
                indices = permutation[i:i+batch_size]

                S_ind=S[indices,:]
                S_ind.requires_grad_()

                A_ind=A[indices,:]

                loss = loss_function(spatial_nn_model(S_ind), A_ind)
                loss_list[epoch] += loss.item()

                loss.backward()
                opt.step()
        else:
            opt.zero_grad()
            S.requires_grad_()

            loss = loss_function(spatial_nn_model(S), A)
            loss_list[epoch] += loss.item()

            loss.backward()
            opt.step()
            
    return spatial_nn_model, loss_list
    
