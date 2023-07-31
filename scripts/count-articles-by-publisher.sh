curl -H "Content-Type: application/json" \
  --cacert /tmp/certs/ca/ca.crt \
  -u 'elastic:18_=+cO*7cqJq2YabgLb' \
  https://localhost:9200/articles/_search?size=0 \
  -d '{ "aggs": { "articles_by_publisher": { "terms": { "field": "publication" } } } }'
