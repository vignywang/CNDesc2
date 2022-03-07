# CNDesc (under review)
This repository is for reviewers to understand the implementation details.

To do：
- [x] Evaluation code for CNDesc
- [x] Trained model 
- [ ] Training code (After the paper is accepted.)


# Requirement
```
pip install -r requirement.txt
```

# Quick start
HPatches Image Matching Benchmark

1.Download the trained model: https://drive.google.com/file/d/16mVPNgYgmAgJ-DlmA7zC8lRffH4l0l5x/view?usp=sharing
and place it in the "ckpt/cndesc".


2.Download the HPatches dataset：

```
cd evaluation_hpatch/hpatches_sequences
bash download.sh
```
3.Extract local descriptors：
```
cd evaluation_hpatch
CUDA_VISIBLE_DEVICES=0 python export.py  --tag [Descriptor_suffix_name]  --output_root [output_dir] --config ../configs/CNDesc_extract.yaml
```
4.Evaluation
```
cd evaluation_benchmark
python hpatch_benchmark.py --config ../configs/hpatches_benchmark.yaml
```
The evaluation results will be displayed as:
```
MMA at 3,6,9 thr:
cndesc [0.7397221459282769]
cndesc [0.8354972556785301]
cndesc [0.8578464366771557]
Precision at 3,6,9 thr:
cndesc [0.7586607756438078]
cndesc [0.8576736450195312]
cndesc [0.880967034233941]
HA at 3,6,9 thr:
cndesc [0.7648148006863065]
cndesc [0.8981480068630643]
cndesc [0.9407406559696904]

```
