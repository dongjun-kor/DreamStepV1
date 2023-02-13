from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
import requests
import json

def index(request):
    if request.method == 'POST' and request.FILES['file']:
        api_key = request.POST.get('api_key')
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        xlsx_file = pd.read_excel(file_url)
        results = []

        for document in xlsx_file.iloc[:, 0]:
            data_list = {'document': document}
            inputs_list = {'data': data_list}
            req_list = {'Inputs': inputs_list, 'GlobalParameters': 1.0}

            req_json = json.dumps(req_list)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + api_key
            }
            response = requests.post('http://85703749-f0d5-489f-8a7f-724648002ab4.koreacentral.azurecontainer.io/score', headers=headers, data=req_json)

            if response.status_code >= 400:
                print('The request failed with status code:', response.status_code)
                print(response.headers)

            results.append(response.json()['Results'])

        xlsx_file['Result'] = results
        xlsx_file.to_excel('result.xlsx', index=False)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="result.xlsx"'
        xlsx_file.to_excel(response, index=False)
        return response

    return render(request, 'index.html')
