from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
import requests
import json
import pandas as pd

def index(request):
    return render(request, 'index.html')

def submit(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        api_key = request.POST['api_key']
        url = 'http://85703749-f0d5-489f-8a7f-724648002ab4.koreacentral.azurecontainer.io/score'
        headers = {'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}
        results = []
        with open(uploaded_file_url, 'rb') as f:
            df = pd.read_excel(f)
            for i in range(len(df)):
                data = {'document': df.iloc[i, 0]}
                data = {'Inputs': {'data': data}, 'GlobalParameters': {}}
                data = json.dumps(data)
                response = requests.post(url, headers=headers, data=data)
                if response.status_code == 200:
                    result = json.loads(response.text)['Results']['output1'][0]['predicted_label']
                    results.append(result)
        context = {'results': results}
        return render(request, 'result.html', context)
    else:
        return HttpResponse('Please provide a file.')

def download(request):
    if request.method == 'POST':
        api_key = request.POST['api_key']
        url = 'http://85703749-f0d5-489f-8a7f-724648002ab4.koreacentral.azurecontainer.io/score'
        headers = {'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}
        results = []
        with open('media/documents/data.xlsx', 'rb') as f:
            df = pd.read_excel(f)
            for i in range(len(df)):
                data = {'document': df.iloc[i, 0]}
                data = {'Inputs': {'data': data}, 'GlobalParameters': {}}
                data = json.dumps(data)
                response = requests.post(url, headers=headers, data=data)
                if response.status_code == 200:
                    result = json.loads(response.text)['Results']['output1'][0]['predicted_label']
                    results.append(result)
        df['Result'] = results
        df.to_excel('media/documents/result.xlsx', index=False)
        file = open('media/documents/result.xlsx', 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/vnd.ms-excel'
        response['Content-Disposition'] = 'attachment; filename="result.xlsx"'
        return response
    else:
        return HttpResponse('Please provide an API key.')

