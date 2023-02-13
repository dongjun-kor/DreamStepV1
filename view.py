from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import requests
import pandas as pd

def home(request):
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)
        df = pd.read_excel(file_url)

        results = []
        for doc in df['document']:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            data = {
                'Inputs': {
                    'input1': {
                        'ColumnNames': ['document'],
                        'Values': [[doc]]
                    }
                },
                'GlobalParameters': {}
            }

            response = requests.post('http://85703749-f0d5-489f-8a7f-724648002ab4.koreacentral.azurecontainer.io/score', headers=headers, json=data)

            if response.status_code >= 400:
                return HttpResponse(f'Request failed with status code: {response.status_code}')

            result = response.json()['Results']['output1']['value']['Values'][0][0]
            results.append(result)

        df['Result'] = results

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=result_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx'
        df.to_excel(response, index=False)
        return response

    return render(request, 'home.html')
