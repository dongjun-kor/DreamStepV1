from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import urllib.request
import json
import os
import ssl

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context()

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

def index(request):
    return render(request, 'index.html')

def process(request):
    file = request.FILES['file']
    # save the file to a folder on the server
    with open('/tmp/' + file.name, 'wb') as f:
        f.write(file.read())
    # read the uploaded file into a Pandas dataframe
    df = pd.read_excel('/tmp/' + file.name)
    # convert the dataframe to a JSON string
    data = {
        'Inputs': {
            'data': df.to_dict(orient='records')
        },
        'GlobalParameters': {
            'param': 1.0
        }
    }
    # encode the data to a byte string
    body = json.dumps(data).encode('utf-8')
    url = 'http://85703749-f0d5-489f-8a7f-724648002ab4.koreacentral.azurecontainer.io/score'
    # replace this with the primary/secondary key or AMLToken for the endpoint
    api_key = 'h5KzpB2p6x2zfoXFd28YNBzPQHdkLaHh'
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
    req = urllib.request.Request(url, body, headers)
    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        json_data = json.loads(result)
        # convert the JSON response to a Pandas dataframe
        result_df = pd.DataFrame(json_data['Results'],columns=['Results'])
        # combine the original data and the result dataframe into a single dataframe
        combined_df = pd.concat([df, result_df], axis=1)
        # convert the combined dataframe to an Excel file
        with pd.ExcelWriter('/tmp/result.xlsx') as writer:
            combined_df.to_excel(writer, index=False)
        # read the result file as a binary string
        with open('/tmp/result.xlsx', 'rb') as f:
            result_data = f.read()
        # return the result file as an HTTP response with the appropriate content type
        response = HttpResponse(result_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="result.xlsx"'
        return response
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        # print the headers - they include the request ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))
        return HttpResponse("Error: " + str(error.code))
