set -ex

export SGLANG_USE_AITER=1

# These env vars should adjust according to your environment
export GLOO_SOCKET_IFNAME=enp193s0f1np1
export SGLANG_HOST_IP=10.2.224.32
#export MC_GID_INDEX=2
export NCCL_IB_HCA=ionic_0,ionic_1,ionic_2,ionic_3,ionic_4,ionic_5,ionic_6,ionic_7
export NCCL_IB_TC=104
export NCCL_IB_FIFO_TC=184
export NCCL_IB_GID_INDEX=1
export NCCL_CROSS_NIC=0

# model: https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507-FP8
python -m sglang.launch_server \
  --model-path Qwen/Qwen3-235B-A22B-Instruct-2507-FP8 \
  --tp-size 4 \
  --disaggregation-mode decode \
  --disaggregation-ib-device ionic_0,ionic_1,ionic_2,ionic_3,ionic_4,ionic_5,ionic_6,ionic_7 \
  --prefill-round-robin-balance \
  --load-balance-method round_robin \
  --host $SGLANG_HOST_IP --port 30003 \
  --disaggregation-transfer-backend mooncake \
  --mem-fraction-static 0.5 \
  --disable-radix-cache \
  --trust-remote-code \
  2>&1 | tee log_decode.log
