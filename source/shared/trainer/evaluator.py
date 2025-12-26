# evaluator.py

import torch

from statistics import mean

from source.shared.trainer.sample_dataset import SampleDataset
from source.shared.trainer.trainer import get_subset_dataloader

class Evaluator:

    def __init__(self, eval_dataset: SampleDataset, eval_batch_size: int, max_eval_epochs: int):
        self.eval_dataset = eval_dataset
        self.eval_batch_size = eval_batch_size
        self.max_eval_epochs = max_eval_epochs

    @torch.no_grad()
    def estimate_loss(self, model):
        model.eval()
        losses = []
        for _ in range(self.max_eval_epochs):
            data_loader = get_subset_dataloader(dataset=self.eval_dataset, batch_size=self.eval_batch_size)
            for x, y in iter(data_loader):
                logits, loss = model(x, y)
                losses.append(loss.item())
        mean_loss = mean(losses)
        model.train()
        return mean_loss
