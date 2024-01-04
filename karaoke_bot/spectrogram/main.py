import cv2 as cv2
import torchvision
from skimage import io, transform
import matplotlib.pyplot as plt
from typing import Tuple, List, Type, Dict, Any
import torchvision.models as models
import torch.nn.functional as F

# import imgaug as ia
# import accimage

import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
from threading import Thread
from queue import Empty, Queue
from libs.plot_examples import plot_examples, plot_examples_segmentation
from seg_losses import *


resize = 1024
tb_period = 8

tb_writer = SummaryWriter(log_dir=tb_basepath)
device1 = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device2 = torch.device('cpu')


def start_train(model):  # запускаем обучение всех слоев
    for param in model.parameters():
        param.requires_grad = True


def calculate_loss(
        model_result: torch.tensor,
        data_target: torch.tensor,
        loss_function: torch.nn.Module = torch.nn.MSELoss()
):
    lossXY = (loss_function(model_result[:, :2], data_target[:, :2])) ** (0.5)  # тут из батчей получаю, править
    return lossXY.item()


model = UnetCoordConv(activation=Mish)
for param in model.parameters():
    param.requires_grad = True
model = nn.DataParallel(model)
model = model.to(device1)


class ThreadKiller:
    """Boolean object for signaling a worker thread to terminate"""

    def __init__(self):
        self.to_kill = False

    def __call__(self):
        return self.to_kill

    def set_tokill(self, tokill):
        self.to_kill = tokill


def threaded_batches_feeder(tokill, batches_queue, dataset_generator):
    while True:
        for img, mask, landmarks in dataset_generator:
            batches_queue.put((img, mask, landmarks), block=True)
            if tokill() == True:
                return


def threaded_cuda_batches(tokill, cuda_batches_queue, batches_queue):
    while True:
        (img, mask, landmarks) = batches_queue.get(block=True)
        img = torch.from_numpy(img)

        # torch normalize

        landmarks = torch.from_numpy(landmarks)
        img = Variable(img.float()).to(device1)
        landmarks = Variable(landmarks.float()).to(device1)
        cuda_batches_queue.put((img, landmarks), block=True)

        if tokill() == True:
            return


def train_single_epoch(
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        loss_function: torch.nn.Module,
        cuda_batches_queue: Queue,
        Per_Step_Epoch: int,
        current_epoch: int
):
    model.train()
    loss_values = []
    loss_tb = []
    pbar = tqdm(total=Per_Step_Epoch)
    for batch_idx in range(int(Per_Step_Epoch)):  # тут продумать
        data_image, target = cuda_batches_queue.get(block=True)

        ###### DEBUG plots
        if batch_idx == 0:
            plot_examples_segmentation(data_image, target, file_output = os.path.join(logs_basepath, 'train_input_ep%04d.png' % current_epoch))
        ###### DEBUG plots

        target = Variable(target)

        # target = target.to(device1)
        optimizer.zero_grad()  # обнулили\перезапустии градиенты для обратного распространения
        data_out = model(data_image)  # применили модель к данным
        loss = loss_function(data_out, target)  # применили фуннкцию потерь
        loss_values.append(loss.item())

        loss_tb.append(loss.item())
        tb_writer.add_scalar('train_loss', np.mean(loss_tb), current_epoch*Per_Step_Epoch + batch_idx)
        loss_tb=[]

        loss.backward()  # пошли по графу нейросетки обратно
        optimizer.step()  # выполняем наш градиентный спуск по вычисленным шагам в предыдущей строчке
        pbar.update(1)
        pbar.set_postfix({'loss': loss.item()})
    pbar.close()
    #MK не забывай закрывать pbar

    return np.mean(loss_values)


