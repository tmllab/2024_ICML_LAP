<div align="center">

# Layer-Aware Analysis of Catastrophic Overfitting: Revealing the Pseudo-Robust Shortcut Dependency
[![Paper](https://img.shields.io/badge/paper-ICML-green)]()

</div>

Official implementation of [Layer-Aware Analysis of Catastrophic Overfitting: Revealing the Pseudo-Robust Shortcut Dependency]() (ICML 2024).

## Abstract
Catastrophic overfitting (CO) presents a significant challenge in single-step adversarial training (AT), manifesting as highly distorted deep neural networks (DNNs) that are vulnerable to multi-step adversarial attacks. However, the underlying factors that lead to the distortion of decision boundaries remain unclear. In this work, we delve into the specific changes within different DNN layers and discover that during CO, the former layers are more susceptible, experiencing earlier and greater distortion, while the latter layers show relative insensitivity. Our analysis further reveals that this increased sensitivity in former layers stems from the formation of $\textit{pseudo-robust shortcuts}$, which alone can impeccably defend against single-step adversarial attacks but bypass genuine-robust learning, resulting in distorted decision boundaries. Eliminating these shortcuts can partially restore robustness in DNNs from the CO state, thereby verifying that dependence on them triggers the occurrence of CO. This understanding motivates us to implement adaptive weight perturbations across different layers to hinder the generation of $\textit{pseudo-robust shortcuts}$, consequently mitigating CO. Extensive experiments demonstrate that our proposed method, **L**ayer-**A**ware Adversarial Weight **P**erturbation (LAP), can effectively prevent CO and further enhance robustness.

<p float="left" align="center">
<img src="LAP.png" width="750" /> 
    
**Figure.** Visualization of the loss landscape for individual layers (1st to 5th columns) and for the whole model (6th column). The upper, middle, and lower rows correspond to the stages before, during, and after CO, respectively.

## Requirements
- This codebase is written for `python3` and 'pytorch'.
- To install necessary python packages, run `pip install -r requirements.txt`.


## Experiments
### Data
- Please download and place all datasets into the data directory.


### Training

To train LAP on CIFAR-10
```
# epsilon8
python3 LAP.py --epoch 30 --epsilon 8 --clamp 1 --alpha 1.00 --delta-init zero --beta 0.03 --gamma 0.30 --out-dir CIFAR10_V-LAP_8
python3 LAP.py --epoch 30 --epsilon 8 --clamp 1 --alpha 1.25 --beta 0.002 --gamma 0.30 --out-dir CIFAR10_R-LAP_8
python3 LAP.py --epoch 30 --epsilon 8 --clamp 0 --alpha 1.00 --beta 0.001 --gamma 0.30 --out-dir CIFAR10_N-LAP_8

# epsilon12
python3 LAP.py --epoch 30 --epsilon 12 --clamp 1 --alpha 1.00 --delta-init zero --beta 0.058 --gamma 0.30 --out-dir CIFAR10_V-LAP_12
python3 LAP.py --epoch 30 --epsilon 12 --clamp 1 --alpha 1.25 --beta 0.03 --gamma 0.30 --out-dir CIFAR10_R-LAP_12
python3 LAP.py --epoch 30 --epsilon 12 --clamp 0 --alpha 1.00 --beta 0.002 --gamma 0.30 --out-dir CIFAR10_N-LAP_12

# epsilon16
python3 LAP.py --epoch 30 --epsilon 16 --clamp 1 --alpha 1.00 --delta-init zero --beta 0.07 --gamma 0.30 --out-dir CIFAR10_V-LAP_16
python3 LAP.py --epoch 30 --epsilon 16 --clamp 1 --alpha 1.25 --beta 0.05 --gamma 0.30 --out-dir CIFAR10_R-LAP_16
python3 LAP.py --epoch 30 --epsilon 16 --clamp 0 --alpha 1.00 --beta 0.005 --gamma 0.30 --out-dir CIFAR10_N-LAP_16


# epsilon32
python3 LAP.py --epoch 30 --epsilon 32 --clamp 1 --alpha 1.00 --delta-init zero  --beta 0.48 --gamma 0.30 --out-dir CIFAR10_V-LAP_32
python3 LAP.py --epoch 30 --epsilon 32 --clamp 1 --alpha 1.25 --beta 0.3 --gamma 0.30 --out-dir CIFAR10_R-LAP_32
python3 LAP.py --epoch 30 --epsilon 32 --clamp 0 --alpha 1.00 --beta 0.75 --gamma 0.30 --out-dir CIFAR10_N-LAP_32

```


## License and Contributing
- This README is formatted based on [paperswithcode](https://github.com/paperswithcode/releasing-research-code).
- Feel free to post issues via Github.

## Reference
If you find the code useful in your research, please consider citing our paper:

<pre>
</pre>
