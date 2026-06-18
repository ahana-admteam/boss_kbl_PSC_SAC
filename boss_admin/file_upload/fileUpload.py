import pyotp
import base64
import requests
from datetime import datetime
# from JSFBDigitalRegistersDev import dev
from random import randint
# from jsfb_admin.models import PhoneMaster
from django.http import HttpResponse, response, JsonResponse
# from loan_review_register.models import DocumentTable
import json
from preliminaryscreeningcommittee_review.models import DocumentTable

#### my_url =  "https://hahttp.myvfirst.com/smpp/sendsms?username=JANAFOS&password=ebse(32hs&to="+str(phone)+"&udh=0&from=JANABK&text=Your%20One%20Time%20Password%20from%20Jana%20Bank%20for%20Mobile%20Number%20is"+str(myotp)+"and%20is%20valid%20for%2024%20Hours.%20Please%20do%20not%20share%20your%20OTP%20with%20anyone.&action=send&category=bulk"

class file_upload:
    
    def insert_documents(review_type,app, review_id,files_values, created_user):
        created_date = datetime.now()
        try: 
            # print("hqwdhqwoidjqwidhqowifhdoqwihdoqwijhd")
            for i in files_values:
                # print(i)
                # {'file_name': 'Screenshot (231).png', 'file_type': 'png', 'sectionNameInput': 'Insurance_doc1', 'document_id': '', 'file': '
                if i['document_id']:
                    # if DocumentTable.objects.filter(review_id=review_id, review_type=review_type,document_id=i['document_id']).exists():
                    #     DocumentTable.objects.filter(review_id=1, review_type=review_type,document_id=i['document_id']).update(
                    #                     file_name=i['file_name'],
                    #                     file= i['file'],
                    #                     file_type = i['file_type'],
                    #                     doc_type = i['doc_type'],
                    #                     created_date = created_date
                    #                     )
                    continue
                else:
                    # print(i['file'],"inside upload docs")
                    DocumentTable.objects.create(file_name=i['file_name'],
                                        file= i['file'],
                                        file_type = i['file_type'],
                                        section = i['section'],
                                        app = app,
                                        review_id=review_id,
                                        review_type=review_type,
                                        created_user=created_user)    
                    print('file saved')
                                            
                                            # created_user
                                            # section
                                            # review_type
                                            # review_id
                                            # app
                                            # file
                                            # file_name
                                            # file_type       
            return HttpResponse("Success")        
        except Exception as e:
            print("Exception raised", str(e))           
            return HttpResponse("Failed")



    def get_all_documents(app_name, review_id):
        # print("*****************Inside*******************", review_id,app_name)
        files_list = list(DocumentTable.objects.filter(review_id=review_id,app=app_name).values('document_id','file','file_name','section'))
        return files_list
    
    def get_single_document(document_id):
        # print("&&&&&&ADDADWDWQWQDQDQWD document id **********", document_id)
        file_val = list(DocumentTable.objects.filter(document_id = document_id).values('file','file_type','section'))
        # print("&&&&&&file values&&&&&&",file_val)
        return file_val




    def delete_documents(document_id):
        # print("delete document", document_id)
        DocumentTable.objects.filter(document_id=document_id).delete()
        return HttpResponse("Success")

