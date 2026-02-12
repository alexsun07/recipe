import os
import subprocess
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

cases = [
    # input tokens, output tokens, concurrency, step
    (900, 400, 240, 16),
    (1800, 400, 108, 2),
    (3300, 400, 48, 2),
    (18000, 400, 4, 1),
    (900, 1800, 240, 16),
    (150, 3800, 240, 16),
]
results = {}
beg = time.time()
for case in cases:
    input_tokens, output_tokens, concurrency, step = case
    prev_state = 'unknown'
    while True:
        num_prompts = concurrency * 5
        cmd = f'python3 -m sglang.bench_serving --backend sglang --base-url http://127.0.0.1:8000 --dataset-name random --random-range-ratio 1.0 --random-input {input_tokens} --random-output {output_tokens} --num-prompts {num_prompts} --max-concurrency={concurrency}'
        print(f"Running command: {cmd}")
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        txt = output.stdout
        #print(txt)
        if output.returncode != 0:
            print(f"Command failed with error: {output.stderr}")
            continue
        req_speed = txt.split('Request throughput (req/s):')[1].split('\n')[0].strip()
        input_speed = txt.split('Input token throughput (tok/s):')[1].split('\n')[0].strip()
        out_speed = txt.split('Output token throughput (tok/s):')[1].split('\n')[0].strip()
        total_inout_speed = txt.split('Total token throughput (tok/s):')[1].split('\n')[0].strip()
        ttft = txt.split('Mean TTFT (ms):')[1].split('\n')[0].strip()
        tpot = txt.split('Mean TPOT (ms):')[1].split('\n')[0].strip()
        print(f'Input: {input_tokens}, Output: {output_tokens}, Concurrency: {concurrency}, TTFT: {ttft} ms, TPOT: {tpot} ms, Request throughput: {req_speed}, Input throughput: {input_speed}, Output throughput: {out_speed}, Total throughput: {total_inout_speed} tok/s')
        if float(ttft) > 3000 or float(tpot) > 50:
            if prev_state == 'valid':
                # previously met sla, now failed, use previous concurrency as result and break
                concurrency, ttft, tpot, req_speed, input_speed, out_speed, total_inout_speed = results[(input_tokens, output_tokens)]
                print(bcolors.OKGREEN + f"Concurrency: {concurrency}, TTFT: {ttft} ms, TPOT: {tpot} ms, Request throughput: {req_speed}, Input throughput: {input_speed}, Output throughput: {out_speed}, Total throughput: {total_inout_speed} tok/s" + bcolors.ENDC)
                break
            prev_state = 'invalid'
            if concurrency > step:
                concurrency -= step
                continue
            break

        results[(input_tokens, output_tokens)] = (concurrency, ttft, tpot, req_speed, input_speed, out_speed, total_inout_speed)
        if prev_state == 'invalid':
            # prevously did not meet sla, now met, no need try
            print(bcolors.OKGREEN + f"Concurrency: {concurrency}, TTFT: {ttft} ms, TPOT: {tpot} ms, Request throughput: {req_speed}, Input throughput: {input_speed}, Output throughput: {out_speed}, Total throughput: {total_inout_speed} tok/s" + bcolors.ENDC)
            break

        prev_state = 'valid'
        concurrency += step

end = time.time()
print(f"Total time taken: {end - beg:.1f} seconds")
print("\nSummary of results:")
print(f'Input tokens, Output tokens, Concurrency, TTFT (ms), TPOT (ms), Request throughput (req/s), Input token throughput (tok/s), Output token throughput (tok/s), Total token throughput (tok/s)')
for key, value in results.items():
    input_tokens, output_tokens = key
    concurrency, ttft, tpot, req_speed, input_speed, out_speed, total_inout_speed = value
    print(f'{input_tokens}, {output_tokens}, {concurrency}, {ttft}, {tpot}, {req_speed}, {input_speed}, {out_speed}, {total_inout_speed}')