# create_model.py
# from assert_gpt

import torch
import os.path

from pathlib import Path

from source.shared import Encoder
from source.shared import GPTLanguageModel
from source.shared import save_model

''' Original hyperparameters
    # hyperparameters
    batch_size = 64  # how many independent sequences will we process in parallel?
    block_size = 256  # what is the maximum context length for predictions?
    # max_epochs = 5000
    eval_interval = 500
    learning_rate = 3e-4
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    n_embd = 384
    n_head = 6
    n_layer = 6
    dropout = 0.2
    # ------------
'''

def create_model(model_file_path: Path, corpus_file_path: Path, n_head: int, n_layer: int, settings):
    print(f'settings.block_size = {settings.block_size}')
    if not model_file_path.is_file():
        print(f'Start create model and optimizer')
        print(f'create_model: model_checkpoint_path={os.path.abspath(model_file_path)}')
        if os.path.exists(model_file_path):
            print(f'model already exist at path={os.path.abspath(model_file_path)}')
        else:
            _create_model(model_file_path, corpus_file_path=corpus_file_path, n_head=n_head, n_layer=n_layer, settings=settings)
            print(f'model created at path={os.path.abspath(model_file_path)}')
        print(f'Done')

def _create_model(model_checkpoint_path: Path, corpus_file_path: Path, n_head: int, n_layer: int, settings):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if torch.backends.mps.is_available():
        device = "mps"

    block_size = settings.block_size  # the maximum context length for predictions
    learning_rate = settings.learning_rate
    n_embd = settings.n_embd
    dropout = settings.dropout

    print(f'create_encoder')
    encoder = Encoder.load_from_json(corpus_folder_path=corpus_file_path.parent)
    print(f'vocab_size={len(encoder.tokens)}')

    # create model
    print(f'create model: block_size={block_size} device={device}')
    model = GPTLanguageModel(n_embd, n_head, block_size, dropout, n_layer, device, encoder)
    model = model.to(device)
    # print the number of parameters in the model
    print(sum(p.numel() for p in model.parameters())/1e6, 'M parameters')

    # create a PyTorch optimizer
    print('create a PyTorch optimizer')
    torch.set_default_device("cpu")
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    # save model and optimizer
    save_model(model, optimizer, model_checkpoint_path)
