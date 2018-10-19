#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, make_response, send_from_directory, send_file

app = Flask(__name__, static_folder='../candysorter/static')


def __respond_json(text):
    resp = make_response(text)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route('/api/translate', methods=['POST'])
def translate():
    return __respond_json('''
        [
        {
            "input": "kan jeg få sjokolade",
            "translatedText": "Can I have some chocolate"
        }
    ]
    ''')


@app.route('/api/morphs', methods=['POST'])
def morph():
    return __respond_json('''
        {
        "morphs": [
            {
                "depend": {
                    "index": [],
                    "label": "AUX"
                },
                "pos": {
                    "case": "CASE_UNKNOWN",
                    "number": "NUMBER_UNKNOWN",
                    "tag": "VERB"
                },
                "word": "Can"
            },
            {
                "depend": {
                    "index": [],
                    "label": "NSUBJ"
                },
                "pos": {
                    "case": "NOMINATIVE",
                    "number": "SINGULAR",
                    "tag": "PRON"
                },
                "word": "I"
            },
            {
                "depend": {
                    "index": [
                        0,
                        1,
                        4
                    ],
                    "label": "ROOT"
                },
                "pos": {
                    "case": "CASE_UNKNOWN",
                    "number": "NUMBER_UNKNOWN",
                    "tag": "VERB"
                },
                "word": "have"
            },
            {
                "depend": {
                    "index": [],
                    "label": "NN"
                },
                "pos": {
                    "case": "CASE_UNKNOWN",
                    "number": "NUMBER_UNKNOWN",
                    "tag": "NOUN"
                },
                "word": "som"
            },
            {
                "depend": {
                    "index": [
                        3
                    ],
                    "label": "DOBJ"
                },
                "pos": {
                    "case": "CASE_UNKNOWN",
                    "number": "SINGULAR",
                    "tag": "NOUN"
                },
                "word": "chocolate"
            }
        ]
    }
    ''')


@app.route('/api/similarities', methods=['POST'])
def similarities():
    return __respond_json('''
    {
        "similarities": {
            "embedded": [
                {
                    "box": [
                        [
                            1194,
                            120
                        ],
                        [
                            1442,
                            114
                        ],
                        [
                            1450,
                            408
                        ],
                        [
                            1201,
                            415
                        ]
                    ],
                    "coords": [
                        0.3052026444050034,
                        0.46767496541417386
                    ],
                    "similarities": [
                        {
                            "em": 0.011613314040005207,
                            "label": "chocolate",
                            "lid": 1
                        },
                        {
                            "em": 0.0621197447180748,
                            "label": "gum",
                            "lid": 2
                        },
                        {
                            "em": 0.9146535396575928,
                            "label": "liquorice",
                            "lid": 3
                        },
                        {
                            "em": 0.011613314040005207,
                            "label": "smurf",
                            "lid": 4
                        }
                    ],
                    "url": "/image/20180710_094456_7523664522134304/candy_00_8kx2jt12.jpg"
                },
                {
                    "box": [
                        [
                            392,
                            510
                        ],
                        [
                            668,
                            553
                        ],
                        [
                            622,
                            853
                        ],
                        [
                            345,
                            810
                        ]
                    ],
                    "coords": [
                        0.30000000000000004,
                        0.4668201521292226
                    ],
                    "similarities": [
                        {
                            "em": 0.004918794147670269,
                            "label": "chocolate",
                            "lid": 1
                        },
                        {
                            "em": 0.05848325043916702,
                            "label": "gum",
                            "lid": 2
                        },
                        {
                            "em": 0.9316791296005249,
                            "label": "liquorice",
                            "lid": 3
                        },
                        {
                            "em": 0.004918794147670269,
                            "label": "smurf",
                            "lid": 4
                        }
                    ],
                    "url": "/image/20180710_094456_7523664522134304/candy_01_d4qu3c7b.jpg"
                },
                {
                    "box": [
                        [
                            1185,
                            603
                        ],
                        [
                            1421,
                            538
                        ],
                        [
                            1528,
                            929
                        ],
                        [
                            1292,
                            993
                        ]
                    ],
                    "coords": [
                        0.7,
                        0.29999999999999993
                    ],
                    "similarities": [
                        {
                            "em": 0.005034829024225473,
                            "label": "chocolate",
                            "lid": 1
                        },
                        {
                            "em": 0.9848954677581787,
                            "label": "gum",
                            "lid": 2
                        },
                        {
                            "em": 0.005034829024225473,
                            "label": "liquorice",
                            "lid": 3
                        },
                        {
                            "em": 0.005034829024225473,
                            "label": "smurf",
                            "lid": 4
                        }
                    ],
                    "url": "/image/20180710_094456_7523664522134304/candy_02_37bvx84t.jpg"
                }
            ],
            "force": [
                {
                    "em": 0.9,
                    "label": "chocolate",
                    "lid": 1
                },
                {
                    "em": 0.6333333333333333,
                    "label": "gum",
                    "lid": 2
                },
                {
                    "em": 0.3666666666666667,
                    "label": "liquorice",
                    "lid": 3
                },
                {
                    "em": 0.1,
                    "label": "smurf",
                    "lid": 4
                }
            ],
            "nearest": {
                "box": [
                    [
                        1185,
                        603
                    ],
                    [
                        1421,
                        538
                    ],
                    [
                        1528,
                        929
                    ],
                    [
                        1292,
                        993
                    ]
                ],
                "coords": [
                    0.7,
                    0.29999999999999993
                ],
                "similarities": [
                    {
                        "em": 0.005034829024225473,
                        "label": "chocolate",
                        "lid": 1
                    },
                    {
                        "em": 0.9848954677581787,
                        "label": "gum",
                        "lid": 2
                    },
                    {
                        "em": 0.005034829024225473,
                        "label": "liquorice",
                        "lid": 3
                    },
                    {
                        "em": 0.005034829024225473,
                        "label": "smurf",
                        "lid": 4
                    }
                ],
                "url": "/image/20180710_094456_7523664522134304/candy_02_37bvx84t.jpg"
            },
            "url": "/image/20180710_094456_7523664522134304/snapshot.jpg"
        }
    }
    ''')


@app.route('/api/pickup', methods=['POST'])
def pickup():
    return __respond_json('''
        [
        {
            "input": "kan jeg få sjokolade",
            "translatedText": "Can I have some chocolate"
        }
    ]
    ''')


@app.route('/image/<path:filename>')
def image(filename):
    return send_from_directory('images', filename)


@app.route('/predict')
def predict():
    return send_file('../candysorter/static/predict.html')


@app.route('/learn')
def learn():
    return send_file('../candysorter/static/learn.html')

@app.route('/settings')
def settings():
    return send_file('../candysorter/static/settings.html')
