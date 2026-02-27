curl http://127.0.0.1:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "prompt": "继续完成这个句子：人工智能的未来",
    "max_tokens": 100,
    "temperature": 0.7
  }'
echo ""
