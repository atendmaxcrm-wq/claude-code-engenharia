# converte o registro de API (ndjson) em HAR 1.2 para o REA ler com inspect-web-network-capture
import json,sys
ent=[]
for l in open(sys.argv[1]):
    x=json.loads(l); h=lambda d:[{"name":k,"value":str(v)} for k,v in (d or {}).items()]
    req={"method":x['method'],"url":x['url'],"httpVersion":"HTTP/2.0","cookies":[],"headers":h(x.get('reqHeaders')),"queryString":[],"headersSize":-1,"bodySize":len(x['postData'] or '')}
    if x['postData']: req["postData"]={"mimeType":"application/json","text":x['postData']}
    body=x['body'] or ''
    res={"status":x['status'],"statusText":"","httpVersion":"HTTP/2.0","cookies":[],"headers":h(x.get('resHeaders')),"content":{"size":len(body),"mimeType":(x.get('resHeaders') or {}).get('content-type','application/json'),"text":body},"redirectURL":"","headersSize":-1,"bodySize":len(body)}
    ent.append({"startedDateTime":x['t'],"time":0,"request":req,"response":res,"cache":{},"timings":{"send":0,"wait":0,"receive":0}})
json.dump({"log":{"version":"1.2","creator":{"name":"rea-cce","version":"1"},"entries":ent}},open(sys.argv[2],'w'))
print(len(ent),'entradas')
