#!/bin/bash
ES='http://127.0.0.1:9200'
ESIDX=$1
ESTYPE=$2
curl -XDELETE $ES/$ESIDX
curl -XPUT $ES/$ESIDX/ -d '{
    "settings" : {
        "index":{
            "analysis":{
                "analyzer":{
                    "my_ngram_analyzer" : {
                        "tokenizer" : "my_ngram_tokenizer"
                    }
                },
                "tokenizer" : {
                    "my_ngram_tokenizer" : {
                        "type" : "nGram",
                        "min_gram" : "1",
                        "max_gram" : "3",
                        "token_chars": [ "letter", "digit" ]
                    }
                }
            }
        },
        "similarity" : {
          "my_similarity" : {
            "type" : "BM25",
            "k1" : "2",
            "b" : "0.8"
            }
          }
    }
}'

curl -XPUT $ES/$ESIDX/$ESTYPE/_mapping -d '{'\"$2\"' : {
        "_all" : {"enabled" : false},
        "properties" : {
            "name" : {"type" : "text", "analyzer":"my_ngram_analyzer","index" : "analyzed", "similarity" : "BM25"}
        }
    }
}'
