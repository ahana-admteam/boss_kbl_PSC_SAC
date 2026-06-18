from boss_v1 import settings
from jwcrypto import jwk, jwe
from datetime import datetime
import json, time
import requests

auth_urls = {
    'npa_status':'https://apiuat.ktkbank.com:8443/non-production/development/pscnpastatuscheckdetails/oauth2/token',
    'dashboard':'https://apiuat.ktkbank.com:8443/non-production/development/pscbranchdashboard/oauth2/token',
    'branch_data':'https://apiuat.ktkbank.com:8443/non-production/development/branch-address-api-oauth/oauth2/token',
    'emp_details':'https://apiuat.ktkbank.com:8443/non-production/development/fi-hupminq/oauth2/token',
    'customer_assets': 'https://apiuat.ktkbank.com:8443/non-production/development/fi-psccustomerassetdetailsfetch/oauth2/token'
}

service_urls = {
    'npa_status':'https://apiuat.ktkbank.com:8443/non-production/development/fi-pscnpastatuscheckdetails/status',
    'dashboard':'https://apiuat.ktkbank.com:8443/non-production/development/fi-pscbranchdashboarddetails/details',
    'branch_data':'https://apiuat.ktkbank.com:8443/non-production/development/branch-addres-api/jsbranch',
    'emp_details':'https://apiuat.ktkbank.com:8443/non-production/development/fi-hupminq/jsfihupminq',
    'customer_assets': 'https://apiuat.ktkbank.com:8443/non-production/development/fi-psccustomerassetdetailsfetch/fetchdetails'
}

client_id="c6dff9f323313c15c8ee9092f4dd978d"
client_secret="5bbdd10a0411afeca60327e4502dc75b"


