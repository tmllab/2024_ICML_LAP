"""
This code is partially based on the repository of https://github.com/locuslab/fast_adversarial (Wong et al., ICLR'20)
This code is partially based on the repository of https://github.com/csdongxian/AWP (Wu et al., NeurIPS' 2020)
"""

import argparse
import logging
import math
import os
import time
import numpy as np
import torch
import torch.nn as nn
from preact_resnet import PreActResNet18
from wideresnet import WideResNet
from utils import *

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='PreActResNet18')
    parser.add_argument('--data-dir', default='../../cifar-data', type=str)
    parser.add_argument('--out-dir', default='LAP_output', type=str)

    parser.add_argument('--epochs', default=30, type=int)
    parser.add_argument('--batch-size', default=128, type=int)
    parser.add_argument('--lr-schedule', default='cyclic', choices=['cyclic', 'multistep'])
    parser.add_argument('--lr-min', default=0.0, type=float)
    parser.add_argument('--lr-max', default=0.2, type=float)
    parser.add_argument('--weight-decay', default=5e-4, type=float)
    parser.add_argument('--momentum', default=0.9, type=float)

    parser.add_argument('--epsilon', default=8, type=int)
    parser.add_argument('--alpha', default=1.0, type=float)
    parser.add_argument('--delta-init', default='random', choices=['zero', 'random'])
    parser.add_argument('--clamp', default=0, type=int)
    parser.add_argument('--beta', default=0.01, type=float)
    parser.add_argument('--gamma', default=1.0, type=float)
    parser.add_argument('--layer-number', default=21, type=int)
    parser.add_argument('--seed', default=0, type=int)
    return parser.parse_args()

def main():
    args = get_args()
    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format='[%(asctime)s] - %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.DEBUG,
        handlers = [
            logging.FileHandler(os.path.join(args.out_dir, 'output.log')),
            logging.StreamHandler()]
    )
    logger.info(args)

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)

    train_loader, test_loader = get_loaders(args.data_dir, args.batch_size)

    epsilon = (args.epsilon / 255.) / std
    alpha = ((args.epsilon * args.alpha) / 255.) / std

    if args.model == 'PreActResNet18':
        model = PreActResNet18(num_classes=100).cuda()
        proxy = PreActResNet18(num_classes=100).cuda()
    elif args.model == 'WideResNet':
        model = WideResNet(34, 100, 10, dropRate=0.0).cuda()
        proxy = WideResNet(34, 100, 10, dropRate=0.0).cuda()
    else:
        raise ValueError("Unknown model")

    opt = torch.optim.SGD(model.parameters(), lr=args.lr_max, momentum=args.momentum, weight_decay=args.weight_decay)
    proxy_opt = torch.optim.SGD(model.parameters(), lr=args.lr_max, momentum=args.momentum, weight_decay=args.weight_decay)

    lr_steps = args.epochs * len(train_loader)
    if args.lr_schedule == 'cyclic':
        scheduler = torch.optim.lr_scheduler.CyclicLR(opt, base_lr=args.lr_min, max_lr=args.lr_max, step_size_up=lr_steps / 2, step_size_down=lr_steps / 2)
    elif args.lr_schedule == 'multistep':
        scheduler = torch.optim.lr_scheduler.MultiStepLR(opt, milestones=[(lr_steps * 0.5), (lr_steps * 0.75)], gamma=0.1)

    # Training
    start_train_time = time.time()
    logger.info('Epoch \t Seconds  \t LR \t \t Train Loss \t Train Acc')
    for epoch in range(args.epochs):
        start_epoch_time = time.time()
        train_loss = 0
        train_acc = 0
        train_n = 0

        for i, (X, y) in enumerate(train_loader):
            model.train()
            proxy.train()
            X, y = X.cuda(), y.cuda()
            if args.delta_init == 'zero':
                delta = torch.zeros(args.batch_size, 3, 32, 32).cuda()
            elif args.delta_init == 'random':
                delta_ran = torch.zeros(args.batch_size, 3, 32, 32).cuda()
                if args.clamp:
                    for j in range(len(epsilon)):
                        delta_ran[:, j, :, :].uniform_(-epsilon[j][0][0].item(), epsilon[j][0][0].item())
                else:
                    for j in range(len(epsilon)):
                        delta_ran[:, j, :, :].uniform_(2 * -epsilon[j][0][0].item(), 2 * epsilon[j][0][0].item())
                delta = delta_ran

            delta.data = clamp(delta[:X.size(0)], lower_limit - X, upper_limit - X)
            delta.requires_grad = True
            output = model(X + delta)
            loss = nn.CrossEntropyLoss(reduce=True)(output, y)

            proxy.load_state_dict(model.state_dict())
            proxy_opt.load_state_dict(opt.state_dict())

            opt.zero_grad()
            loss.backward()
            opt.step()

            grad = delta.grad.detach()
            delta.data = delta + alpha * torch.sign(grad)
            if args.clamp:
                delta.data = clamp(delta, -epsilon, epsilon)
            delta.data = clamp(delta[:X.size(0)], lower_limit - X, upper_limit - X)
            delta = delta.detach()

            diff_weights = diff_in_weights(proxy, model)
            model.load_state_dict(proxy.state_dict())
            opt.load_state_dict(proxy_opt.state_dict())

            model.train()
            add_into_weights(model, diff_weights, args.gamma, args.beta, args.layer_number)
            output = model(clamp(X + delta[:X.size(0)], lower_limit, upper_limit))
            loss = nn.CrossEntropyLoss(reduce=False)(output, y)
            loss = loss.mean()

            opt.zero_grad()
            loss.backward()
            opt.step()

            train_loss += loss.item() * y.size(0)
            train_acc += (output.max(1)[1] == y).sum().item()
            train_n += y.size(0)
            scheduler.step()
        epoch_time = time.time()
        lr = scheduler.get_lr()[0]
        logger.info('%d \t %.1f \t \t %.4f \t %.4f \t %.4f',
                    epoch, (epoch_time - start_epoch_time), lr, (train_loss / train_n), (train_acc / train_n))
    train_time = time.time()
    torch.save(model.state_dict(), os.path.join(args.out_dir, f'model_{args.seed}.pth'))
    logger.info('Total train time: %.4f minutes', (train_time - start_train_time) / 60)

    # Evaluation
    if args.model == 'PreActResNet18':
        model_test = PreActResNet18(num_classes=100).cuda()
    elif args.model == 'WideResNet':
        model_test = WideResNet(34, 100, 10, dropRate=0.0).cuda()
    else:
        raise ValueError("Unknown model")

    model_test.load_state_dict(torch.load(os.path.join(args.out_dir, f'model_{args.seed}.pth')))
    model_test.float()
    model_test.eval()

    test_loss, test_acc = evaluate_standard(test_loader, model_test)
    fgsm_loss, fgsm_acc = evaluate_fgsm(test_loader, model_test, epsilon)
    pgd_loss, pgd_acc = evaluate_pgd(test_loader, model_test, 50, 1, epsilon)

    logger.info('Test Loss \t Test Acc \t FGSM Loss \t FGSM Acc \t PGD Loss \t PGD Acc')
    logger.info('%.4f \t \t %.4f \t %.4f \t %.4f \t %.4f \t %.4f', test_loss, test_acc, fgsm_loss, fgsm_acc, pgd_loss, pgd_acc)

if __name__ == "__main__":
    main()