def validate_single_epoch(model: torch.nn.Module,
                          loss_function: torch.nn.Module,
                          cuda_batches_queue: Queue,
                          Per_Step_Epoch: int,
                          current_epoch: int):
    model.eval()

    loss_values = []

    pbar = tqdm(total=Per_Step_Epoch)
    for batch_idx in range(int(Per_Step_Epoch)):  # тут продумать
        data_image, target = cuda_batches_queue.get(block=True)
        data_out = model(data_image)

        if batch_idx == 0:
            plot_examples_segmentation(data_image, data_out, file_output = os.path.join(logs_basepath, 'val_results_ep%04d.png' % current_epoch))

        loss = loss_function(data_out, target)
        loss_values.append(loss.item())
        pbar.update(1)
        pbar.set_postfix({'loss': loss.item()})
    pbar.close()
    # MK не забывай закрывать pbar

    return np.mean(loss_values)


def train_model(model: torch.nn.Module, train_dataset, val_dataset, max_epochs=480):

    loss_function = BinaryFocalLoss(alpha=1, gamma=4)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    lr_scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=32, T_mult=2, eta_min=1e-8, lr_decay = 0.8)

    #region data preprocessing threads starting
    batches_queue_length = 4
    preprocess_workers = 4

    train_batches_queue = Queue(maxsize=batches_queue_length)
    train_cuda_batches_queue = Queue(maxsize=4)
    train_thread_killer = ThreadKiller()
    train_thread_killer.set_tokill(False)

    for _ in range(preprocess_workers):
        thr = Thread(target=threaded_batches_feeder, args=(train_thread_killer, train_batches_queue, train_dataset))
        thr.start()

    train_cuda_transfers_thread_killer = ThreadKiller()
    train_cuda_transfers_thread_killer.set_tokill(False)
    train_cudathread = Thread(target=threaded_cuda_batches, args=(train_cuda_transfers_thread_killer, train_cuda_batches_queue, train_batches_queue))
    train_cudathread.start()

    test_batches_queue = Queue(maxsize=batches_queue_length)
    test_cuda_batches_queue = Queue(maxsize=4)
    test_thread_killer = ThreadKiller()
    test_thread_killer.set_tokill(False)

    for _ in range(preprocess_workers):
        thr = Thread(target=threaded_batches_feeder, args=(test_thread_killer, test_batches_queue, sun_dataset_test))
        thr.start()

    test_cuda_transfers_thread_killer = ThreadKiller()
    test_cuda_transfers_thread_killer.set_tokill(False)
    test_cudathread = Thread(target=threaded_cuda_batches,
                             args=(test_cuda_transfers_thread_killer, test_cuda_batches_queue,
                                   test_batches_queue))
    test_cudathread.start()
    #endregion

    Steps_Per_Epoch_Train = 64
    Steps_Per_Epoch_Test = len(val_dataset) // batch_size + 1

    for epoch in range(max_epochs):

        print(f'Epoch {epoch} / {max_epochs}')
        train_loss = train_single_epoch(model, optimizer, loss_function, train_cuda_batches_queue, Steps_Per_Epoch_Train, current_epoch=epoch)

        tb_writer.add_scalar('train_loss', train_loss, epoch)

        val_loss = validate_single_epoch(model, loss_function, test_cuda_batches_queue, Steps_Per_Epoch_Test, current_epoch=epoch)
        tb_writer.add_scalar('val_loss', val_loss, epoch)

        print(f'Validation loss: {val_loss}')

        lr_scheduler.step()

        torch.save(model.module.state_dict(), os.path.join(checkpoints_basepath, 'model_ep%04d.pt' % epoch))

    #region stopping datapreprocessing threads
    test_thread_killer.set_tokill(True)  # убиваю потокои, так же убить валидационные
    train_thread_killer.set_tokill(True)  # убиваю потокои, так же убить валидационные
    test_cuda_transfers_thread_killer.set_tokill(True)
    train_cuda_transfers_thread_killer.set_tokill(True)
    for _ in range(preprocess_workers):
        try:
            # Enforcing thread shutdown
            test_batches_queue.get(block=True, timeout=1)
            test_cuda_batches_queue.get(block=True, timeout=1)
            train_batches_queue.get(block=True, timeout=1)
            train_cuda_batches_queue.get(block=True, timeout=1)
        except Empty:
            pass
    #endregion


train_model(model, train_dataset=sun_dataset_train, val_dataset=sun_dataset_test, max_epochs=480)
