from preliminaryscreeningcommittee_review.views.psc_views import *
from PyPDF2 import PdfReader, PdfMerger, PdfWriter
from fpdf import FPDF
#Export to PDFs
def save_base64_image_as_pdf(base64_string, file_path, file_type):
    # Decode base64 string
    image_data = base64.b64decode(base64_string)
    # If the file_type is 'PDF', just write the decoded data directly to a file
    if file_type.lower() == 'pdf':
        with open(file_path, 'wb') as f:
            f.write(image_data)
        return
    
    # Convert image data to a PIL Image object for PNG or JPG
    image = PIMG.open(io.BytesIO(image_data))
    
    # Save the image to a temporary file
    temp_img_path = f"temp_image.{file_type.lower()}"
    image.save(temp_img_path, file_type.upper())
    
    # If saving as PDF, embed the image in a PDF
    if file_type.lower() in ['png', 'jpg','jpeg']:
        pdf = FPDF()
        pdf.add_page()
        pdf.image(temp_img_path, x=10, y=10, w=pdf.w - 20)  # Adjust x, y, w as needed
        pdf.output(file_path)
        
        # Clean up temporary image file
        os.remove(temp_img_path)
        
    else:
        raise ValueError(file_type,"Unsupported file type. Please use 'png', 'jpg', 'jpeg', or 'pdf'.")

