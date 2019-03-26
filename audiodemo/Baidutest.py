from aip import AipSpeech
import requests
import os
import json
import uuid
import time
#语音识别
VOICE_APP_ID = '11611721'
VOICE_API_KEY = 'ykWjeT6KW143SDQKEH1vPAps'
VOICE_SECRET_KEY = '1lDDeBC40B8TPXWbAVDMuEzlz1MDcDcU'
speech_client = AipSpeech(VOICE_APP_ID, VOICE_API_KEY, VOICE_SECRET_KEY)

file_mp3 = 'salesman.wav'

'''
cmd_str = "ffmpeg -y  -i {file_name}.wav -acodec pcm_s16le -f s16le -ac 1 -ar 8000 {file_name}11.wav".format(file_name = file_mp3)
os.system(cmd_str)

with open("{file_name}.pcm".format(file_name = file_mp3), "rb") as f:
    audio_content = f.read()
res = speech_client.asr(audio_content, "pcm", 8000, {
    "dev_pid": 1537
})
print(res.get("result")[0])
with open("{file_name}".format(file_name = file_mp3), "rb") as f:
    audio_content = f.read()
res = speech_client.asr(audio_content, "wav", 8000, {
    "dev_pid": 1537
})
print(res.get("result")[0])
'''

#智能呼叫中心
companyName = 'xiaoneng'
suffix = 'wav'
CALL_APP_ID = 15146084
CALL_API_KEY = 'QYUQ1DGS5mzX5VK1uPsYsRZz'
CALL_SECRET_KEY = 'XNfnUDiyZIsYPx8RcbnfH3GOIGYvXPIH'
Token_request_url = "https://aip.baidubce.com/oauth/2.0/token"
Upload_request_url = "https://aip.baidubce.com/rpc/2.0/session/offline/upload/asr?access_token"
result_request_url = "https://aip.baidubce.com/rpc/2.0/search/info?access_token"
KEY_TASK_Content = 'content'
Token_payload = {
    'grant_type': 'client_credentials',
    'client_id':CALL_API_KEY,
    'client_secret':CALL_SECRET_KEY
}

start_time = time.time()
try:
    r = requests.post(Token_request_url, data = Token_payload)
except Exception as e:
    print(e)
data = json.loads(r.text)
access_token = data.get('access_token')
print(access_token)
expires_in = data.get('expires_in')
# # print(access_token)
# # print(expires_in)
if (access_token ):
    callId = str(uuid.uuid4())

    #callId = 'ecf52abd - 025c - 4f44 - b709 - 740cd9ca00be'
    print('callId is:', callId)
    agentFileUrl = "http://bj-v100.ntalker.com/setting/pcm/salesman.wav" #百度音频http://bj-v100.ntalker.com/setting/pcm/8k.wav
    clientFileUrl = 'http://bj-v100.ntalker.com/setting/pcm/customer.wav'
    Upload_request_url = Upload_request_url + '=' + access_token

    Upload_payload = {
        "appId": CALL_APP_ID,
        "companyName": companyName,
        "callId": callId,
        "agentFileUrl": agentFileUrl,
        "clientFileUrl":clientFileUrl,
        "suffix": "wav"
    }

    try:
        upload_reponse = requests.post(Upload_request_url, data= json.dumps(Upload_payload))
    except Exception as e:
        print(e)
    upload_data = json.loads(upload_reponse.text)
    print('the result of upload is ',upload_data )
    status = upload_data.get('status')
    msg = upload_data.get('msg')
    if status == 0 and  msg == 'OK':
        print("upload audio success")
        result_request_url = result_request_url  + '=' + access_token
        result_request_payload = {
            "category": "OFFLINE_ASR_RESULT",
            "paras": {
                         "appId":CALL_APP_ID,
                         "callId": callId,
            }
        }

        translate_start = time.time()
        while True:
            try:
                time.sleep(10)
                result_reponse = requests.post(result_request_url, data = json.dumps(result_request_payload))
            except Exception as e:
                print(e)
            result_data = json.loads(result_reponse.text)
            status = result_data.get('status')
            Content_list = result_data.get('data').get(KEY_TASK_Content)
            if  status ==0 and not result_data.get('status'):
                translate_end = time.time()
                print('the result of search is：', result_data)
                break
            continue

end_time = time.time()
print('time consuming is ',translate_end - translate_start)
#自定义音频 callId = '4dfb459c-791b-4a17-bec1-ffa628a606ea'
#百度音频测试
'''
# callId = 'eba3dfe8-e5e9-477a-80dd-50ceec57e0bf'
# access_token = '24.bfed9a6f00ae0e394710d4bf9b3f2cb3.2592000.1547613782.282335-15146084'
callId = '4e8695cb-8cc7-467d-9a05-c1b083a5e441' #百度client
#access_token = '24.bf0676ab26e2a3f374b759992892550a.2592000.1547614005.282335-15146084'
result_request_url = result_request_url + '=' + access_token

result_request_payload = {
    "category": "OFFLINE_ASR_RESULT",
    "paras": {
        "appId": CALL_APP_ID,
        "callId": callId,
    }
}
try:
    result_reponse = requests.post(result_request_url, data=json.dumps(result_request_payload))
except Exception as e:
    print(e)
result_data = json.loads(result_reponse.text)
#print('the result of search is：', result_data)
Content_list = result_data.get('data')[KEY_TASK_Content]

Agent_Data = [Content['sentence'] for Content in json.loads(Content_list) if Content['roleCategory'] == 'agent']
client_Data = [Content['sentence'] for Content in json.loads(Content_list) if Content['roleCategory'] == 'client']
Agent_Result = ''.join(Agent_Data)
client_Result = ''.join(client_Data)
print(Agent_Result)
print(client_Result)

'''