class KBLAPIWrapper:

    def encrypt(msg):
        static_url = settings.base.KEYS_ROOT
        static_url = str(static_url).replace('\\', '/')
        with open(static_url+'\\uatreqenc25.pem','rb') as cert_file:
            public_key = jwk.JWK.from_pem(cert_file.read())

        payload = json.dumps(msg).encode('utf-8')
        protected_header  = {
            "alg": "RSA-OAEP-256",
            "enc": "A256GCM"
        }
        jwe_token = jwe.JWE(payload, recipient=public_key, protected=protected_header)
        jwecompact = jwe_token.serialize(True)
        return jwecompact

    def decrypt(msg):
        static_url = settings.base.KEYS_ROOT
        static_url = str(static_url).replace('\\', '/')
        with open(static_url+'\\plain.pem','rb') as cert_file:
            private_key = jwk.JWK.from_pem(cert_file.read())
        jwetoken = jwe.JWE()
        jwetoken.deserialize(msg, key=private_key)
        payload = jwetoken.payload
        data = json.loads(payload)
        return data

    def OAuthBearer(scope,url):
        # print('auth token',scope,url)
        payload = {
            "client_id":client_id,
            "client_secret":client_secret,
            "scope":scope,
            "grant_type":"client_credentials",
        }
        
        headers = {
            "Content-Type":"application/x-www-form-urlencoded",
        }
        
        response = requests.post(url=url, data=payload, headers=headers, verify=False)
        
        data = response.json()
        # print('acc token', data['access_token'])
        return data['access_token']

    def NPAStatusAPI(acc_id):
        try:
            #Generate Request ID
            _date = datetime.now()
            date = _date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

            req_id = "NPASts"+_date.strftime("%Y%m%d%H%M%S%f")

            #Generate OAUTH Token
            scope = "psc"
            auth_url = auth_urls['npa_status']
            token = KBLAPIWrapper.OAuthBearer(scope,auth_url)

            #Generate Encrypted Payload
            payload = {
                "RequestUUID" : req_id,
                "MessageDateTime" : str(date),
                "AcctId" : str(acc_id)
            }
            enc_data = KBLAPIWrapper.encrypt(payload)

            #Make API Call
            url = service_urls['npa_status']
            headers = {
                "Authorization" : f'Bearer {token}',
                "Content-Type" : "application/json",
                "X-IBM-Client-Id" : client_id,
                "X-IBM-Client-Secret" : client_secret,
            }
            body = {
                "Request" : f'{enc_data}'
            }
            response = requests.post(url=url, json=body, headers=headers, verify=False)
            enc_response = response.json()
            #Decrypt the encrypted respnse
            dec_data = KBLAPIWrapper.decrypt(enc_response["Response"])
            return dec_data
            
        except Exception as e:
            print(e)
            err_msg = {"response":"Response not received as API is down"}
            return err_msg

    def PSCDashboardAPI(branch_code):
        #Generate Request ID
        try:
            _date = datetime.now()
            date = _date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

            req_id = "PSCDshbrd"+_date.strftime("%Y%m%d%H%M%S%f")

            #Generate OAUTH Token
            scope = "Dashboard"
            auth_url = auth_urls['dashboard']
            # print('branch_code',branch_code,scope,auth_url)
            token = KBLAPIWrapper.OAuthBearer(scope,auth_url)
            # print(token)
            #Generate Encrypted Payload
            payload = {
                "RequestUUID" : req_id,
                "MessageDateTime" : str(date),
                "SolId" : str(branch_code),
                "AsOnDate" : "31-01-2025"
            }
            enc_data = KBLAPIWrapper.encrypt(payload)
            # print("enc_data",enc_data)
            #Make API Call
            url = service_urls['dashboard']
            headers = {
                "Authorization" : f'Bearer {token}',
                "Content-Type" : "application/json",
                "X-IBM-Client-Id" : client_id,
                "X-IBM-Client-Secret" : client_secret,
            }
            body = {
                "Request" : f'{enc_data}'
            }
            response = requests.post(url=url, json=body, headers=headers, verify=False)
            enc_response = response.json()
            # print("API Response",enc_response)

            #Decrypt the encrypted respnse
            dec_data = KBLAPIWrapper.decrypt(enc_response["Response"])
            # print("Decrypted data",dec_data)

            return dec_data
        except Exception as e:
            print(e)
            err_msg = {"response":"Response not received as API is down"}
            return err_msg

    def BranchDataAPI():
        try:
            # print("Branch API")

            #Generate Request ID
            date = datetime.now()
            req_id = "Brch"+date.strftime("%Y%m%d%H%M%S%f")

            #Generate OAUTH Token
            scope = "Branch"
            auth_url = auth_urls['branch_data']
            token = KBLAPIWrapper.OAuthBearer(scope,auth_url)
            # print("Token:",token)

            #Generate Encrypted Payload
            payload = {
                "requestId" : req_id,
                "asOnDate" : "29-05-2024"
            }
            enc_data = KBLAPIWrapper.encrypt(payload)
            # print("enc data",enc_data)

            #Make API Call
            url = service_urls['branch_data']
            headers = {
                "Authorization" : f'Bearer {token}',
                "Content-Type" : "application/json",
                "X-IBM-Client-Id" : client_id,
                "X-IBM-Client-Secret" : client_secret,
            }
            body = {
                "Request" : f'{enc_data}'
            }
            response = requests.post(url=url, json=body, headers=headers, verify=False)
            enc_response = response.json()
            # print('enc response')

            #Decrypt the encrypted respnse
            dec_data = KBLAPIWrapper.decrypt(enc_response["Response"])
            # print("dec response")

            return dec_data
        except Exception as e:
            print('Error',e)
            err_msg = {"response":"Response not received as API is down"}
            return err_msg

    def EmpDataAPI(empid):
        try:
            #Generate Request ID
            date = datetime.now()
            req_id = "Hupminq"+date.strftime("%Y%m%d%H%M%S%f")

            #Generate OAUTH Token
            scope = "HUPMINQ"
            auth_url = auth_urls['emp_details']
            token = KBLAPIWrapper.OAuthBearer(scope,auth_url)

            #Generate Encrypted Payload
            payload = {
                "requestId" : req_id,
                "UserId" : str(empid)
            }
            enc_data = KBLAPIWrapper.encrypt(payload)
            # print('enc data ', enc_data)
            #Make API Call
            url = service_urls['emp_details']
            headers = {
                "Authorization" : f'Bearer {token}',
                "Content-Type" : "application/json",
                "X-IBM-Client-Id" : client_id,
                "X-IBM-Client-Secret" : client_secret,
            }
            body = {
                "Request" : f'{enc_data}'
            }
            response = requests.post(url=url, json=body, headers=headers, verify=False)
            enc_response = response.json()


            #Decrypt the encrypted respnse
            dec_data = KBLAPIWrapper.decrypt(enc_response["Response"])
            print('dec data', dec_data)
            return dec_data
        except Exception as e:
            print('error ',e)
            err_msg = {"response":"Response not received as API is down"}
            return err_msg

    def CustomerAssetsAPI(cust_id):
        #Generate Request ID
        try:
            ca_start_time = time.time()
            _date = datetime.now()
            date = _date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

            req_id = "CustAssets"+_date.strftime("%Y%m%d%H%M%S%f")

            #Generate OAUTH Token
            scope = "CustomerAssets"
            auth_url = auth_urls['customer_assets']
            # print('cust_id',cust_id,scope,auth_url)
            token = KBLAPIWrapper.OAuthBearer(scope,auth_url)
            # print(token)
            #Generate Encrypted Payload
            payload = {
                "RequestUUID" : req_id,
                "MessageDateTime" : str(date),
                "custId" : str(cust_id),
                "asOnDate" : "31-12-2024"
            }
            print("payload", payload)
            enc_data = KBLAPIWrapper.encrypt(payload)
            # print("enc_data",enc_data)
            #Make API Call
            url = service_urls['customer_assets']
            headers = {
                "Authorization" : f'Bearer {token}',
                "Content-Type" : "application/json",
                "X-IBM-Client-Id" : client_id,
                "X-IBM-Client-Secret" : client_secret,
            }
            body = {
                "Request" : f'{enc_data}'
            }
            response = requests.post(url=url, json=body, headers=headers, verify=False)
            ca_end_time = time.time() - ca_start_time
            print("Action: {}, Message: {}, Time Taken:{}".format("Customer Assets API Response", response, ca_end_time))
            if response:
                enc_response = response.json()
                print("API Response",enc_response)

                #Decrypt the encrypted respnse
                dec_data = KBLAPIWrapper.decrypt(enc_response["Response"])

                ca_dec_time = time.time() - ca_start_time
                print("Action: {}, Message: {}, Time Taken to decrypt:{}".format("Customer Assets API Response", dec_data, ca_dec_time))
                return dec_data
            else:
                msg = "Customer Asset API is returning response"
                
                return msg

        except Exception as e:
            print(e)
            err_msg = {"response":f"Response not received{e}"}
            return err_msg
    

  
# branch_data = KBLAPIWrapper.BranchDataAPI()
# print(branch_data)

# dashboard_data = KBLAPIWrapper.PSCDashboardAPI("098")
# print(dashboard_data)