def pdf_merge(s_string, dirs):
    try:
        dirs = str(dirs).replace('\\', '/')
        x = [os.path.join(dirs, a) for a in os.listdir(dirs)
            if a.endswith(".pdf") and (a.startswith(s_string) or a.startswith("1_" + s_string))]

        # print(x, dirs)

        merger = PdfMerger()

        for pdf in x:
            try:
                with open(pdf, 'rb') as f:
                    merger.append(f)
            except FileNotFoundError:
                sc_log.error('PDF merger function error')
                print('PDF merger function error')
                print(f"File not found: {pdf}")

        # Create an in-memory buffer
        buffer = io.BytesIO()
        
        # Save the merged PDF to the buffer
        merger.write(buffer)
        merger.close()
        
        # Move the buffer pointer to the beginning
        buffer.seek(0)
        
        # Optionally, delete the temporary files
        for pdf in x:
            try:
                os.remove(pdf)
            except OSError as e:
                sc_log.error('File delete error error: ' + e)
                print("User Id: {}, Designation: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], "PDF merger error",e))


        return buffer
    except Exception as e:
        print("error in pdf merge ", e)
        return e

@my_login_required
def psc_review_export(request, pk, merge_condition):
    start_time = time.time()
    # Fetch MOM data
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    roles = request.session['new_roles'].split("_")
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    static_url = settings.base.STATIC_ROOT
    static_url = str(static_url).replace('\\', '/')
    logo_path = str(static_url)+'/assets/images/'+str(tenant)+'/'+str(tenant_image)
    psc_data = (PSCTable.objects.filter(id=pk).values(*psc_all_data).order_by('mom_id'))
    cust_idpsc = CustomerTable.objects.filter(npa_status=True,cust_id=psc_data[0]['cust_id']).values('id')[0]['id']
    credit_datapsc = CreditFacilityTable.objects.filter(psc_id=cust_idpsc).values(*creditsanction_all_data)       
    security_datapsc = SecuritiesTable.objects.filter(psc_id=cust_idpsc).values(*securities_all_data)    
    staff_accountability = psc_data[0]['staff_accountability']
    def process_accountability_data(key_dd, key):
            data = staff_accountability.get(key, [])
            condition = data[0].get(f"{key_dd}") if data else None
            if condition:
                return data
            else:
                return []
            
    pre_sanction = process_accountability_data('pre_sanction_lapses_dd', 'pre_sanction')
    #print('pre_sanction',pre_sanction)
    pre_sanction_lapses_sa = process_accountability_data('pre_sanction_lapses_sa_dd', 'pre_sanction_lapses_sa')
    #print('pre_sanction_lapses_sa',pre_sanction_lapses_sa)
    
    post_sanction = process_accountability_data('post_sanction_lapses_dd', 'post_sanction')
    post_sanction_sa = process_accountability_data('post_sanction_lapses_sa_dd', 'post_sanction_sa')
    post_sanction_ma = process_accountability_data('post_sanction_lapses_ma_dd', 'post_sanction_ma')
    sanction_lapses_po = process_accountability_data('sanction_lapses_po_dd', 'sanction_lapses_po')
    non_fulfillment_tc = process_accountability_data('non_fulfillment_tc_dd', 'non_fulfillment_tc')
    pow_exceeding_insts = process_accountability_data('pow_exceeding_insts_dd', 'pow_exceeding_insts')
    cersai = process_accountability_data('cersai_dd', 'cersai')
    valua_remarks_varia = process_accountability_data('valua_remarks_varia_dd', 'valua_remarks_varia')
    sec_availability = process_accountability_data('sec_availability_dd', 'sec_availability')
    loan_pro_woc = process_accountability_data('loan_pro_woc_dd', 'loan_pro_woc')
    loan_pro_np = process_accountability_data('loan_pro_np_dd', 'loan_pro_np')
    securities_div = process_accountability_data('securities_div_dd', 'securities_div')
    loan_sec_irregularities = process_accountability_data('loan_sec_irregularities_dd', 'loan_sec_irregularities')
    fraud_cases = process_accountability_data('fraud_cases_dd', 'fraud_cases')
    other_info = process_accountability_data('other_info_dd', 'other_info')
    aof = process_accountability_data('aof_dd', 'aof')
    # print('aof[0][aof_dd]',aof[0]['aof_dd'])
    post_sanc_doc_irregularities = process_accountability_data('post_sanc_doc_irregularities_dd', 'post_sanc_doc_irregularities')
    cgtmse_loan = process_accountability_data('cgtmse_loan_dd', 'cgtmse_loan')
    mortgage_notice = process_accountability_data('mortgage_notice_dd', 'mortgage_notice')
    housing_soc_conf = process_accountability_data('housing_soc_conf_dd', 'housing_soc_conf')
    post_mort_ec = process_accountability_data('post_mort_ec_dd', 'post_mort_ec')
    all_aod = staff_accountability['all_aod']
    # print('all_aod',all_aod)
    for aod in all_aod:
        aod['aodDates'] = aod['borrowerAODDate'].split(', ')
    doc_date_list = [{"i": idx + 1, "doc_date": entry['doc_date'].strftime("%d-%m-%Y")} for idx, entry in enumerate(credit_datapsc)]

    # Output
    # print('doc_date_list',doc_date_list)
    all_aod1 = []
    for doc in doc_date_list:
        for aod in all_aod:
            if str(doc['i']) == aod['borrowerAODNo']:  # Match 'i' with 'borrowerAODNo'
                all_aod1.append({
                    'i': doc['i'],
                    'doc_date': doc['doc_date'],
                    'borrowerAODNo': aod['borrowerAODNo'],
                    'borrowerAODDate': aod['borrowerAODDate'],
                    'aodDates': aod['aodDates']
                })
    # print(all_aod1)
    # print('all_aod',all_aod1)
    # return
    insepction_num = staff_accountability['insepction_num']
    staff_data = staff_accountability['staff_data']
    ad_sanc_bo = staff_accountability['ad_sanc_bo']
    bo_names = staff_accountability['bo_names']
    so_sa_name = staff_accountability['so_sa_name']   
    buffer = io.BytesIO()
    # pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=25, leftMargin=25, topMargin=18, bottomMargin=18)
    doc = SimpleDocTemplate(buffer, pagesize=(A4), rightMargin=5, leftMargin=5, topMargin=18, bottomMargin=3)
    Story=[]
    im = Image(logo_path, 1.5 * inch, 0.5 * inch)
    im.hAlign = 'LEFT'
    Story.append(im)
    Story.append(Spacer(1, 12))  # Adjust the height (second parameter) as needed
    data1 = []
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    H1 = Paragraph('''<para align=center><font size='13'><b><u>SUBMITTED TO THE PRELIMINARY SCREENING COMMITTEE – I or II REVIEW OF <br/><br/>NON PERFORMING ACCOUNTS / QUICK MORTALITY CASES</u></b></font></para>''',styles["BodyText"])
    heading1 = [H1]
    data1.append(heading1)
    data1.append('')
    r1c1 = Paragraph('''<para align=left><font size='10'><b>Branch : '''+ psc_data[0]['branch_code_id__branch_name'] +'''</b></font></para>''', styles["BodyText"])
    r1c2 = Paragraph('''<para align=right><font size='10'><b>Date : '''+psc_data[0]['creation_date'].strftime('%d-%m-%Y')+'''</b></font></para>''', styles["BodyText"])
    row1 = [r1c1,"",r1c2] 
    data1.append(row1)        
    r2c1 = Paragraph('''<para align=left><font size='10'><b>Region : '''+ psc_data[0]['region_name'] +'''</b></font></para>''', styles["BodyText"])
    r2c2 = Paragraph('''<para align=center><font size='10'><b>Cust Id : '''+psc_data[0]['cust_id']+'''</b></font></para>''', styles["BodyText"])
    r2c3 = Paragraph('''<para align=right><font size='10'><b>PSC No : '''+psc_data[0]['psc_rec_id']+'''</b></font></para>''', styles["BodyText"])
    row2 = [r2c1,r2c2,r2c3] 
    data1.append(row2)      
    data1.append('')      
    SH1 = Paragraph('''<para align=left><font size='11'><b>1. Basic Details</b></font></para>''',styles["BodyText"])
    subheading1 = [SH1]
    data1.append(subheading1)  
    r3c1 = Paragraph('''<para align=left><font size='10'>Borrower Name : '''+ psc_data[0]['borrower_name'] +'''</font></para>''', styles["BodyText"])
    r3c2 = Paragraph('''<para align=center><font size='10'>Borrower Address : '''+psc_data[0]['address']+'''</font></para>''', styles["BodyText"])
    r3c3 = Paragraph('''<para align=right><font size='10'>Constitution : '''+psc_data[0]['constitution']+'''</font></para>''', styles["BodyText"])
    row3 = [r3c1,r3c2,r3c3] 
    data1.append(row3)      
    r4c1 = Paragraph('''<para align=left><font size='10'>Proprietor's Name : '''+ psc_data[0]['partners'] +'''</font></para>''', styles["BodyText"])
    r4c2 = Paragraph('''<para align=center><font size='10'>Establishment Date : '''+psc_data[0]['establishment_date'].strftime('%d-%m-%Y')+'''</font></para>''', styles["BodyText"])
    r4c3 = Paragraph('''<para align=right><font size='10'>Networth of the Borrower : '''+str(psc_data[0]['networth'])+'''</font></para>''', styles["BodyText"])
    row4 = [r4c1,r4c2,r4c3] 
    data1.append(row4)      
    r5c1 = Paragraph('''<para align=left><font size='10'>Dealing with us since : '''+psc_data[0]['dealing_since'].strftime('%d-%m-%Y')+'''</font></para>''', styles["BodyText"])
    r5c2 = Paragraph('''<para align=center><font size='10'>Nature of business : '''+ psc_data[0]['business_nature'] +'''</font></para>''', styles["BodyText"])
    r5c3 = Paragraph('''<para align=right><font size='10'>Guarantor's Name : '''+str(psc_data[0]['guarantors_name'])+'''</font></para>''', styles["BodyText"])
    row5 = [r5c1,r5c2,r5c3] 
    data1.append(row5)      
    t1 = Table(data1)
    table_style1 = [ 
                ('SPAN', (0, 0), (2, 0)),  
                ('ALIGN',(0,0),(-1,-1),'LEFT')
                ]
    t1.setStyle(TableStyle(table_style1))
    total_width1 = 580  # Total available width in points
    column_width1 = total_width1 / 3
    t1._argW = [column_width1] * 3
    Story.append(t1)
    Story.append(Spacer(1, 10))  # Spacer between the two tables

    Story.append(Spacer(1,6))
    SHC = Paragraph('''<para align=left><font size='11'><b>2. Details of credit facility sanctioned.</b></font></para>''', styles["BodyText"])
    Story.append(SHC)
    Story.append(Spacer(1,3))
    
    cs_table_data = [['Sl. NO.',	'SRN',	'Date of Release',	'Nature of Account',	'Nature of Advance',	'LAN',	'Sanction Amount',	'Due Date',	'NPA Date',	'Present Balance',	'Current Balance',	'Purpose of Advance',	'Asset Classification', 'Document Date']]
    cs_table = Table(cs_table_data)
    
    for cs in credit_datapsc:
        cs_row = [
            cs['credit_feci_slno'] or '-',
            cs['reference_num'] or '-',
            cs['sanction_date'].strftime('%d-%m-%Y') if cs['sanction_date'] else '-',
            cs['account_nature'] or '-',
            cs['advance_nature'] or '-',
            cs['lan'] or '-',
            cs['sanctioned_limit'],
            cs['due_date'].strftime('%d-%m-%Y') if cs['due_date'] else '-',
            cs['npa_date'].strftime('%d-%m-%Y') if cs['npa_date'] else '-',
            cs['npa_balance'] or '-',
            cs['balance'] or '-',
            cs['advance_purpose'] or '-',
            cs['asset_classification'] or '-',
            cs['doc_date'].strftime('%d-%m-%Y') if cs['doc_date'] else '-'
        ]
        cs_table_data.append(cs_row)
    
    cs_table = Table(cs_table_data)
    cs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            # ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 3.5),  # Set font size
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
    ]))

    Story.append(cs_table)
    Story.append(Spacer(1, 10))  # Spacer between the two tables
    SHS = Paragraph('''<para align=left><font size='11'><b>3. Details of securities and value.</b></font></para>''', styles["BodyText"])
    Story.append(SHS)
    Story.append(Spacer(1,3))
    sv_table_data = [['Security Nature', 'LAN',	'Security Type', 'Sanction Valuation' ,'Sanction Valuation Date', 'Latest Valuation', 'Latest Valuation Date', 'Insurance Valid Upto', 'Insurance Value', 'CERSAI NO.']]
    sv_table = Table(sv_table_data)
    
    for sv in security_datapsc:
        sv_row = [
            sv['security_nature'] or '-',
            sv['lan'] or '-',
            sv['security_type'],
            sv['sanction_valuation'] or '-',
            sv['sanction_valuation_date'].strftime('%d-%m-%Y') if sv['sanction_valuation_date'] else '-',
            sv['latest_valuation'] or '-',
            sv['latest_valuation_date'].strftime('%d-%m-%Y') if sv['latest_valuation_date'] else '-',
            sv['insurance_valid_upto'].strftime('%d-%m-%Y') if sv['insurance_valid_upto'] else '-',
            sv['insurance_value'],
            sv['cersai_num'] or '-',
        ]
        sv_table_data.append(sv_row)
    
    sv_table = Table(sv_table_data)
    sv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            # ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 5),  # Set font size
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
    ]))

    Story.append(sv_table)
    
    data2 = []
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    data2.append('')     
    SHP = Paragraph('''<para align=left><font size='11'><b>4. Past Performance : </b>'''+ psc_data[0]['past_performance'] +'''</font></para>''', styles["BodyText"])
    subheadingP = [SHP]
    data2.append(subheadingP)      
    data2.append('')     
    r2c1 = Paragraph('''<para align=left><font size='11'><b>5. Reasons for the accounts turning into NPA: </b>'''+ psc_data[0]['npa_reasons'] +'''</font></para>''', styles["BodyText"])
    row2 = [r2c1] 
    data2.append(row2)      
    data2.append('')        
    r3c1 = Paragraph('''<para align=left><font size='11'><b>6. Present position / Recovery steps initiated etc.,: </b>'''+ psc_data[0]['recovery_steps'] +'''</font></para>''', styles["BodyText"])
    row3 = [r3c1] 
    data2.append(row3)  
    t2 = Table(data2)
    table_style2 = [ 
                ('ALIGN',(0,0),(-1,-1),'LEFT')
                ]
    t2.setStyle(TableStyle(table_style2))
    total_width2 = 580  # Total available width in points
    column_width2 = total_width2 
    t2._argW = [column_width2] 
    Story.append(t2)
    
    styles.add(ParagraphStyle(name='NormalRed', fontSize=10, textColor=colors.red))
    styles.add(ParagraphStyle(name='NormalBlack', fontSize=10, textColor=colors.black))
    SHSA = Paragraph('''<para align=left><font size='11'><b>7. Staff Accountability, if any:</b></font></para>''', styles["BodyText"])
    Story.append(SHSA)
    data3 = []
    Story.append(Spacer(1,8))
    r1c1 = Paragraph('''<para align=left><font size='11'>i)</font></para>''', styles["BodyText"])
    r1c2 = Paragraph('''<para align=left><font size='11'>Pre-sanction lapses if any: Branch / Sales Officer.\nIf yes, give full details.</font></para>''', styles["BodyText"])
    if not pre_sanction_lapses_sa:
        r1c3 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        r1c4 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        r1c3 = Paragraph('''<para align=left><font size='11'>'''+pre_sanction[0]['pre_sanction_lapses_dd']+'''</font></para>''', styles["BodyText"])
        r1c4 = Paragraph('''<para align=left><font size='11'>'''+pre_sanction[0]['pre_sanction_lapses_details']['pre_sanction_lapses_remarks']+'''</font></para>''', styles["BodyText"])
    row1 = [r1c1,r1c2,r1c3,r1c4]
    data3.append(row1)
    r2c1 = Paragraph('''<para align=left><font size='11'>ii)</font></para>''', styles["BodyText"])
    r2c2 = Paragraph('''<para align=left><font size='11'>Pre-sanction lapses at sanctioning office \nincluding sanctioning authority.\nIf yes, give full details.</font></para>''', styles["BodyText"])
    if not pre_sanction_lapses_sa:
        r2c3 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        r2c4 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        r2c3 = Paragraph('''<para align=left><font size='11'>'''+pre_sanction_lapses_sa[0]['pre_sanction_lapses_sa_dd']+'''</font></para>''', styles["BodyText"])
        r2c4 = Paragraph('''<para align=left><font size='11'>'''+pre_sanction_lapses_sa[0]['pre_sanction_lapses_sa_details']['pre_sanction_lapses_sa_remarks']+'''</font></para>''', styles["BodyText"])
    row2 = [r2c1,r2c2,r2c3,r2c4]
    data3.append(row2)
    r3c1 = Paragraph('''<para align=left><font size='11'>iii)</font></para>''', styles["BodyText"])
    r3c2 = Paragraph('''<para align=left><font size='11'>Post – sanction lapses if any: </font></para>''', styles["BodyText"])
    if not post_sanction:
        r3c3 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        r3c4 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        r3c3 = Paragraph('''<para align=left><font size='11'>'''+post_sanction[0]['post_sanction_lapses_dd']+'''</font></para>''', styles["BodyText"])
        r3c4 = Paragraph('''<para align=left><font size='11'>'''+post_sanction[0]['post_sanction_lapses_details']['post_sanction_lapses_remarks']+'''</font></para>''', styles["BodyText"])
    row3 = [r3c1,r3c2,r3c3,r3c4]
    data3.append(row3)
    row4_11 = Paragraph('''<para align=left><font size='11'>iv)</font></para>''', styles["BodyText"])
    row4_12 = Paragraph('''<para align=left><font size='11'>Post-sanction lapses at sanctioning office including sanctioning authority, if any.</font></para>''', styles["BodyText"])
    if not post_sanction_sa:
        row4_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row4_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row4_13 = Paragraph('''<para align=left><font size='11'>'''+post_sanction_sa[0]['post_sanction_lapses_sa_dd']+'''</font></para>''', styles["BodyText"])
        row4_14 = Paragraph('''<para align=left><font size='11'>'''+post_sanction_sa[0]['post_sanction_lapses_sa_details']['post_sanction_lapses_sa_remarks']+'''</font></para>''', styles["BodyText"])
    row4 = [row4_11,row4_12,row4_13,row4_14]
    data3.append(row4)
    row5_11 = Paragraph('''<para align=left><font size='11'>v)</font></para>''', styles["BodyText"])
    row5_12 = Paragraph('''<para align=left><font size='11'>Post-sanction lapses at monitoring office including monitoring authority, if any.</font></para>''', styles["BodyText"])
    if not post_sanction_ma:
        row5_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row5_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row5_13 = Paragraph('''<para align=left><font size='11'>'''+post_sanction_ma[0]['post_sanction_lapses_ma_dd']+'''</font></para>''', styles["BodyText"])
        row5_14 = Paragraph('''<para align=left><font size='11'>'''+post_sanction_ma[0]['post_sanction_lapses_ma_details']['post_sanction_lapses_ma_remarks']+'''</font></para>''', styles["BodyText"])
    row5 = [row5_11,row5_12,row5_13,row5_14]
    data3.append(row5)
    row6_11 = Paragraph('''<para align=left><font size='11'>vi)</font></para>''', styles["BodyText"])
    row6_12 = Paragraph('''<para align=left><font size='11'>Pre & Post sanction lapses at processing office like CLPU/CPC/RLPC etc. if any.	</font></para>''', styles["BodyText"])
    if not sanction_lapses_po:
        row6_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row6_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row6_13 = Paragraph('''<para align=left><font size='11'>'''+sanction_lapses_po[0]['sanction_lapses_po_dd']+'''</font></para>''', styles["BodyText"])
        row6_14 = Paragraph('''<para align=left><font size='11'>'''+sanction_lapses_po[0]['sanction_lapses_po_details']['sanction_lapses_po_remarks']+'''</font></para>''', styles["BodyText"])
    row6 = [row6_11,row6_12,row6_13,row6_14]
    data3.append(row6)
    row7_11 = Paragraph('''<para align=left><font size='11'>vii)</font></para>''', styles["BodyText"])
    row7_12 = Paragraph('''<para align=left><font size='11'>Non fulfilment of any terms and conditions of sanction, if any:	</font></para>''', styles["BodyText"])
    if not non_fulfillment_tc:
        row7_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row7_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row7_13 = Paragraph('''<para align=left><font size='11'>'''+non_fulfillment_tc[0]['non_fulfillment_tc_dd']+'''</font></para>''', styles["BodyText"])
        row7_14 = Paragraph('''<para align=left><font size='11'>'''+non_fulfillment_tc[0]['non_fulfillment_tc_details']['non_fulfillment_tc_remarks']+'''</font></para>''', styles["BodyText"])
    row7 = [row7_11,row7_12,row7_13,row7_14]
    data3.append(row7)
    row8_11 = Paragraph('''<para align=left><font size='11'>viii)</font></para>''', styles["BodyText"])
    row8_12 = Paragraph('''<para align=left><font size='11'>Deficiencies in the particular operations of the account. </font></para>''', styles["BodyText"])
    if not aof:
        row8_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row8_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    if aof:
        if aof[0]['aof_dd'] == 'NO':
            row8_13 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_dd']+'''</font></para>''', styles["BodyText"])
            row8_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        elif aof[0]['aof_dd'] == 'YES':
            row8_13 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_dd']+'''</font></para>''', styles["BodyText"])
            row8_14 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_remarks']+'''</font></para>''', styles["BodyText"])
    row8 = [row8_11,row8_12,row8_13,row8_14]
    data3.append(row8)
    if aof:
        if aof[0]['aof_dd'] == 'YES':
            row8a0 = Paragraph('''<para align=right><font size='11'>a)</font></para>''', styles["BodyText"])
            row8a1 = Paragraph('''<para align=left><font size='11'>Permission Reference Number</font></para>''', styles["BodyText"])
            row8a2 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_prn']+'''</font></para>''', styles["BodyText"])
            row8b0 = Paragraph('''<para align=right><font size='11'>b)</font></para>''', styles["BodyText"])
            row8b1 = Paragraph('''<para align=left><font size='11'>Diversion of funds</font></para>''', styles["BodyText"])
            row8b2 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_funds_div']+'''</font></para>''', styles["BodyText"])
            row8c0 = Paragraph('''<para align=right><font size='11'>c)</font></para>''', styles["BodyText"])
            row8c1 = Paragraph('''<para align=left><font size='11'>End use not ensured.</font></para>''', styles["BodyText"])
            row8c2 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_enduse']+'''</font></para>''', styles["BodyText"])
            row8d0 = Paragraph('''<para align=right><font size='11'>d)</font></para>''', styles["BodyText"])
            row8d1 = Paragraph('''<para align=left><font size='11'>In case of Housing loans for construction, Project Loans, Project completion certificate to be uploaded	</font></para>''', styles["BodyText"])
            row8d2 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_loan_type']+'''</font></para>''', styles["BodyText"])
            row8e0 = Paragraph('''<para align=right><font size='11'>e)</font></para>''', styles["BodyText"])
            row8e1 = Paragraph('''<para align=left><font size='11'>Unauthorised overdrawings</font></para>''', styles["BodyText"])
            row8e2 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_overdrawings']+'''</font></para>''', styles["BodyText"])
            row8f0 = Paragraph('''<para align=right><font size='11'>f)</font></para>''', styles["BodyText"])
            row8f1 = Paragraph('''<para align=left><font size='11'>Passing of cheques for non-business related transactions.</font></para>''', styles["BodyText"])
            row8f2 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_cheque_passing']+'''</font></para>''', styles["BodyText"])
            row8g0 = Paragraph('''<para align=right><font size='11'>g)</font></para>''', styles["BodyText"])
            row8g1 = Paragraph('''<para align=left><font size='11'>Disproportionate cash withdrawals.</font></para>''', styles["BodyText"])
            row8g2 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_dispro_withdrawls']+'''</font></para>''', styles["BodyText"])
            row8h0 = Paragraph('''<para align=right><font size='11'>h)</font></para>''', styles["BodyText"])
            row8h1 = Paragraph('''<para align=left><font size='11'>Transfer of amount to staff members etc.</font></para>''', styles["BodyText"])
            row8h2 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_staff_amt_trans']+'''</font></para>''', styles["BodyText"])
            row8i0 = Paragraph('''<para align=right><font size='11'>i)</font></para>''', styles["BodyText"])
            row8i1 = Paragraph('''<para align=left><font size='11'>Any other deficiencies (mention specifically).</font></para>''', styles["BodyText"])
            row8i2 = Paragraph('''<para align=left><font size='11'>'''+aof[0]['aof_details']['aof_other_deficiencies']+'''</font></para>''', styles["BodyText"])
            row8a = [row8a0,row8a1,"",row8a2]
            row8b = [row8b0,row8b1,"",row8b2]
            row8c = [row8c0,row8c1,"",row8c2]
            row8d = [row8d0,row8d1,"",row8d2]
            row8e = [row8e0,row8e1,"",row8e2]
            row8f = [row8f0,row8f1,"",row8f2]
            row8g = [row8g0,row8g1,"",row8g2]
            row8h = [row8h0,row8h1,"",row8h2]
            row8i = [row8i0,row8i1,"",row8i2]
            data3.append(row8a)
            data3.append(row8b)
            data3.append(row8c)
            data3.append(row8d)
            data3.append(row8e)
            data3.append(row8f)
            data3.append(row8g)
            data3.append(row8h)
            data3.append(row8i)
    row9_11 = Paragraph('''<para align=left><font size='11'>ix)</font></para>''', styles["BodyText"])
    row9_12 = Paragraph('''<para align=left><font size='11'>Non fulfilment of any terms and conditions of sanction, if any:	</font></para>''', styles["BodyText"])
    if not pow_exceeding_insts:
        row9_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row9_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row9_13 = Paragraph('''<para align=left><font size='11'>'''+pow_exceeding_insts[0]['pow_exceeding_insts_dd']+'''</font></para>''', styles["BodyText"])
        row9_14 = Paragraph('''<para align=left><font size='11'>'''+pow_exceeding_insts[0]['pow_exceeding_insts_details']['pow_exceeding_insts_remarks']+'''</font></para>''', styles["BodyText"])
    row9 = [row9_11,row9_12,row9_13,row9_14]
    data3.append(row9)
    row10_11 = Paragraph('''<para align=left><font size='11'>x)</font></para>''', styles["BodyText"])
    row10_12 = Paragraph('''<para align=left><font size='11'>Irregularity if any in the Post Sanction documentation.</font></para>''', styles["BodyText"])
    if not post_sanc_doc_irregularities:
        row10_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row10_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row10_13 = Paragraph('''<para align=left><font size='11'>'''+post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_dd']+'''</font></para>''', styles["BodyText"])
        row10_14 = Paragraph('''<para align=left><font size='11'>'''+post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_details']['post_sanc_doc_irregularities_remarks']+'''</font></para>''', styles["BodyText"])
    row10 = [row10_11,row10_12,row10_13,row10_14]
    data3.append(row10)
    if post_sanc_doc_irregularities:
        if post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_dd'] == 'YES':
            row10a0 = Paragraph('''<para align=right><font size='11'>a)</font></para>''', styles["BodyText"])
            row10a1 = Paragraph('''<para align=left><font size='11'>Not obtained required documents.</font></para>''', styles["BodyText"])
            row10a2 = Paragraph('''<para align=left><font size='11'>'''+post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_details']['psdi_req_docs_obtained']+'''</font></para>''', styles["BodyText"])
            row10b0 = Paragraph('''<para align=right><font size='11'>b)</font></para>''', styles["BodyText"])
            row10b1 = Paragraph('''<para align=left><font size='11'>Not obtained signature of all concerned parties as required.</font></para>''', styles["BodyText"])
            row10b2 = Paragraph('''<para align=left><font size='11'>'''+post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_details']['psdi_req_sign_obtained']+'''</font></para>''', styles["BodyText"])
            row10c0 = Paragraph('''<para align=right><font size='11'>c)</font></para>''', styles["BodyText"])
            row10c1 = Paragraph('''<para align=left><font size='11'>Not properly stamped as required.</font></para>''', styles["BodyText"])
            row10c2 = Paragraph('''<para align=left><font size='11'>'''+post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_details']['psdi_stamped']+'''</font></para>''', styles["BodyText"])
            row10d0 = Paragraph('''<para align=right><font size='11'>d)</font></para>''', styles["BodyText"])
            row10d1 = Paragraph('''<para align=left><font size='11'>Not done registration with subregistrar's office as required.</font></para>''', styles["BodyText"])
            row10d2 = Paragraph('''<para align=left><font size='11'>'''+post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_details']['psdi_reg_subrer_off']+'''</font></para>''', styles["BodyText"])
            row10e0 = Paragraph('''<para align=right><font size='11'>e)</font></para>''', styles["BodyText"])
            row10e1 = Paragraph('''<para align=left><font size='11'>Not noted the Bank's hypothecation clause in Registration Certificate of the vehicle, as required.</font></para>''', styles["BodyText"])
            row10e2 = Paragraph('''<para align=left><font size='11'>'''+post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_details']['psdi_rc_hypo_clause']+'''</font></para>''', styles["BodyText"])
            row10f0 = Paragraph('''<para align=right><font size='11'>f)</font></para>''', styles["BodyText"])
            row10f1 = Paragraph('''<para align=left><font size='11'>Periodical asset verification not done as required.</font></para>''', styles["BodyText"])
            row10f2 = Paragraph('''<para align=left><font size='11'>'''+post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_details']['psdi_periodic_asset_ver']+'''</font></para>''', styles["BodyText"])
            row10g0 = Paragraph('''<para align=right><font size='11'>g)</font></para>''', styles["BodyText"])
            row10g1 = Paragraph('''<para align=left><font size='11'>Any other lapses, mention specifically.</font></para>''', styles["BodyText"])
            row10g2 = Paragraph('''<para align=left><font size='11'>'''+post_sanc_doc_irregularities[0]['post_sanc_doc_irregularities_details']['psdi_other_lapses']+'''</font></para>''', styles["BodyText"])
            row10a = [row10a0,row10a1,"",row10a2]
            row10b = [row10b0,row10b1,"",row10b2]
            row10c = [row10c0,row10c1,"",row10c2]
            row10d = [row10d0,row10d1,"",row10d2]
            row10e = [row10e0,row10e1,"",row10e2]
            row10f = [row10f0,row10f1,"",row10f2]
            row10g = [row10g0,row10g1,"",row10g2]
            data3.append(row10a)
            data3.append(row10b)
            data3.append(row10c)
            data3.append(row10d)
            data3.append(row10e)
            data3.append(row10f)
            data3.append(row10g)
    row11_11 = Paragraph('''<para align=left><font size='11'>xi)</font></para>''', styles["BodyText"])
    row11_12 = Paragraph('''<para align=left><font size='11'>Registered the Bank’s charge with CERSAI.	</font></para>''', styles["BodyText"])
    if not cersai:
        row11_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row11_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row11_13 = Paragraph('''<para align=left><font size='11'>'''+cersai[0]['cersai_dd']+'''</font></para>''', styles["BodyText"])
        row11_14 = Paragraph('''<para align=left><font size='11'>'''+cersai[0]['cersai_details']['cersai_remarks']+'''</font></para>''', styles["BodyText"])
    row11 = [row11_11,row11_12,row11_13,row11_14]
    data3.append(row11)
    row12_11 = Paragraph('''<para align=left><font size='11'>xii)</font></para>''', styles["BodyText"])
    row12_12 = Paragraph('''<para align=left><font size='11'>Whether loan is covered under CGTMSE.</font></para>''', styles["BodyText"])
    if not cgtmse_loan:
        row12_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row12_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row12_13 = Paragraph('''<para align=left><font size='11'>'''+cgtmse_loan[0]['cgtmse_loan_dd']+'''</font></para>''', styles["BodyText"])
        row12_14 = Paragraph('''<para align=left><font size='11'>'''+cgtmse_loan[0]['cgtmse_loan_details']['cgtmse_loan_remarks']+'''</font></para>''', styles["BodyText"])
    row12 = [row12_11,row12_12,row12_13,row12_14]
    data3.append(row12)
    if cgtmse_loan:
        if cgtmse_loan[0]['cgtmse_loan_dd'] == 'YES':
            row12a0 = Paragraph('''<para align=right><font size='11'>a)</font></para>''', styles["BodyText"])
            row12a1 = Paragraph('''<para align=left><font size='11'>CG PAN Number	</font></para>''', styles["BodyText"])
            row12a2 = Paragraph('''<para align=left><font size='11'>'''+cgtmse_loan[0]['cgtmse_loan_details']['cg_pan_num']+'''</font></para>''', styles["BodyText"])
            row12a = [row12a0,row12a1,"",row12a2]
            data3.append(row12a)
    row13_11 = Paragraph('''<para align=left><font size='11'>xiii)</font></para>''', styles["BodyText"])
    row13_12 = Paragraph('''<para align=left><font size='11'>Notice of mortgage sent to concerned Sub-registrar’s Office (YES/NO). In case of Branches situated in Maharashtra:	</font></para>''', styles["BodyText"])
    if not mortgage_notice:
        row13_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row13_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row13_13 = Paragraph('''<para align=left><font size='11'>'''+mortgage_notice[0]['mortgage_notice_dd']+'''</font></para>''', styles["BodyText"])
        row13_14 = Paragraph('''<para align=left><font size='11'>'''+mortgage_notice[0]['mortgage_notice_details']['mortgage_notice_remarks']+'''</font></para>''', styles["BodyText"])
    row13 = [row13_11,row13_12,row13_13,row13_14]
    data3.append(row13)
    if mortgage_notice:
        if mortgage_notice[0]['mortgage_notice_dd'] == 'YES':
            row13a0 = Paragraph('''<para align=right><font size='11'>a)</font></para>''', styles["BodyText"])
            row13a1 = Paragraph('''<para align=left><font size='11'>Place of SRO office	.</font></para>''', styles["BodyText"])
            row13a2 = Paragraph('''<para align=left><font size='11'>'''+mortgage_notice[0]['mortgage_notice_details']['mortgage_notice_sro_place']+'''</font></para>''', styles["BodyText"])
            row13b0 = Paragraph('''<para align=right><font size='11'>b)</font></para>''', styles["BodyText"])
            row13b1 = Paragraph('''<para align=left><font size='11'>Reference Number.</font></para>''', styles["BodyText"])
            row13b2 = Paragraph('''<para align=left><font size='11'>'''+mortgage_notice[0]['mortgage_notice_details']['mortgage_notice_ref_num']+'''</font></para>''', styles["BodyText"])
            row13c0 = Paragraph('''<para align=right><font size='11'>c)</font></para>''', styles["BodyText"])
            row13c1 = Paragraph('''<para align=left><font size='11'>Date</font></para>''', styles["BodyText"])
            row13c2 = Paragraph('''<para align=left><font size='11'>'''+mortgage_notice[0]['mortgage_notice_details']['mortgage_notice_date']+'''</font></para>''', styles["BodyText"])
            row13d0 = Paragraph('''<para align=right><font size='11'>d)</font></para>''', styles["BodyText"])
            row13d1 = Paragraph('''<para align=left><font size='11'>Details of notice of intimation to be submitted	.</font></para>''', styles["BodyText"])
            row13d2 = Paragraph('''<para align=left><font size='11'>'''+mortgage_notice[0]['mortgage_notice_details']['mortgage_notice_details']+'''</font></para>''', styles["BodyText"])
            row13e0 = Paragraph('''<para align=right><font size='11'>e)</font></para>''', styles["BodyText"])
            row13e1 = Paragraph('''<para align=left><font size='11'>Details of NOC obtained by society.</font></para>''', styles["BodyText"])
            row13e2 = Paragraph('''<para align=left><font size='11'>'''+mortgage_notice[0]['mortgage_notice_details']['mortgage_notice_noc']+'''</font></para>''', styles["BodyText"])
            
            row13a = [row13a0,row13a1,"",row13a2]
            row13b = [row13b0,row13b1,"",row13b2]
            row13c = [row13c0,row13c1,"",row13c2]
            row13d = [row13d0,row13d1,"",row13d2]
            row13e = [row13e0,row13e1,"",row13e2]
            
            data3.append(row13a)
            data3.append(row13b)
            data3.append(row13c)
            data3.append(row13d)
            data3.append(row13e)
    row14_11 = Paragraph('''<para align=left><font size='11'>xiv)</font></para>''', styles["BodyText"])
    row14_12 = Paragraph('''<para align=left><font size='11'>Confirmation from Housing Society etc. obtained for having noted the Bank's charge on the immovable property (YES/NO). In case of Branches situated in Maharashtra:</font></para>''', styles["BodyText"])
    if not housing_soc_conf:
        row14_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row14_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row14_13 = Paragraph('''<para align=left><font size='11'>'''+housing_soc_conf[0]['housing_soc_conf_dd']+'''</font></para>''', styles["BodyText"])
        row14_14 = Paragraph('''<para align=left><font size='11'>'''+housing_soc_conf[0]['housing_soc_conf_details']['housing_soc_conf_remarks']+'''</font></para>''', styles["BodyText"])
    row14 = [row14_11,row14_12,row14_13,row14_14]
    data3.append(row14)
    if housing_soc_conf:
        if housing_soc_conf[0]['housing_soc_conf_dd'] == 'YES':
            row14a0 = Paragraph('''<para align=right><font size='11'>a)</font></para>''', styles["BodyText"])
            row14a1 = Paragraph('''<para align=left><font size='11'>Details of notice of Intimation to be submitted	</font></para>''', styles["BodyText"])
            row14a2 = Paragraph('''<para align=left><font size='11'>'''+housing_soc_conf[0]['housing_soc_conf_details']['housing_soc_conf_detail']+'''</font></para>''', styles["BodyText"])
            row14b0 = Paragraph('''<para align=right><font size='11'>b)</font></para>''', styles["BodyText"])
            row14b1 = Paragraph('''<para align=left><font size='11'>Details of NOC obtained by Society	</font></para>''', styles["BodyText"])
            row14b2 = Paragraph('''<para align=left><font size='11'>'''+housing_soc_conf[0]['housing_soc_conf_details']['housing_soc_conf_noc']+'''</font></para>''', styles["BodyText"])
            row14a = [row14a0,row14a1,"",row14a2]
            row14b = [row14b0,row14b1,"",row14b2]
            data3.append(row14a)
            data3.append(row14b)
    row15_11 = Paragraph('''<para align=left><font size='11'>xv)</font></para>''', styles["BodyText"])
    row15_12 = Paragraph('''<para align=left><font size='11'>Enforceability Certificate obtained post mortgage by the Panel Advocate .</font></para>''', styles["BodyText"])
    if not post_mort_ec:
        row15_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row15_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row15_13 = Paragraph('''<para align=left><font size='11'>'''+post_mort_ec[0]['post_mort_ec_dd']+'''</font></para>''', styles["BodyText"])
        row15_14 = Paragraph('''<para align=left><font size='11'>'''+post_mort_ec[0]['post_mort_ec_ad_details']['post_mort_ec_remarks']+'''</font></para>''', styles["BodyText"])
    row15 = [row15_11,row15_12,row15_13,row15_14]
    data3.append(row15)
    if post_mort_ec:
        if post_mort_ec[0]['post_mort_ec_dd'] == 'YES':
            row15a0 = Paragraph('''<para align=right><font size='11'>a)</font></para>''', styles["BodyText"])
            row15a1 = Paragraph('''<para align=left><font size='11'>Name of Legal Advisor</font></para>''', styles["BodyText"])
            row15a2 = Paragraph('''<para align=left><font size='11'>'''+post_mort_ec[0]['post_mort_ec_ad_details']['post_mort_ec_ad_name']+'''</font></para>''', styles["BodyText"])
            row15b0 = Paragraph('''<para align=right><font size='11'>b)</font></para>''', styles["BodyText"])
            row15b1 = Paragraph('''<para align=left><font size='11'>Date of EC</font></para>''', styles["BodyText"])
            row15b2 = Paragraph('''<para align=left><font size='11'>'''+post_mort_ec[0]['post_mort_ec_ad_details']['post_mort_ec_date']+'''</font></para>''', styles["BodyText"])
            row15a = [row15a0,row15a1,"",row15a2]
            row15b = [row15b0,row15b1,"",row15b2]
            data3.append(row15a)
            data3.append(row15b)
    row16_11 = Paragraph('''<para align=left><font size='11'>xvi)</font></para>''', styles["BodyText"])
    row16_12 = Paragraph('''<para align=left><font size='11'>Deficiencies in the security like wide variations in valuations etc.</font></para>''', styles["BodyText"])
    if not valua_remarks_varia:
        row16_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row16_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row16_13 = Paragraph('''<para align=left><font size='11'>'''+valua_remarks_varia[0]['valua_remarks_varia_dd']+'''</font></para>''', styles["BodyText"])
        row16_14 = Paragraph('''<para align=left><font size='11'>'''+valua_remarks_varia[0]['valua_remarks_varia_details']['valua_remarks_varia_remarks']+'''</font></para>''', styles["BodyText"])
    row16 = [row16_11,row16_12,row16_13,row16_14]
    data3.append(row16)
    row17_11 = Paragraph('''<para align=left><font size='11'>xvii)</font></para>''', styles["BodyText"])
    row17_12 = Paragraph('''<para align=left><font size='11'>AOD obtained from all borrower(s)/guarantors/co-obligant(s)</font></para>''', styles["BodyText"])
    row17 = [row17_11, row17_12]
    # data3.append(row17)
    if all_aod1:
    # Create the AOD table header
        table_data = [['SL No', 'Document Date', 'AOD Dates']]
    
        # for index, aod in enumerate(all_aod, start=1):
        #     sl_no = str(index)
        #     borrowerAODDate = aod['borrowerAODDate']
        #     table_data.append([sl_no, borrowerAODDate])
        for index, aod in enumerate(all_aod1, start=1):
            sl_no = str(index)
            borrowerAODDates = []
            
            for date in aod['borrowerAODDate'].split(','):
                date = date.strip()
                try:
                    # Attempt to parse as yyyy-MM-dd and convert to dd-MM-yyyy
                    formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
                except ValueError:
                    # If parsing fails, assume the date is already in dd-MM-yyyy format
                    formatted_date = date
                
                borrowerAODDates.append(formatted_date)

            doc_dateAOD = aod['doc_date']  # You can handle doc_date similarly if needed
            dates_paragraph = Paragraph(',<br />'.join(borrowerAODDates), styles["BodyText"])
            table_data.append([sl_no, doc_dateAOD, dates_paragraph])


    # Create the table
        table = Table(table_data, colWidths=[50, 75])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

    # Add the table to the data3 list
        row17.append("")
        row17.append([table])
    data3.append(row17)
    row18_11 = Paragraph('''<para align=left><font size='11'>xvii)</font></para>''', styles["BodyText"])
    row18_12 = Paragraph('''<para align="left"><font size="11">
                            Availability of security for enforceability (YES/NO)<br/><br/>
                            Prime:<br/><br/>
                            Collateral:<br/><br/>
                            If not, mention specifically. To be clearly mentioned such as stock, P&M,
                            Furniture & Fixtures available or not.
                            </font></para>''', styles["BodyText"])
    if not sec_availability:
        row18_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row18_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row18_13 = Paragraph('''<para align=left><font size='11'>'''+sec_availability[0]['sec_availability_dd']+'''</font></para>''', styles["BodyText"])
        row18_14 = Paragraph('''<para align=left><font size='11'>'''+sec_availability[0]['sec_availability_details']['sec_availability_remarks']+'''</font></para>''', styles["BodyText"])
    row18 = [row18_11,row18_12,row18_13,row18_14]
    data3.append(row18)
    row19_11 = Paragraph('''<para align=left><font size='11'>xix)</font></para>''', styles["BodyText"])
    row19_12 = Paragraph('''<para align="left"><font size="11">In case of Project Loan
                            </font></para>''', styles["BodyText"])
    row19 = [row19_11,row19_12]
    data3.append(row19)
    row19a_01 = Paragraph('''<para align=right><font size='11'>a)</font></para>''', styles["BodyText"])
    row19a_02 = Paragraph('''<para align=left><font size='11'>Loan proceeds released without the consent of the monitoring department (CrMD/RO as the case may be). (YES/no). If YES give full details.</font></para>''', styles["BodyText"])
    if not loan_pro_woc:
        row19a_11 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row19a_12 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row19a_11 = Paragraph('''<para align=left><font size='11'>'''+loan_pro_woc[0]['loan_pro_woc_dd']+'''</font></para>''', styles["BodyText"])
        row19a_12 = Paragraph('''<para align=left><font size='11'>'''+loan_pro_woc[0]['loan_pro_woc_details']['loan_pro_woc_remarks']+'''</font></para>''', styles["BodyText"])
    row19b = [row19a_01,row19a_02,row19a_11,row19a_12]
    data3.append(row19b)
    row19b_01 = Paragraph('''<para align=right><font size='11'>b)</font></para>''', styles["BodyText"])
    row19b_02 = Paragraph('''<para align=left><font size='11'>Loan proceeds released not proportionate to the work progress/creation of securities(YES/NO).</font></para>''', styles["BodyText"])
    if not loan_pro_np:
        row19b_11 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row19b_12 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row19b_11 = Paragraph('''<para align=left><font size='11'>'''+loan_pro_np[0]['loan_pro_np_dd']+'''</font></para>''', styles["BodyText"])
        row19b_12 = Paragraph('''<para align=left><font size='11'>'''+loan_pro_np[0]['loan_pro_np_details']['loan_pro_np_remarks']+'''</font></para>''', styles["BodyText"])
    row19b = [row19b_01,row19b_02,row19b_11,row19b_12]
    data3.append(row19b)
    row20_11 = Paragraph('''<para align=left><font size='11'>xx)</font></para>''', styles["BodyText"])
    row20_12 = Paragraph('''<para align=left><font size='11'>Deviation observed if any, between the securities stipulated as per terms of sanction and securities actually held. If so, furnish full details.</font></para>''', styles["BodyText"])
    if not securities_div:
        row20_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row20_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row20_13 = Paragraph('''<para align=left><font size='11'>'''+securities_div[0]['securities_div_dd']+'''</font></para>''', styles["BodyText"])
        row20_14 = Paragraph('''<para align=left><font size='11'>'''+securities_div[0]['securities_div_details']['securities_div_remarks']+'''</font></para>''', styles["BodyText"])
    row20 = [row20_11,row20_12,row20_13,row20_14]
    data3.append(row20)
    row21_11 = Paragraph('''<para align=left><font size='11'>xxi)</font></para>''', styles["BodyText"])
    row21_12 = Paragraph('''<para align=left><font size='11'>Irregularity if any in the loan/ security documentation affecting enforceability of loan/security.</font></para>''', styles["BodyText"])
    if not loan_sec_irregularities:
        row21_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row21_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row21_13 = Paragraph('''<para align=left><font size='11'>'''+loan_sec_irregularities[0]['loan_sec_irregularities_dd']+'''</font></para>''', styles["BodyText"])
        row21_14 = Paragraph('''<para align=left><font size='11'>'''+loan_sec_irregularities[0]['loan_sec_irregularities_details']['loan_sec_irregularities_remarks']+'''</font></para>''', styles["BodyText"])
    row21 = [row21_11,row21_12,row21_13,row21_14]
    data3.append(row21)
    row22_11 = Paragraph('''<para align=left><font size='11'>xxii)</font></para>''', styles["BodyText"])
    row22_12 = Paragraph('''<para align=left><font size='11'>Whether the cases involve an element offraud/connotation of fraud ?</font></para>''', styles["BodyText"])
    if not fraud_cases:
        row22_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row22_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row22_13 = Paragraph('''<para align=left><font size='11'>'''+fraud_cases[0]['fraud_cases_dd']+'''</font></para>''', styles["BodyText"])
        row22_14 = Paragraph('''<para align=left><font size='11'>'''+fraud_cases[0]['fraud_cases_details']['fraud_cases_remarks']+'''</font></para>''', styles["BodyText"])
    row22 = [row22_11,row22_12,row22_13,row22_14]
    data3.append(row22)
    row23_11 = Paragraph('''<para align=left><font size='11'>xxiii)</font></para>''', styles["BodyText"])
    row23_12 = Paragraph('''<para align=left><font size='11'>Number of Inspection done at the Branch by Inspection Officials (from the date of sanction till date)</font></para>''', styles["BodyText"])
    if not insepction_num:
        row23_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row23_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row23_13 = Paragraph('''<para align=left><font size='11'>'''+insepction_num[0]['num_inspec_lapses']+'''</font></para>''', styles["BodyText"])
        row23_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    row23 = [row23_11,row23_12,row23_13,row23_14]
    data3.append(row23)
    row23a_01 = Paragraph('''<para align=right><font size='11'>a)</font></para>''', styles["BodyText"])
    row23a_02 = Paragraph('''<para align=left><font size='11'>Lapses if any observed.<br/><br/>
                                Name of Inspection Official(s)</font></para>''', styles["BodyText"])
    if not insepction_num:
        row23a_11 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row23a_12 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row23a_11 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row23a_12 = Paragraph('''<para align=left><font size='11'>'''+insepction_num[0]['ob_inspec_lapses']+'''</font></para>''', styles["BodyText"])
    row23b = [row23a_01,row23a_02,row23a_11,row23a_12]
    data3.append(row23b)
    row23b_01 = Paragraph('''<para align=right><font size='11'>b)</font></para>''', styles["BodyText"])
    row23b_02 = Paragraph('''<para align=left><font size='11'>Lapses if any not observed.</font></para>''', styles["BodyText"])
    if not insepction_num:
        row23b_11 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row23b_12 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row23b_11 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row23b_12 = Paragraph('''<para align=left><font size='11'>'''+insepction_num[0]['nob_inspec_lapses']+'''</font></para>''', styles["BodyText"])
    row23b = [row23b_01,row23b_02,row23b_11,row23b_12]
    data3.append(row23b)
    row24_11 = Paragraph('''<para align=left><font size='11'>xxiv)</font></para>''', styles["BodyText"])
    row24_12 = Paragraph('''<para align=left><font size='11'>Name of Branch Head and Sales Officer (if any) at the time of sanction of the advance :</font></para>''', styles["BodyText"])
    if not ad_sanc_bo:
        row24_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row24_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row24_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row24_14 = Paragraph('''<para align=left><font size='11'></font>'''+ad_sanc_bo[0]['ad_sanc_bo_name'] + '('+ad_sanc_bo[0]['ad_sanc_bo_id']+')'+'''</para>''', styles["BodyText"])
    row24 = [row24_11,row24_12,row24_13,row24_14]
    data3.append(row24)
    row25_11 = Paragraph('''<para align=left><font size='11'>xxv)</font></para>''', styles["BodyText"])
    row25_12 = Paragraph('''<para align=left><font size='11'>Names of Branch Head thereafter till now.</font></para>''', styles["BodyText"])

    # Iterate over bo_names and create paragraphs
    row25_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    if not bo_names:
        row25_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        # Create a string with all names and IDs
        bo_names_str = '<br/>'.join([f"{name['bo_till_date_name']} ({name['bo_till_date_id']})" for name in bo_names])
        row25_14 = Paragraph(f'''<para align=left><font size='11'>{bo_names_str}</font></para>''', styles["BodyText"])

    row25 = [row25_11, row25_12, row25_13, row25_14]
    data3.append(row25)
    row26_11 = Paragraph('''<para align=left><font size='11'>xxvi)</font></para>''', styles["BodyText"])
    row26_12 = Paragraph('''<para align=left><font size='11'>Name of the Sanctioning office and Sanctioning Authority.</font></para>''', styles["BodyText"])
    if not so_sa_name:
        row26_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row26_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row26_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row26_14 = Paragraph('''<para align=left><font size='11'></font>'''+so_sa_name[0]['so_sa_name_name'] + '('+so_sa_name[0]['so_sa_name_id']+')'+'''</para>''', styles["BodyText"])
    row26 = [row26_11,row26_12,row26_13,row26_14]
    data3.append(row26)
    row27_11 = Paragraph('''<para align=left><font size='11'>xxvii)</font></para>''', styles["BodyText"])
    row27_12 = Paragraph('''<para align=left><font size='11'>Any other observations / information.</font></para>''', styles["BodyText"])
    if not other_info:
        row27_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        row27_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row27_13 = Paragraph('''<para align=left><font size='11'>'''+other_info[0]['other_info_dd']+'''</font></para>''', styles["BodyText"])
        row27_14 = Paragraph('''<para align=left><font size='11'>'''+other_info[0]['other_info_details']['other_info_remarks']+'''</font></para>''', styles["BodyText"])
    row27 = [row27_11,row27_12,row27_13,row27_14]
    data3.append(row27)
    row28_11 = Paragraph('''<para align=left><font size='11'>xxviii)</font></para>''', styles["BodyText"])
    row28_12 = Paragraph('''<para align="left"><font size="11">Name of the official(s) whose lapses have been observed.</font></para>''', styles["BodyText"])
    row28 = [row28_11,row28_12]
    data3.append(row28)
    t3 = Table(data3)
    table_style3 = [ 
                ('TEXTCOLOR', (0, 4), (-1, 6), colors.red),  # Red text for specific rows
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text to the left of the cell
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Set font
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Set font size
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke)  # Background color
                ]
    t3.setStyle(TableStyle(table_style3))
    total_width3 = 780  # Total available width in points
    first_column_width = 40
    remaining_width = total_width3 - first_column_width
    column_width3 = remaining_width / 3
    t3._argW = [first_column_width, column_width3, first_column_width,column_width3]
    Story.append(t3)
    data4 = []
    row27_11 = Paragraph('''<para align=left><font size='11'>Staff No.</font></para>''', styles["BodyText"])
    row27_12 = Paragraph('''<para align=left><font size='11'>Staff Name</font></para>''', styles["BodyText"])
    row27_13 = Paragraph('''<para align=left><font size='11'></font>Designation (at Branch/Sanctioning Office/Monitoring Office)
                            </para>''', styles["BodyText"])
    row27_14 = Paragraph('''<para align=left><font size='11'>If he/she is attaining the age of superannuation within next 1 year period, mention specifically.</font></para>''', styles["BodyText"])
    row27 = [row27_11,row27_12,row27_13,row27_14]
    data4.append(row27)
    if staff_data:
        for staff in staff_data:
            row = [
                Paragraph(f'''<para align=left><font size='11'>{staff["sd_staff_no"]}</font></para>''', styles["BodyText"]),
                Paragraph(f'''<para align=left><font size='11'>{staff["sd_staff_name"]}</font></para>''', styles["BodyText"]),
                Paragraph(f'''<para align=left><font size='11'>{staff["sd_designation"]}</font></para>''', styles["BodyText"]),
                Paragraph(f'''<para align=left><font size='11'>{staff["is_age_of_superannuation_within_nextyear_period"]}</font></para>''', styles["BodyText"])
            ]
            data4.append(row)

    t4 = Table(data4)
    table_style3 = [ 
                ('TEXTCOLOR', (0, 4), (-1, 6), colors.red),  # Red text for specific rows
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text to the left of the cell
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Set font
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Set font size
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke)  # Background color
                ]
    t4.setStyle(TableStyle(table_style3))
    total_width3 = 700  # Total available width in points
    first_column_width = 80
    remaining_width = total_width3 - first_column_width
    column_width3 = remaining_width / 3
    t4._argW = [first_column_width, first_column_width, column_width3,column_width3]
    Story.append(t4)

    obsv = []
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    obsv.append('')     
    SHP = Paragraph('''<para align=left><font size='11'><b>8.Observations of Branch Head : </b>'''+ psc_data[0]['ob_branch_head'] +'''</font></para>''', styles["BodyText"])
    subheadingP = [SHP]
    obsv.append(subheadingP)      
    obsv.append('')     
    r2c1 = Paragraph('''<para align=left><font size='11'><b>9.Observations of the Regional Head : </b>'''+ psc_data[0]['ob_regional_head'] +'''</font></para>''', styles["BodyText"])
    row2 = [r2c1] 
    obsv.append(row2)      
    obsv.append('')        
    r3c1 = Paragraph('''<para align=left><font size='11'><b>10.Observations of Department Head : </b>'''+ psc_data[0]['ob_dept_head'] +'''</font></para>''', styles["BodyText"])
    row3 = [r3c1] 
    obsv.append(row3)  
    tobsv = Table(obsv)
    table_style2 = [ 
                ('ALIGN',(0,0),(-1,-1),'LEFT')
                ]
    tobsv.setStyle(TableStyle(table_style2))
    total_width2 = 580  # Total available width in points
    column_width2 = total_width2 
    tobsv._argW = [column_width2] 
    Story.append(tobsv)
    doc.build(Story)
    buffer.seek(0)
    if merge_condition == "no":
        # return FileResponse(buffer, as_attachment=True, filename=f'{psc_data[0]["psc_rec_id"]}_form.pdf')
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{psc_data[0]["psc_rec_id"]}_form.pdf"'
        response.write(buffer.getvalue())
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Export","PSC review export to pdf completed"))
        return response
    # 
    elif merge_condition == "yes":
        try:
        # above 8 line to be commented after PyPDF upgradation
            end_psc = time.time()
            # print('**********time taken to end psc',end_psc-start_time)
            start_convert = time.time()
            documents = DocumentTable.objects.filter(review_id = psc_data[0]['psc_rec_id']).values('review_id','section','file_type','file_name','file','section')
            psc_folder_path = os.path.join(settings.MEDIA_ROOT, "PSC",psc_data[0]['psc_rec_id'])
            os.makedirs(psc_folder_path, exist_ok=True)
            for fil in documents:
                file_name_with_extension = f"{fil['review_id']}__{fil['section']}.pdf"  # Assuming the file_name is without an extension
                file_path = os.path.join(psc_folder_path, file_name_with_extension)
                #print('file_path',file_path)
                
                save_base64_image_as_pdf(fil['file'],file_path,fil['file_type'])

            end_convert = time.time()
            print('**********time taken for convertion btw psc',end_convert-start_convert)
        
            buffer.seek(0)
            start_merge = time.time()
            file_name_with_extension = f"1_{psc_data[0]['psc_rec_id']+'form'}.pdf"  # Assuming the file_name is without an extension
            
            file_pathform1 = os.path.join(psc_folder_path,file_name_with_extension)
            with open(file_pathform1, 'wb') as f:
                f.write(buffer.getvalue())
            folderpath = os.path.join(psc_folder_path)
            merged_buffer = pdf_merge(psc_data[0]['psc_rec_id'], psc_folder_path)
            end_merge = time.time() 
            print('**********time taken for merge psc',end_merge-start_merge)
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "PSC Review Export","PSC review export to pdf completed with file uploads"))
            return FileResponse(merged_buffer, as_attachment=True, filename=f"{psc_data[0]['psc_rec_id']}_form.pdf")
        # response = HttpResponse(merged_buffer, content_type='application/pdf')
        # response['Content-Disposition'] = f'inline; filename="{psc_data[0]["psc_rec_id"]}_form.pdf"'
        # return response

        except Exception as e:
            # print(e)
            sc_log.error('PSC review export error: ' + e)
            # print('PSC review export error: ' + e)
            return HttpResponse(e)

        finally:
            # Clean up the folder and files
            if os.path.exists(psc_folder_path):
                try:
                    shutil.rmtree(psc_folder_path)
                except OSError as e:
                    sc_log.error('Error deleting directory : ' + e)
                    print(f"Error deleting directory {psc_folder_path}: {e}")

