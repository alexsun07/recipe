set -ex

export GLOO_SOCKET_IFNAME=enp193s0f1np1
export MASTER_NODE_IP=10.2.224.7
export RANK=0

cd mori
torchrun --nnodes=2 --node_rank=$RANK \
    --cmd bench --max-token 4096 \
    --nproc_per_node=1 \
    --master_addr=$MASTER_NODE_IP \
    --master_port=1234  \
    examples/ops/dispatch_combine/test_dispatch_combine_internode.py \
    --kernel-type v1
