echo "deleting articles index"
curl -X DELETE  --cacert /tmp/certs/ca/ca.crt -u 'elastic:18_=+cO*7cqJq2YabgLb' https://localhost:9200/articles | jq .

echo "recreating articles index"
curl -X PUT \
  -H "Content-Type: application/json" \
  --cacert /tmp/certs/ca/ca.crt \
  -u 'elastic:18_=+cO*7cqJq2YabgLb' \
  https://localhost:9200/articles \
  -d '{ "mappings": { "properties": { "publication": { "type": "keyword" } } } }' | jq .
