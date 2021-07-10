from flask import Flask, jsonify
from flask import request
from flask_cors import CORS, cross_origin
from HarmonySearch.Candidate import Candidate
from HarmonySearch.HSearch import HSearch
from typing import List
import requests

app = Flask(__name__)
cors = CORS(app)




def recommendation(model):
    components = model['components']

    candidate_space: List[List[Candidate]] = []

    for component in components:

        leafs = get_leafs(component)

        candidate_space.append([Candidate(get_struct(l)) for l in leafs])

    hs = HSearch(candidate_space=candidate_space, loss_function=loss_function,
                 termination=40000,
                 harmony_memory_size=30,
                 harmony_memory_consideration_rate=0.3,
                 pitch_adjustment_rate=0.1)

    imp = hs.run()

    solution = [v.value for v in imp.candidates]

    resultText = "Availability: "+str(solution[0]['availability']*100)+"% Cost "+str(solution[0]['cost'])

    return resultText, [
        {
            'componentIdx': 0, #idx in components array,
            'replaceWith': 0 #id of solution componente
        }
    ]

def get_struct(component):
    return {
        'availability': 0,
        'cost': 0,
        'component':component
    }

def get_leafs(component):
    url = "localhost/component/"+str(component['id'])+'/leafs'
    resp = requests.get(url=url)
    data = resp.json()

    print('test',data)

    return []


def loss_function(candidates: List[Candidate])->float:

    return 0


@app.route('/', methods=['POST'])
@cross_origin()
def post_model():
    data = request.get_json()
    if data['model']['components']:
        a, r = recommendation(data['model'])
        response = jsonify({
            'result': a,
            'replacements': r
        })
    else:
        response =  jsonify({
            'result': 'No value (empty project)',
            'replacements': []
        })
    return response

if __name__ == '__main__':
    app.run(debug=True)