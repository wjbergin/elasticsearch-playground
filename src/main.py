import csv
from itertools import islice
from elasticsearch import Elasticsearch
from elasticsearch import helpers

airport_data = '/var/app/data/airports.dat'

es = Elasticsearch(
    ['http://elasticsearch:9200'],
)

settings_and_mapping = {
  "settings" : {
    "index" : {"number_of_shards" : 1},
    "analysis": {
      "normalizer": {
        "lowercase_normalizer": {
          "type": "custom",
          "filter": ["lowercase"]
        }
      }
    }
  },
  "mappings": {
    "_doc": {
      "properties": {
        "name": {
            "type": "text",
            "fields": {
                "normalize": {
                    "normalizer": "lowercase_normalizer",
                    "type": "keyword"
                    },
                "keyword": {
                    "type": "keyword"
                    }
            }
        },
        "city": {
            "type": "text",
            "fields": {
                "normalize": {
                    "normalizer": "lowercase_normalizer",
                    "type": "keyword"
                    },
                "keyword": {
                    "type": "keyword"
                    }
            }
        },
        "country":
          { "type": "text"  },
        "iata":
          { "type": "text"  },
        "icao":
          { "type": "text"  },
        "location": {
            "type": "geo_point"
        },
        "utc_offset": {"type": "integer"},
        "timezone": { "type": "text" },
        "altitude": { "type": "integer" },
      }
    }
  }
}

try:
    res = es.indices.create(index='airport', body=settings_and_mapping)
except:
    pass

fieldnames = [
    'id',
    'name',
    'city',
    'country',
    'iata',
    'icao',
    'lat',
    'lon',
    'alt',
    'offset',
    'dst',
    'tz',
    'type',
    'source',
]

def create_doc(data):
    data['location'] = {
             'lat': float(airport['lat']),
             'lon': float(airport['lon'])
            }
    del data['lat']
    del data['lon']
    del data['id']
    return data

with open(airport_data, 'r') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=fieldnames)
    for batch in iter(lambda: tuple(islice(reader, 50)), ()):
        actions = []
        for airport in batch:
            _id = int(airport['id'])
            doc = create_doc(airport)
            action = {
                '_op_type': 'create',
                '_index': 'airport',
                '_type': '_doc',
                '_id': _id,
                '_source': doc
            }
            actions.append(action)

        res = helpers.bulk(es, actions)
        print(res)

if __name__ == '__main__':
    pass
