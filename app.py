from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
from datetime import datetime


app = Flask(__name__)

client = MongoClient('mongodb+srv://nande:nande@cluster0.8kafc33.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta_plus_week2


@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
    return render_template(
        'index.html',
        words=words
    )


@app.route('/error')
def error():
    word = request.args.get('word')
    suggestions = request.args.get('suggestions')
    if suggestions:
        suggestions = suggestions.split(',')
    return render_template(
        'error.html',
        word=word,
        suggestions=suggestions
    )

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = "4a20bac2-b02b-40bb-8948-91ec4c27b194"
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for(
            'error',
            word=keyword
        ))

    if type(definitions[0]) is str:
        return redirect(url_for(
            'error',
            word=keyword,
            suggestions=','.join(definitions)
        ))

    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status
    )

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')
    dateB = json_data.get('date_give')
    doc = {
        'word': word,
        'definitions': definitions,
        'dateB': dateB,
    }
    db.words.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was saved!!!',
        'date': datetime.now().strftime('%Y.%m.%d')
    })


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'the word {word} was deleted'
    })


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)