@my_login_required
def sac_review_export(request, pk, merge_condition):
    start_time = time.time()
    config_data = Box(request.session['config_data'])
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    static_url = settings.base.STATIC_ROOT
    static_url = str(static_url).replace('\\', '/')
    logo_path = str(static_url)+'/assets/images/'+str(tenant)+'/'+str(tenant_image)
    sac_data = (SACTable.objects.filter(id=pk).values(*sac_all_data).order_by('mom_id'))
    cust_idsac = CustomerTable.objects.filter(npa_status=True,cust_id=sac_data[0]['psc_rec_id__cust_id']).values('id')[0]['id']
    credit_datasac = CreditFacilityTable.objects.filter(psc_id=cust_idsac).values(*creditsanction_all_data)   
    
    # security_datasac = SecuritiesTable.objects.filter(psc_id=cust_idsac).values(*securities_all_data)    
    psc__id = sac_data[0]['psc_rec_id']
    psc__i = sac_data[0]['psc_rec_id__cust_id']
    psc__cid = CustomerTable.objects.filter(cust_id=psc__i).values('id')[0]['id']
    sac_data_updated =  CustomerTable.objects.filter(cust_id=psc__i).values('lapses_details')[0]['lapses_details'] 
    
    # mom_lapses_data = PSCTable.objects.filter(id=sac_data[0]['psc_rec_id']).values('mom_lapse_desc')[0]['mom_lapse_desc'] 

    mom_lapses_data = sac_data_updated["records"][0]['staff_lapses_details']
    # print("mom_lapses_data",mom_lapses_data)
    lapses_data = sac_data[0]['lapses_data']
    #print(lapses_data)
    # lapses_branch = lapses_data['lapses_branch']
    fraud_element = lapses_data['fraud_element']
    addr_lett_date = lapses_data['addr_lett_date']
    reply_date = lapses_data['reply_date']
    rep_auth_remarks = lapses_data['rep_auth_remarks']
    
    def process_accountability_data(key_dd, key):
        data = lapses_data.get(key, [])
        condition = data[0].get(f"{key_dd}") if data else None
        if condition:
            return data
        else:
            return []
    fraud_element = process_accountability_data('fraud_element_dd', 'fraud_element')
    reply_date = process_accountability_data('reply_date_dd', 'reply_date')
    reject_remarks = sac_data[0]['reject_remarks']
    buffer = io.BytesIO()
    # pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=25, leftMargin=25, topMargin=18, bottomMargin=18)
    doc = SimpleDocTemplate(buffer, pagesize=(A4), rightMargin=5, leftMargin=5, topMargin=18, bottomMargin=3)
    Story=[]
    im = Image(logo_path, 1.5 * inch, 0.5 * inch)
    im.hAlign = 'LEFT'
    Story.append(im)
    Story.append(Spacer(1, 12))  # Adjust the height (second parameter) as needed
    data1 = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    H1 = Paragraph('''<para align=center><font size='13'><b><u>STAFF ACCOUNTABILITY COMMITTEE – I or II </u></b></font></para>''', styles["BodyText"])
    heading1 = [H1]
    data1.append(heading1)
    data1.append('')
    SH1 = Paragraph('''<para align=left><font size='11'><b>(i) Basic Details</b></font></para>''', styles["BodyText"])
    subheading1 = [SH1]
    data1.append(subheading1)

    r3c1 = Paragraph('''<para align=left><font size='10'>SAC No : '''+ sac_data[0]['sac_rec_id'] +'''</font></para>''', styles["BodyText"])
    r3c2 = Paragraph('''<para align=center><font size='10'>Name of the Executive : '''+sac_data[0]['emp_name']+'''</font></para>''', styles["BodyText"])
    r3c3 = Paragraph('''<para align=right><font size='10'>Staff No. : '''+sac_data[0]['staff_no']+'''</font></para>''', styles["BodyText"])
    row3 = [r3c1, r3c2, r3c3]
    data1.append(row3)

    r4c1 = Paragraph('''<para align=left><font size='10'>Present Designation : '''+ sac_data[0]['present_designation'] +'''</font></para>''', styles["BodyText"])
    r4c2 = Paragraph('''<para align=center><font size='10'>Present place of working : '''+sac_data[0]['present_working']+'''</font></para>''', styles["BodyText"])
    r4c3 = Paragraph('''<para align=right><font size='10'>PSC No. : '''+str(sac_data[0]['psc_rec_id__psc_rec_id'])+'''</font></para>''', styles["BodyText"])
    row4 = [r4c1, r4c2, r4c3]
    data1.append(row4)

    r5c1 = Paragraph('''<para align=left><font size='10'>PSC Date : '''+sac_data[0]['psc_rec_id__form_creation_date'].strftime('%d-%m-%Y')+'''</font></para>''', styles["BodyText"])
    row5 = [r5c1]
    data1.append(row5)

    data1.append('')

    SH2 = Paragraph('''<para align=left><font size='11'><b>(ii) Name of the branch / Office wherein the lapses have been observed :</b></font></para>''', styles["BodyText"])
    r6c1 = Paragraph('''<para align=left><font size='10'>'''+str(sac_data[0]['lapses_data']['lapses_branch'])+'''</font></para>''', styles["BodyText"])
    row6 = [SH2, '', r6c1]  # Empty string for the second column to span
    data1.append(row6)

    t1 = Table(data1)
    table_style1 = [
        ('SPAN', (0, 0), (2, 0)),  # Span the heading across all three columns
        ('SPAN', (0, len(data1) - 1), (1, len(data1) - 1)),  # Span SH2 across the first two columns
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ]
    t1.setStyle(TableStyle(table_style1))

    total_width1 = 580  # Total available width in points
    column_width1 = total_width1 / 3
    t1._argW = [column_width1] * 3
    Story.append(t1)

    Story.append(Spacer(1, 10))  # Spacer between the two tables

    Story.append(Spacer(1,6))
    SHC = Paragraph('''<para align=left><font size='11'><b>(iii) Particulars of account (s)</b></font></para>''', styles["BodyText"])
    Story.append(SHC)
    Story.append(Spacer(1,3))
    
    cs_table_data = [['Sl. NO.',	'SRN',	'Date of Release',	'Nature of Account',	'Nature of Advance',	'LAN',	'Sanction Amount',	'Due Date',	'NPA Date',	'Present Balance',	'Current Balance',	'Purpose of Advance',	'Asset Classification', 'Document Date']]
    cs_table = Table(cs_table_data)
    
    for cs in credit_datasac:
        cs_row = [
            cs['credit_feci_slno'] or '-',
            cs['reference_num'] or '-',
            cs['sanction_date'].strftime('%d-%m-%Y') if cs['sanction_date'] else '-',
            cs['account_nature'] or '-',
            cs['advance_nature'] or '-',
            cs['lan'] or '-',
            cs['sanctioned_limit'],
            cs['due_date'].strftime('%d-%m-%Y') if cs['due_date'] else '-',
            cs['npa_date'].strftime('%d-%m-%Y') if cs['npa_date'] else '-',
            cs['npa_balance'] or '-',
            cs['balance'] or '-',
            cs['advance_purpose'] or '-',
            cs['asset_classification'] or '-',
            cs['doc_date'].strftime('%d-%m-%Y') if cs['doc_date'] else '-'
        ]
        cs_table_data.append(cs_row)
    
    cs_table = Table(cs_table_data)
    cs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            # ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 5),  # Set font size
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
    ]))

    Story.append(cs_table)
    Story.append(Spacer(1, 10))

    data3 = []

    r0c1 = Paragraph('''<para align=left><font size='11'>iv)</font></para>''', styles["BodyText"])
    r0c2 = Paragraph('''<para align=left><font size='11'>Whether the cases involve an element of fraud/connotation of fraud ?*	</font></para>''', styles["BodyText"])
    row0 = [r0c1,r0c2]
    five_line_style = ParagraphStyle(
        name="FiveLines",
        fontSize=10,
        leading=12
    )

    if mom_lapses_data:
        # Create the AOD table header
        table_data = [['Facility', 'Head', 'Lapses']]
        
        for index, aod in enumerate(mom_lapses_data, start=1):
            borrowerAODDates1 = aod['acc_no']
            borrowerAODDates2 = aod['emp_code']
            borrowerAODDates3 = aod['lapses_observed']
            lapses_paragraph_truncated = shorten(borrowerAODDates3, width=300, placeholder='....')
            lapses_para = Paragraph(lapses_paragraph_truncated, five_line_style)
            
            # Create Paragraph objects to ensure text wraps within table cells
            facilityno_paragraph = Paragraph(borrowerAODDates1, styles["BodyText"])
            branch_head_paragraph = Paragraph(borrowerAODDates2, styles["BodyText"])
            lapses_paragraph = Paragraph(borrowerAODDates3, styles["BodyText"])
            
            table_data.append([facilityno_paragraph, branch_head_paragraph, lapses_para])

        # Create the table
        table = Table(table_data, colWidths=[50, 40, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-2), 10),
            ('LEADING',(0,0),(-1,-1),12),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Add the table to the data3 list
        # row0.append("")
        row0.append([table])
    data3.append(row0)
    r1c1 = Paragraph('''<para align=left><font size='11'>v)</font></para>''', styles["BodyText"])
    r1c2 = Paragraph('''<para align=left><font size='11'>Whether the cases involve an element of fraud/connotation of fraud ?*	</font></para>''', styles["BodyText"])
    if not fraud_element:
        r1c3 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        r1c4 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        r1c3 = Paragraph('''<para align=left><font size='11'>'''+fraud_element[0]['fraud_element_dd']+'''</font></para>''', styles["BodyText"])
        r1c4 = Paragraph('''<para align=left><font size='11'>'''+fraud_element[0]['fraud_element_remarks']+'''</font></para>''', styles["BodyText"])
    row1 = [r1c1,r1c2,r1c3,r1c4]
    data3.append(row1)
    r2c1 = Paragraph('''<para align=left><font size='11'>vi)</font></para>''', styles["BodyText"])
    r2c2 = Paragraph('''<para align=left><font size='11'>Date of the letter addressed to the employee / Executive as required under Staff Accountability Policy. (Enclose a copy)</font></para>''', styles["BodyText"])
    if not addr_lett_date:
        r2c3 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        r2c4 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        r2c3 = Paragraph('''<para align=left><font size='11'>'''+addr_lett_date+'''</font></para>''', styles["BodyText"])
        r2c4 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    row2 = [r2c1,r2c2,r2c3,""]
    data3.append(row2)
    r3c1 = Paragraph('''<para align=left><font size='11'>vii)</font></para>''', styles["BodyText"])
    r3c2 = Paragraph('''<para align=left><font size='11'>Date of reply, if any received from the employee / Executive (Enclose a copy)</font></para>''', styles["BodyText"])
    if not reply_date:
        r3c3 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        r3c4 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        r3c3 = Paragraph('''<para align=left><font size='11'>'''+reply_date[0]['reply_date_dd']+'''</font></para>''', styles["BodyText"])
        r3c4 = Paragraph('''<para align=left><font size='11'>'''+reply_date[0]['reply_date_dt']+'''</font></para>''', styles["BodyText"])
    row3 = [r3c1,r3c2,r3c3,r3c4]
    data3.append(row3)
    row4_11 = Paragraph('''<para align=left><font size='11'>viii)</font></para>''', styles["BodyText"])
    row4_12 = Paragraph('''<para align=left><font size='11'>Views of the reporting authority.</font></para>''', styles["BodyText"])
    if not rep_auth_remarks:
        row4_13 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
        # row4_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    else:
        row4_13 = Paragraph('''<para align=left><font size='11'>'''+rep_auth_remarks+'''ss</font></para>''', styles["BodyText"])
        
        # row4_14 = Paragraph('''<para align=left><font size='11'></font></para>''', styles["BodyText"])
    row4 = [row4_11,row4_12,row4_13,""]
    data3.append(row4)
    
    t3 = Table(data3)
    table_style3 = [ 
                ('SPAN', (3, 0), (2, 0)),
                ('SPAN', (3, 2), (2, 2)),
                ('SPAN', (3, 4), (2, 4)),
                ('TEXTCOLOR', (0, 4), (-1, 6), colors.red),  # Red text for specific rows
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text to the left of the cell
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Set font
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Set font size
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke)  # Background color
                ]
    t3.setStyle(TableStyle(table_style3))
    total_width3 = 720  # Total available width in points
    first_column_width = 30
    third_column_width = 70
    remaining_width = total_width3 - first_column_width
    column_width3 = remaining_width / 3
    t3._argW = [first_column_width, column_width3, third_column_width,column_width3]
    Story.append(t3)
    obsv = []
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    obsv.append('')     
    r2c1 = Paragraph('''<para align=left><font size='11'><b>(ix) Observations of the Regional Head : </b>'''+ sac_data[0]['ob_regional_head'] +'''</font></para>''', styles["BodyText"])
    row2 = [r2c1] 
    obsv.append(row2)      
    obsv.append('')        
    r3c1 = Paragraph('''<para align=left><font size='11'><b>(x) Observations of Department Head : </b>'''+ sac_data[0]['ob_dept_head'] +'''</font></para>''', styles["BodyText"])
    row3 = [r3c1] 
    obsv.append(row3)  
    tobsv = Table(obsv)
    table_style2 = [ 
                ('ALIGN',(0,0),(-1,-1),'LEFT')
                ]
    tobsv.setStyle(TableStyle(table_style2))
    total_width2 = 580  # Total available width in points
    column_width2 = total_width2 
    tobsv._argW = [column_width2] 
    Story.append(tobsv)
    if merge_condition == 'no':
        doc.build(Story)
        end_sac = time.time()
        print('**********time taken for sac form',end_sac-start_time)
        buffer.seek(0)
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review Export","SAC review export to pdf completed"))
        # return FileResponse(buffer, as_attachment=True, filename=f"{sac_data[0]['sac_rec_id']}_form.pdf")
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{sac_data[0]["sac_rec_id"]}_form.pdf"'
        response.write(buffer.getvalue())
        return response
    else:
        try:
        # above 8 line to be commented after PyPDF upgradation
            start_convert = time.time()
            # Define file path for PDF output
            # Change to your desired file name and extension
            documents = DocumentTable.objects.filter(review_id = sac_data[0]['sac_rec_id']).values('review_id','section','file_type','file_name','file','section')
            sac_folder_path = os.path.join(settings.MEDIA_ROOT, "SAC",sac_data[0]['sac_rec_id'])
            os.makedirs(sac_folder_path, exist_ok=True)
            for fil in documents:
                sac_name_with_extension = f"{fil['review_id']}__{fil['section']}.pdf"  # Assuming the file_name is without an extension
                file_path = os.path.join(sac_folder_path, sac_name_with_extension)
                print('file_path',file_path)
                
                save_base64_image_as_pdf(fil['file'],file_path,fil['file_type'])
                
            
            end_convert = time.time()
            print('**********time taken for sac convert pdf',end_convert-start_convert)       
            doc.build(Story)
            start_merge = time.time()
            buffer.seek(0)
            file_name_with_extension = f"1_{sac_data[0]['sac_rec_id']+'form'}.pdf"  # Assuming the file_name is without an extension
            file_pathform = os.path.join(sac_folder_path, file_name_with_extension)
            with open(file_pathform, 'wb') as f:
                f.write(buffer.getvalue())
            folderpath = os.path.join(sac_folder_path)
            merged_buffer = pdf_merge(sac_data[0]['sac_rec_id'], sac_folder_path)
            end_merge = time.time()
            print('**********time taken for sac merge pdf',end_merge-start_merge)
            print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "SAC Review Export","SAC review export to pdf completed with file uploads"))
            # return FileResponse(merged_buffer, as_attachment=True, filename=f"{sac_data[0]['sac_rec_id']}_form.pdf")
            # Return the merged PDF as a response
            response = HttpResponse(merged_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{sac_data[0]["sac_rec_id"]}_form.pdf"'
            return response
        except Exception as e:
                # print(e)
                sc_log.error('SAC review export error: ' + e)
                # print('SAC review export error: ' + str(e))
                return HttpResponse(e)

        finally:
            # Clean up the folder and files
            if os.path.exists(sac_folder_path):
                try:
                    shutil.rmtree(sac_folder_path)
                except OSError as e:
                    sc_log.error('Error deleting directory  error: ' + str(e))
                    # print(f"Error deleting directory {sac_folder_path}: {e}")

@my_login_required
def mom_lapse_export(request, pk, preps):
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    # Fetch MOM data
    config_data = Box(request.session['config_data'])
    psc_mom_limit = config_data.module.PSC001.psc_mom_limit
    roles = request.session['new_roles'].split("_")
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    static_url = settings.base.STATIC_ROOT
    static_url = str(static_url).replace('\\', '/')
    logo_path = str(static_url)+'/assets/images/'+str(tenant)+'/'+str(tenant_image)
    try:
        mom_data = (MOMTable.objects.filter(id=pk).values('meeting_id', 'mom_creation_date__date', 'mom_date__date', 'audience', 'loan_count', 'active', 'review_type'))
        review = MOMTable.objects.filter(id=pk).values('review_type')[0]['review_type']
        mom_from_date, mom_to_date = mom_date_fetch(request, pk)
        mom_total_count(request, pk, review)
        mom_to_date = mom_to_date
        cust_ids = PSCTable.objects.filter(
                Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date)) | 
                Q(npa_status=True, mom_id=pk)
            ).values_list('cust_id', flat=True).distinct()
        if review == 'PSC1':
                psc_data = []
                for cust_id in cust_ids:
                    total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values_list('total_exposure', flat=True).first()
                    if total_exposure and float(total_exposure) < psc_mom_limit:
                        psc_data += list(
                            PSCTable.objects.filter(
                                (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                                (Q(npa_status=True, mom_id=pk)),
                                cust_id=cust_id
                            ).values(*psc_all_data).order_by('last_modified_date')
                        )
            
        elif review == 'PSC2':
            psc_data = []
            for cust_id in cust_ids:
                
                total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values('total_exposure').first()
                #print('total_exposure',total_exposure['total_exposure'])
                if total_exposure and float(total_exposure['total_exposure']) >= psc_mom_limit:
                    #print('in psc2 if',psc_data)
                    psc_data += list(
                        PSCTable.objects.filter(
                            (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                            (Q(npa_status=True, mom_id=pk)),
                            cust_id=cust_id
                        ).values(*psc_all_data).order_by('last_modified_date')
                    )

        elif review == 'sac':
            sac_data = list(
                SACTable.objects.filter(
                    (Q(psc_rec_id__npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                    (Q(psc_rec_id__npa_status=True, mom_id=pk))
                ).values(*sac_all_data).order_by('last_modified_date')
            )
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=(A4), rightMargin=5, leftMargin=5, topMargin=18, bottomMargin=18)
        Story=[]
        data = []
        im = Image(logo_path, 1.5 * inch, 0.5 * inch)
        im.hAlign = 'LEFT'
        Story.append(im)
        Story.append(Spacer(1, 12))  # Adjust the height (second parameter) as needed
        styles=getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        data.append('')
        r1c1 = Paragraph('''<para align=left><font size='10'><b>Meeting No. : ''' + mom_data[0]['meeting_id'] + '''</b></font></para>''', styles["BodyText"])
        r1c2 = Paragraph('''<para align=right><font size='10'><b>Date : ''' + mom_data[0]['mom_creation_date__date'].strftime('%d-%m-%Y') + '''</b></font></para>''', styles["BodyText"])
        row1 = [r1c1, r1c2]
        data.append(row1)
        data.append('')
        if review == 'PSC2' or review == 'PSC1' :
            H1 = Paragraph('''<para align=center><font size='12'><b><u>Minutes of the meeting of the PRELIMINARY SCREENING COMMITTEE - held on ''' + mom_data[0]['mom_date__date'].strftime('%d-%m-%Y') + '''</u></b></font></para>''',styles["BodyText"])
        elif review == 'sac':
            H1 = Paragraph('''<para align=center><font size='12'><b><u>Minutes of the meeting of the STAFF ACCOUNTABILITY COMMITTEE - held on ''' + mom_data[0]['mom_date__date'].strftime('%d-%m-%Y') + '''</u></b></font></para>''',styles["BodyText"])
        heading1 = [H1,"", "", "","", ""]
        data.append(heading1)
        data.append('')
        H2 = Paragraph('''<para align=left><font size='12'><b>Present:</b></font></para>''',styles["BodyText"])
        heading2 = [H2,"", "", "","", ""]
        data.append(heading2)
        mom_audience = MOMTable.objects.filter(id=pk).values('audience')[0]['audience']
        max_columns = 6
        rows_needed = (len(mom_audience) // max_columns) + 1 if len(mom_audience) % max_columns != 0 else len(mom_audience) // max_columns

        for i in range(rows_needed):
            row_data = mom_audience[i * max_columns:(i + 1) * max_columns]
            row = []
            for record_data in row_data:
                record_info = f"{record_data['staffName']} <br/>" \
                            f"{record_data['staffNo']}<br/>" \
                            f"{record_data['designation']}<br/>" \
                            f"{record_data['role']}"
                r5c1 = Paragraph(f'''<para align=left><font size='10'><b>{record_info}</b></font></para>''', styles["BodyText"])
                row.append(r5c1)
            
            while len(row) < max_columns:
                row.append('')
            
            data.append(row)
        t = Table(data)
        table_style = [
                    # ('GRID',(0,0),(-1,-1),0.2,colors.white),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),  
                    ('SPAN', (0, 0), (5, 0)),
                    ('SPAN', (0, 1), (4, 1)),  #1st row
                    ('SPAN', (1, 1), (5, 1)),  #2nd row
                    ('SPAN', (0, 2), (5, 2)),  #2nd row
                    ('SPAN', (0, 3), (5, 3)),  #3nd row
                    ('SPAN', (0, 4), (5, 4)),  #4nd row
                    ('SPAN', (0, 5), (5, 5)),  #4nd row
                    
                    ('ALIGN',(0,0),(-1,-1),'CENTER')
                ]
        
    
        t.setStyle(TableStyle(table_style))

        # Set the width of each column
        total_width = 550  # Total available width in points
        column_width = total_width / 6
        t._argW = [column_width] * 6
        
        Story.append(t)

        Story.append(Spacer(1, 24))  # Spacer between the two tables
        if review == 'PSC2' or review == 'PSC1' :

            psc_table_data = [
                        ['PSC Srl No.', 'Branch', 'Region', 'Customer ID', 'Facility No.', 'Borrower', 'NPA Date', 'NPA Tag', 'PSC Status', 'Current Role', 'Lapse']
                    ]
            if not psc_data:
                psc_table_data.append(['No data'] + [''] * 10)  # 'No data' in the first cell, rest are empty to match column count
                
                psc_table = Table(psc_table_data)
                psc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('FONTSIZE', (0, 0), (-1, -1), 8.2),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('SPAN', (0, 1), (-1, 1))  # Span the 'No data' cell across all columns
                ]))
            else:
                for psc in psc_data:
                    #print('psc_data',psc_data)
                    psc_row = [
                        psc['psc_rec_id'] or '-',
                        psc['branch_code_id__branch_code'] or '-',
                        psc['region_name'] or '-',
                        psc['cust_id'] or '-',
                        psc['facility_num'] or '-',
                        psc['borrower_name'] or '-',
                        psc['npa_date__date'].strftime('%d-%m-%Y') if psc['npa_date__date'] else '-',
                        psc['nap_tag'] or '-',
                        psc['status'] or '-',
                        psc['current_role'] or '-',
                        psc['mom_lapse'] or '-'
                    ]
                    psc_table_data.append(psc_row)
                
                
                psc_table = Table(psc_table_data)
                psc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('FONTSIZE', (0, 0), (-1, -1), 5.9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
                ]))

            Story.append(psc_table)
        
        elif review == 'sac':
            sac_table_data = [
                        ['SAC Srl No.', 'Branch', 'Region', 'Customer ID', 'Facility No.', 'Borrower', 'NPA Date', 'NPA Tag', 'SAC Status', 'Current Role', 'Lapse']
                    ]
            if not sac_data:
                sac_table_data.append(['No data'] + [''] * 10)  # 'No data' in the first cell, rest are empty to match column count
                
                sac_table = Table(sac_table_data)
                sac_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('FONTSIZE', (0, 0), (-1, -1), 8.2),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('SPAN', (0, 1), (-1, 1))  # Span the 'No data' cell across all columns
                ]))
            else:
                for sac in sac_data:
                    sac_row = [
                        sac['sac_rec_id'], sac['psc_rec_id__branch_code_id__branch_code'], sac['psc_rec_id__region_name'], sac['psc_rec_id__cust_id'],
                        sac['psc_rec_id__facility_num'], sac['psc_rec_id__borrower_name'], sac['psc_rec_id__npa_date__date'].strftime('%d-%m-%Y'),
                        sac['psc_rec_id__nap_tag'], sac['status'], sac['current_role'], sac['mom_lapse']
                    ]
                    sac_table_data.append(sac_row)

                sac_table = Table(sac_table_data)
                sac_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('FONTSIZE', (0, 0), (-1, -1), 5.9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
                ]))
            Story.append(sac_table)
        doc.build(Story)
        writer = PdfWriter()
        buffer.seek(0)
        reader = PdfReader(buffer)
        for page in reader.pages:
            writer.add_page(page)
        # writer.add_pages(PdfReader(buffer).pages)
        # print('preps',preps)
        if preps == 'after':
            if review == 'PSC2' or review == 'PSC1' :
                psc_moms_yes = PSCTable.objects.filter(mom_id = pk, mom_lapse='yes').values('psc_rec_id','id')
                for p_id in psc_moms_yes:
                    # print('psc_moms_yes',p_id['psc_rec_id'],p_id['id'])
                    review_response = mom_review_export(request, p_id['id'], pk)
                    review_buffer = BytesIO(review_response.content)
                    review_reader = PdfReader(review_buffer)
                    
                    # Add pages from the review PDF to the writer
                    for page in review_reader.pages:
                        writer.add_page(page)
            elif review == 'sac':
                sac_moms_yes = SACTable.objects.filter(mom_id = pk, mom_lapse='yes').values('sac_rec_id','id')
                # print('sac_moms_yes',sac_moms_yes)
                for p_id in sac_moms_yes:
                    #print('sac_moms_yes',p_id['sac_rec_id'],p_id['id'])
                    review_response = mom_review_export(request, p_id['id'], pk)
                    review_buffer = BytesIO(review_response.content)
                    review_reader = PdfReader(review_buffer)
                    
                    # Add pages from the review PDF to the writer
                    for page in review_reader.pages:
                        writer.add_page(page)
            # pass
        elif preps == 'before':
            mom_from_date, mom_to_date = mom_date_fetch(request, pk)
            mom_total_count(request, pk, review)
            mom_to_date = mom_to_date
            cust_ids = PSCTable.objects.filter(
                    Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date)) | 
                    Q(npa_status=True, mom_id=pk)
                ).values_list('cust_id', flat=True).distinct()
            #print('review',review)
            if review == 'PSC1':
                    psc_moms_yes1 = []
                    for cust_id in cust_ids:
                        total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values_list('total_exposure', flat=True).first()
                        if total_exposure and float(total_exposure) < psc_mom_limit:
                            psc_moms_yes1 += list(
                                PSCTable.objects.filter(
                                    (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                                    (Q(npa_status=True, mom_id=pk)),
                                    cust_id=cust_id
                                ).values('psc_rec_id', 'id').order_by('last_modified_date')
                            )
                            #print('psc_moms_yes1',psc_moms_yes1)
                            # return
                            p1unique_records = {}
                            for record in psc_moms_yes1:
                                if record['psc_rec_id'] not in p1unique_records:
                                    p1unique_records[record['psc_rec_id']] = record
                            for p_id in p1unique_records.values():
                                # print('p_id',p_id)
                                review_response = psc_review_export(request, p_id['id'], 'no')
                                #print('before mom')
                                review_buffer = BytesIO(review_response.content)
                                review_reader = PdfReader(review_buffer)
                                
                                # Add pages from the review PDF to the writer
                                for page in review_reader.pages:
                                    writer.add_page(page)
                
            elif review == 'PSC2':
                # psc_moms_yes2 = []
                for cust_id in cust_ids:
                    
                    total_exposure = CustomerTable.objects.filter(npa_status=True,cust_id=cust_id).values('total_exposure').first()
                    #print('total_exposure',total_exposure['total_exposure'])
                    if total_exposure and float(total_exposure['total_exposure']) >= psc_mom_limit:
                        #print('in psc2 if',psc_data)
                        psc_moms_yes2 = list(
                            PSCTable.objects.filter(
                                (Q(npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                                (Q(npa_status=True, mom_id=pk)),
                                cust_id=cust_id
                            ).values('psc_rec_id','id').order_by('last_modified_date')
                        )
                        # print('psc_moms_yes1',psc_moms_yes2)
                        # return
                        p2unique_records = {}
                        for record in psc_moms_yes2:
                            if record['psc_rec_id'] not in p2unique_records:
                                p2unique_records[record['psc_rec_id']] = record

                        # Process the unique records
                        for p_id in p2unique_records.values():
                            #print('p_id', p_id)
                            review_response = psc_review_export(request, p_id['id'], 'no')
                            #print('before mom')
                            
                            review_buffer = BytesIO(review_response.content)
                            if not review_response.content.startswith(b'%PDF'):
                                print("Invalid PDF data")
                                continue

                            review_reader = PdfReader(review_buffer)

                            
                            # Add pages from the review PDF to the writer
                            for page in review_reader.pages:
                                writer.add_page(page)

            elif review == 'sac':
                #print('here')
                sac_moms_yes = SACTable.objects.filter(
                        (Q(psc_rec_id__npa_status=True, current_role='Convener', last_modified_date__range=(mom_from_date, mom_to_date))) | 
                        (Q(psc_rec_id__npa_status=True, mom_id=pk))
                    ).values('sac_rec_id','id').order_by('last_modified_date')
                #print(sac_moms_yes)
                sunique_records = {}
                for record in sac_moms_yes:
                    if record['sac_rec_id'] not in sunique_records:
                        sunique_records[record['sac_rec_id']] = record
                for p_id in sunique_records.values():
                    review_response = sac_review_export(request, p_id['id'], 'yes')
                    review_buffer = BytesIO(review_response.content)
                    review_reader = PdfReader(review_buffer)
                    
                    # Add pages from the review PDF to the writer
                    for page in review_reader.pages:
                        writer.add_page(page)
        else:
            return HttpResponse("Not selected any condition")
        final_buffer = BytesIO()
        writer.write(final_buffer)
        final_buffer.seek(0)
        print("User Id: {}, Designation: {}, Role: {}, Action: {}, Message: {}".format(request.session['emp_id'], request.session['designation'], session_role, "MOM Lapses Export","MOM Lapses export to pdf completed with file uploads"))
        # return FileResponse(final_buffer, as_attachment=True, filename='mom_lapses_export.pdf')
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="'+ review+'_mom_lapses_export.pdf"'
        response.write(final_buffer.getvalue())
        return response
    except Exception as e:
        print(e)
        sc_log.error('MOM lapses export error: ' + e)
        print('MOM lapses export error: ' + str(e))
        return redirect('mom_lapses')

@my_login_required
def mom_review_export(request, pk, m_id):
    session_role = DesignationMatrix.objects.filter(role_code=request.session['new_roles']).values('role_name')[0]['role_name']
    # Fetch MOM data
    config_data = Box(request.session['config_data'])
    tenant = config_data.tenant
    tenant_image = config_data.logo_image.image_path
    static_url = settings.base.STATIC_ROOT
    static_url = str(static_url).replace('\\', '/')
    logo_path = str(static_url)+'/assets/images/'+str(tenant)+'/'+str(tenant_image)
    try:
        mom_data = (MOMTable.objects.filter(id=m_id).values('meeting_id', 'mom_creation_date__date', 'mom_date__date', 'audience', 'loan_count', 'active', 'review_type'))
        review = MOMTable.objects.filter(id=m_id).values('review_type')[0]['review_type']
        
        psc_data = (PSCTable.objects.filter(id=pk).values('psc_rec_id', 'branch_code_id__branch_code', 'region_name', 'cust_id', 'borrower_name','facility_num', 'sanc_limit', 'npa_date__date', 'nap_tag', 'status', 'current_role', 'mom_lapse','mom_br_head','branch_code_id__branch_name','mom_lapse_desc').order_by('mom_id'))
        
        sac_data = (SACTable.objects.filter(id=pk).values('sac_rec_id', 'psc_rec_id__psc_rec_id','psc_rec_id__branch_code_id__branch_code','psc_rec_id__branch_code_id__branch_name', 'psc_rec_id__region_name', 'psc_rec_id__cust_id', 'psc_rec_id__borrower_name','psc_rec_id__facility_num', 'psc_rec_id__sanc_limit', 'psc_rec_id__npa_date__date', 'psc_rec_id__nap_tag', 'status', 'current_role', 'mom_lapse','id','creation_date','created_user','psc_rec_id','sac_rec_id','emp_name','staff_no','present_designation','present_working','status','psc_date','lapses_data','reject_remarks','ob_regional_head','ob_dept_head','mom_lapse','mom_lapse_desc','mom_br_head','mom_id','last_modified_date','last_modified_user','current_role','psc_rec_id__branch_code_id__branch_code','psc_rec_id__branch_code_id__branch_name','psc_rec_id__cust_id','psc_rec_id__borrower_name','psc_rec_id__facility_num','psc_rec_id__sanc_limit','psc_rec_id__region_name','psc_rec_id__npa_date','psc_rec_id__npa_date__date','psc_rec_id__nap_tag','psc_rec_id__psc_rec_id','psc_rec_id__form_creation_date').order_by('mom_id'))
        #print('mom exports merger',mom_data, review, sac_data)
        if review == 'PSC1' or review == 'PSC2':
            cust_idpsc = CustomerTable.objects.filter(npa_status=True,cust_id=psc_data[0]['cust_id']).values('id')[0]['id']
            credit_datapsc = CreditFacilityTable.objects.filter(psc_id=cust_idpsc).values('id', 'creation_date', 'created_user', 'credit_feci_slno', 'reference_num', 'sanction_date', 'account_nature', 'advance_nature', 'lan', 'sanctioned_limit', 'due_date', 'npa_balance', 'balance', 'advance_purpose', 'npa_date', 'asset_classification','doc_date')
        elif review == 'sac':
            cust_idsac = CustomerTable.objects.filter(npa_status=True,cust_id=sac_data[0]['psc_rec_id__cust_id']).values('id')[0]['id']
            credit_datasac = CreditFacilityTable.objects.filter(psc_id=cust_idsac).values('id', 'creation_date', 'created_user', 'credit_feci_slno', 'reference_num', 'sanction_date', 'account_nature', 'advance_nature', 'lan', 'sanctioned_limit', 'due_date', 'npa_balance', 'balance', 'advance_purpose', 'npa_date', 'asset_classification', 'doc_date')
        # print('mom_br_head',psc_data[0]['mom_br_head'][0]['psc_branch_head_name'])
        buffer = io.BytesIO()
        # pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=25, leftMargin=25, topMargin=18, bottomMargin=18)
        doc = SimpleDocTemplate(buffer, pagesize=(A4), rightMargin=5, leftMargin=5, topMargin=18, bottomMargin=3)
        Story=[]
        data = []
        im = Image(logo_path, 1.5 * inch, 0.5 * inch)
        im.hAlign = 'LEFT'
        Story.append(im)
        Story.append(Spacer(1, 12))  # Adjust the height (second parameter) as needed
        styles=getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        styNormal = styles["Justify"]
        data.append('')
        r1c1 = Paragraph('''<para align=left><font size='10'><b>Meeting No. : ''' + mom_data[0]['meeting_id'] + '''</b></font></para>''', styles["BodyText"])
        r1c2 = Paragraph('''<para align=right><font size='10'><b>Date : ''' + mom_data[0]['mom_creation_date__date'].strftime('%d-%m-%Y') + '''</b></font></para>''', styles["BodyText"])
        row1 = [r1c1, r1c2]
        data.append(row1)
        data.append('')
        if review == 'PSC2' or review == 'PSC1' :
            H1 = Paragraph('''<para align=center><font size='12'><b><u>Minutes of the meeting of the PRELIMINARY SCREENING COMMITTEE - held on ''' + mom_data[0]['mom_date__date'].strftime('%d-%m-%Y') + '''</u></b></font></para>''',styles["BodyText"])
        elif review == 'sac':
            H1 = Paragraph('''<para align=center><font size='12'><b><u>Minutes of the meeting of the STAFF ACCOUNTABILITY COMMITTEE - held on ''' + mom_data[0]['mom_date__date'].strftime('%d-%m-%Y') + '''</u></b></font></para>''',styles["BodyText"])
        heading1 = [H1,"", "", "","", ""]
        data.append(heading1)
        data.append('')
        H2 = Paragraph('''<para align=left><font size='12'><b>Present:</b></font></para>''',styles["BodyText"])
        heading2 = [H2,"", "", "","", ""]
        data.append(heading2)
        mom_audience = MOMTable.objects.filter(id=m_id).values('audience')[0]['audience']
        max_columns = 6
        rows_needed = (len(mom_audience) // max_columns) + 1 if len(mom_audience) % max_columns != 0 else len(mom_audience) // max_columns

        for i in range(rows_needed):
            row_data = mom_audience[i * max_columns:(i + 1) * max_columns]
            row = []
            for record_data in row_data:
                record_info = f"{record_data['staffName']} <br/>" \
                            f"{record_data['staffNo']}<br/>" \
                            f"{record_data['designation']}<br/>" \
                            f"{record_data['role']}"
                r5c1 = Paragraph(f'''<para align=left><font size='10'><b>{record_info}</b></font></para>''', styles["BodyText"])
                row.append(r5c1)

            while len(row) < max_columns:
                row.append('')
            
            data.append(row)
        data.append('')
        
        t = Table(data)
        table_style = [
                    # ('GRID',(0,0),(-1,-1),0.2,colors.black),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),  
                    ('SPAN', (0, 0), (5, 0)),
                    ('SPAN', (0, 1), (4, 1)),  #1st row
                    ('SPAN', (1, 1), (5, 1)),  #2nd row
                    ('SPAN', (0, 2), (5, 2)),  #2nd row
                    ('SPAN', (0, 3), (5, 3)),  #3nd row
                    ('SPAN', (0, 4), (5, 4)),  #4nd row
                    ('SPAN', (0, 5), (5, 5)),  #4nd row
                    ('SPAN', (2, 9), (3, 9)),  #2nd row
                    ('SPAN', (0, 10), (1, 10)),  #2nd row
                    ('SPAN', (3, 10), (5, 10)),  #2nd row
                    
                    ('ALIGN',(0,0),(-1,-1),'CENTER')
                ]
        
    
        t.setStyle(TableStyle(table_style))

        # Set the width of each column
        total_width = 580.68  # Total available width in points
        column_width = total_width / 6
        t._argW = [column_width] * 6
        
        Story.append(t)
        Story.append(Spacer(1, 12))
        data1 = []
        H3 = Paragraph('''<para><font size='12'><b>Basic Details:</b></font></para>''', styles["BodyText"])
        heading3 = [H3, ""]
        data1.append(heading3)
        
        r1c1 = Paragraph('''<para align=left><font size='10'>Branch Code</font></para>''', styles["BodyText"])
        r1c2 = Paragraph('''<para align=center><font size='10'>Branch Name</font></para>''', styles["BodyText"])
        r1c3 = Paragraph('''<para align=right><font size='10'>Region</font></para>''', styles["BodyText"])
        row1 = [r1c1,r1c2, r1c3] 
        data1.append(row1)
        if review == 'PSC1' or review == 'PSC2':
            r2c1 = Paragraph('''<para align=left><font size='10'>''' + psc_data[0]['branch_code_id__branch_code'] + '''</font></para>''', styles["BodyText"])
            r2c2 = Paragraph('''<para align=center><font size='10'>''' + psc_data[0]['branch_code_id__branch_name'] + '''</font></para>''', styles["BodyText"])
            r2c3 = Paragraph('''<para align=right><font size='10'>''' + psc_data[0]['region_name'] + '''</font></para>''', styles["BodyText"])
            row2 = [r2c1,r2c2, r2c3] 
        elif review == 'sac':
            r2c1 = Paragraph('''<para align=left><font size='10'>''' + sac_data[0]['psc_rec_id__branch_code_id__branch_code'] + '''</font></para>''', styles["BodyText"])
            r2c2 = Paragraph('''<para align=center><font size='10'>''' + sac_data[0]['psc_rec_id__branch_code_id__branch_name'] + '''</font></para>''', styles["BodyText"])
            r2c3 = Paragraph('''<para align=right><font size='10'>''' + sac_data[0]['psc_rec_id__region_name'] + '''</font></para>''', styles["BodyText"])
            row2 = [r2c1,r2c2, r2c3] 
        data1.append(row2)
        data1.append('')
        if review == 'PSC1' or review == 'PSC2':
            r3c1 = Paragraph('''<para><font size='10'>PSC ID</font></para>''', styles["BodyText"])
        elif review == 'sac':
            r3c1 = Paragraph('''<para><font size='10'>SAC ID</font></para>''', styles["BodyText"])
        r3c2 = Paragraph('''<para align=center><font size='10'>Borrower Name</font></para>''', styles["BodyText"])
        r3c3 = Paragraph('''<para align=center><font size='10'>Customer ID</font></para>''', styles["BodyText"])
        r3c4 = Paragraph('''<para align=right><font size='10'>NPA Date</font></para>''', styles["BodyText"])
        row3 = [r3c1, r3c3, r3c2, r3c4]
        data1.append(row3)
        if review == 'PSC1' or review == 'PSC2':
            r4c1 = Paragraph('''<para><font size='10'>''' + psc_data[0]['psc_rec_id']+ '''</font></para>''', styles["BodyText"])
            r4c2 = Paragraph('''<para align=center><font size='10'>'''+ psc_data[0]['borrower_name'] + '''</font></para>''', styles["BodyText"])
            r4c3 = Paragraph('''<para align=center><font size='10'>'''+ psc_data[0]['cust_id'] + '''</font></para>''', styles["BodyText"])
            r4c4 = Paragraph('''<para align=right><font size='10'>'''+ psc_data[0]['npa_date__date'].strftime('%d-%m-%Y') + '''</font></para>''', styles["BodyText"])
            row4 = [r4c1, r4c3, r4c2, r4c4]
        elif review == 'sac':
            r4c1 = Paragraph('''<para><font size='10'>''' + sac_data[0]['sac_rec_id']+ '''</font></para>''', styles["BodyText"])
            r4c2 = Paragraph('''<para align=center><font size='10'>'''+ sac_data[0]['psc_rec_id__borrower_name'] + '''</font></para>''', styles["BodyText"])
            r4c3 = Paragraph('''<para align=center><font size='10'>'''+ sac_data[0]['psc_rec_id__cust_id'] + '''</font></para>''', styles["BodyText"])
            r4c4 = Paragraph('''<para align=right><font size='10'>'''+ sac_data[0]['psc_rec_id__npa_date__date'].strftime('%d-%m-%Y') + '''</font></para>''', styles["BodyText"])
            row4 = [r4c1, r4c3, r4c2, r4c4]


        data1.append(row4)
        data1.append('')

        t1 = Table(data1)
        table_style1 = [
                    # ('GRID',(0,0),(-1,-1),0.2,colors.black),
                    # ('BOX', (0, 0), (-1, -1), 1, colors.black),  
                    # ('SPAN', (2, 1), (2, 1)),  #2nd row
                    # ('SPAN', (2, 1), (2, 1)),  #2nd row
                    # ('SPAN', (0, 2), (1, 2)),  #2nd row
                    # ('SPAN', (3, 2), (3, 2)),  #2nd row
                    
                    ('ALIGN',(0,0),(-1,-1),'LEFT')
                ]
        
    
        t1.setStyle(TableStyle(table_style1))

        # Set the width of each column
        total_width1 = 580  # Total available width in points
        column_width1 = total_width1 / 4
        t1._argW = [column_width1] * 4
        
        Story.append(t1)

        
        # if review == 'PSC1' or review == 'PSC2':
        cs_table_data = [
            ['Sl. NO.',	'SRN',	'Date of Release',	'Nature of Account',	'Nature of Advance',	'LAN',	'Sanction Amount',	'Due Date',	'NPA Date',	'Present Balance',	'Current Balance',	'Purpose of Advance',	'Asset Classification', 'Document Date']
                        ]
        cs_table = Table(cs_table_data)
        if review == 'PSC1' or review == 'PSC2':
            for cs in credit_datapsc:
                cs_row = [
                    cs['credit_feci_slno'] or '-',
                    cs['reference_num'] or '-',
                    cs['sanction_date'].strftime('%d-%m-%Y') if cs['sanction_date'] else '-',
                    cs['account_nature'] or '-',
                    cs['advance_nature'] or '-',
                    cs['lan'] or '-',
                    cs['sanctioned_limit'],
                    cs['due_date'].strftime('%d-%m-%Y') if cs['due_date'] else '-',
                    cs['npa_date'].strftime('%d-%m-%Y') if cs['npa_date'] else '-',
                    cs['npa_balance'] or '-',
                    cs['balance'] or '-',
                    cs['advance_purpose'] or '-',
                    cs['asset_classification'] or '-',
                    cs['doc_date'].strftime('%d-%m-%Y') if cs['doc_date'] else '-'
                ]
                cs_table_data.append(cs_row)
            
            cs_table = Table(cs_table_data)
            cs_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('FONTSIZE', (0, 0), (-1, -1), 4),  # Set font size
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
            ]))

            Story.append(cs_table)
        elif review == 'sac':
            for cs in credit_datasac:
                cs_row = [
                    cs['credit_feci_slno'] or '-',
                    cs['reference_num'] or '-',
                    cs['sanction_date'].strftime('%d-%m-%Y') if cs['sanction_date'] else '-',
                    cs['account_nature'] or '-',
                    cs['advance_nature'] or '-',
                    cs['lan'] or '-',
                    cs['sanctioned_limit'],
                    cs['due_date'].strftime('%d-%m-%Y') if cs['due_date'] else '-',
                    cs['npa_date'].strftime('%d-%m-%Y') if cs['npa_date'] else '-',
                    cs['npa_balance'] or '-',
                    cs['balance'] or '-',
                    cs['advance_purpose'] or '-',
                    cs['asset_classification'] or '-',
                    cs['doc_date'].strftime('%d-%m-%Y') if cs['doc_date'] else '-'
                ]
                cs_table_data.append(cs_row)
            
            cs_table = Table(cs_table_data)
            cs_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('FONTSIZE', (0, 0), (-1, -1), 4),  # Set font size
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
            ]))

            Story.append(cs_table)

        Story.append(Spacer(1, 24))  # Spacer between the two tables
        lapses_table_data = [
                            ['Account No','Branch Head During lapses observed',	'Lapses', 'Present Branch Head']
                        ]
        mom_accno = []
        lapses_table = Table(lapses_table_data)
        
        # Add the data rows to the table data
        if review == 'PSC1' or review == 'PSC2':
            for cd in credit_datapsc:
                mom_accno.append(cd['lan'])
            for cs in psc_data[0]['mom_lapse_desc']:

                momacc_no = Paragraph(psc_data[0]['facility_num'])
                remarks = Paragraph(cs['lapses_psc_remarks'] or '-', styles['Normal'])
                branch_head_info = Paragraph(f"{cs['lapses_psc_branch_head_name']}({cs['lapses_psc_branch_head_id']})" if cs['lapses_psc_branch_head_name'] and cs['lapses_psc_branch_head_id'] else '-', styles['Normal'])
                present_br = Paragraph('''<para align=left><font size='10'><b>''' + psc_data[0]['mom_br_head'][0]['psc_branch_head_name'] + '(' + psc_data[0]['mom_br_head'][0]['psc_branch_head_id'] + ')'+'''</b></font></para>''', styles["BodyText"])
                
                cs_row = [momacc_no, branch_head_info, remarks, present_br]
                lapses_table_data.append(cs_row)

            lapses_table = Table(lapses_table_data)
            lapses_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),  # Reduce font size to 8
                    ('WORDWRAP', (0, 0), (-1, -1), 'LTR')  # Enable word wrap
            ]))

            Story.append(lapses_table)
        elif review == 'sac':
            for cd in credit_datasac:
                mom_accno.append(cd['lan'])
            for cs in sac_data[0]['mom_lapse_desc']:
                momacc_no = Paragraph(sac_data[0]['psc_rec_id__facility_num'])
                remarks = Paragraph(cs['lapses_sac_remarks'] or '-', styles['Normal'])
                branch_head_info = Paragraph(f"{cs['lapses_sac_branch_head_name']}({cs['lapses_sac_branch_head_id']})" if cs['lapses_sac_branch_head_name'] and cs['lapses_sac_branch_head_id'] else '-', styles['Normal'])
                present_br = Paragraph('''<para align=left><font size='10'><b>''' + sac_data[0]['mom_br_head'][0]['sac_branch_head_name'] + '(' + sac_data[0]['mom_br_head'][0]['sac_branch_head_id'] + ')'+'''</b></font></para>''', styles["BodyText"])
                
                cs_row = [momacc_no, branch_head_info, remarks, present_br]
                lapses_table_data.append(cs_row)
            
            lapses_table = Table(lapses_table_data)
            lapses_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),  # Reduce font size to 8
                    ('WORDWRAP', (0, 0), (-1, -1), 'LTR')  # Enable word wrap
            ]))

            Story.append(lapses_table)
        Story.append(Spacer(1, 24))  # Spacer between the two tables
        
        doc.build(Story)

    
        # pdf.build(data)
        buffer.seek(0)
        # return FileResponse(buffer, as_attachment=True, filename=''+ review+'_mom_review_export.pdf')
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="'+ review+'_mom_review_export.pdf"'
        response.write(buffer.getvalue())
        return response

    except Exception as e:
        # print('mom review export error',e)
        sc_log.error('MOM review export error: ' + e)
        # print('MOM review export error: ' + e)
        return redirect('mom_lapses')
