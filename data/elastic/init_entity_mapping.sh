#!/bin/bash
ES='http://127.0.0.1:9200'
ESIDX='entity_search'
ESTYPE='school'
curl -XPUT $ES/$ESIDX/$ESTYPE/_mapping -d '{
    "school" : {
        "_all" : {"enabled" : false},
        "properties" : {
            "short_name" : {"type" : "text", "analyzer":"my_ngram_analyzer","index" : "analyzed", "similarity" : "BM25"}
        }
    }
}'
