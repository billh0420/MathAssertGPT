# neural_network_utility.py
# from shared.neural_network

import os.path
import torch
from torch import Tensor
from torch.nn import functional as F

from .MathGPTLanguageModel import GPTLanguageModel
from source.shared.frame_stack.frame_exceptions import MMError

def generate_predicted_dictum(prompt: str, terminal_token: str, model) -> str:
    assert isinstance(terminal_token, str)
    encoder = model.encoder
    split_prompt = prompt.split()
    max_new_tokens = model.block_size - len(split_prompt)
    encoded_prefix = torch.tensor([encoder.encode(prompt.rstrip())]).to(model.device)
    terminal_token_id = encoder.stoi[terminal_token]
    generated_tokens = generate_tokens(max_new_tokens, encoded_prefix, model=model, terminal_token_id=terminal_token_id)[0].tolist()
    predicted_dictum = encoder.remove_trailing_space_tokens(encoder.decode(generated_tokens))
    return predicted_dictum

def generate_tokens(max_new_tokens, idx: Tensor, model, terminal_token_id: int | None) -> Tensor:
    # idx is (B, T) array of indices in the current context
    assert not model.training
    assert isinstance(terminal_token_id, int or None)
    with torch.no_grad():
        for _ in range(max_new_tokens):
            # crop idx to the last block_size tokens
            idx_cond = idx[:, -model.block_size:].to(model.device)  # at most block_size
            # get the predictions
            logits, loss = model(idx_cond)
            # focus only on the last time step
            logits = logits[:, -1, :]  # becomes (B, C)
            # apply softmax to get probabilities
            probs = F.softmax(logits, dim=-1)  # (B, C)
            # sample from the distribution
            idx_next = torch.multinomial(probs, num_samples=1).to(model.device)  # (B, 1)
            # append sampled index to the running sequence
            idx = torch.cat((idx, idx_next), dim=1).to(model.device)  # (B, T+1)
            if terminal_token_id is not None and idx_next.shape == (1, 1):
                if idx_next.cpu().numpy()[0][0] == terminal_token_id:
                    break
    return idx

def get_n_layer(model: GPTLanguageModel) -> int:
    layer_count = 0
    for module_name, module in model.named_modules():
        if module_name.startswith('blocks'):
            split_module_name = module_name.split('.')
            if len(split_module_name) == 2:
                layer_count += 1
    return layer_count

def load_model(model_checkpoint_path, device, encoder):
    if os.path.exists(model_checkpoint_path):
        if device == 'cpu':
            checkpoint = torch.load(model_checkpoint_path, map_location=torch.device('cpu'))
        else:
            checkpoint = torch.load(model_checkpoint_path)
        # model
        n_embd = checkpoint['n_embd']
        n_head = checkpoint['n_head']
        block_size = checkpoint['block_size']
        dropout = checkpoint['dropout']
        n_layer = checkpoint['n_layer']
        vocab_size = checkpoint['vocab_size']
        if vocab_size != len(encoder.tokens):
            raise Exception(f'vocab_size={vocab_size} is not equal to #encoder.tokens={len(encoder.tokens)}')
        model = GPTLanguageModel(n_embd, n_head, block_size, dropout, n_layer, device, encoder)
        model.epoch = checkpoint['epoch']
        model.step = checkpoint['step']
        model.load_state_dict(checkpoint['model_state_dict'])
        # optimizer
        learning_rate = checkpoint['optimizer_state_dict']['param_groups'][0]['lr']
        optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    else:
        raise MMError(f'Model not found at path={os.path.abspath(model_checkpoint_path)}')
    return model, optimizer

def save_model(model: GPTLanguageModel, optimizer, model_checkpoint_path):
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'n_embd': model.n_embd,
        'n_head': model.n_head,
        'block_size': model.block_size,
        'dropout': model.dropout,
        'n_layer': model.n_layer,
        'device': model.device,
        'vocab_size': model.vocab_size,
        'epoch': model.epoch,
        'step': model.step
    }, model_checkpoint_path)