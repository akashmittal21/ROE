import json
import sys
import base64
import warnings
from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader, PdfMerger
import os.path
import shutil
from PIL import Image
from io import BytesIO
import logging
from urllib.parse import unquote

#TODO: Need to write the code so that when the text goes out of its dedicated width it needs to adjust the font till the text is in the given width

def processInput(input_value, inputType):
    if inputType.lower() == "price":
        if isinstance(input_value, (float, int)):
            formatValue = format(input_value, '.2f')
            return formatValue
        elif isinstance(input_value, str):
            return input_value
    elif inputType.lower() == "misc":
        if isinstance(input_value, int):
            # formatValue = str(input)
            return input_value
        else:
            return input_value


def signature(string, fileName):
    decoded_data = base64.b64decode(string)
    image = Image.open(BytesIO(decoded_data))
    original_width, original_height = image.size
    max_width = 300
    max_height = 150

    image = image.resize((max_width, max_height))
    image.save(fileName, format='PNG')

    # img_file = open(fileName, 'wb')
    # img_file.write(decoded_data)
    # img_file.close()
    # quit(0)


def studentForm(data):
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
            fontPath = os.path.join(application_path, "MyraidPro.ttf")
        questionFont = f'{application_path}/MyraidPro_{data["firstName"]}_{data["lastName"]}.ttf'
        shutil.copy2(fontPath, questionFont)
    except:
        print(f"ERROR: ttf file not found {questionFont}")
        
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
        tempFont = f'{application_path}/DejaVuSansCondensed_{data["firstName"]}_{data["lastName"]}.ttf'
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {tempFont}")

    pdf.add_font('dejavu', '', tempFont)
    pdf.add_font('myraidpro', '', questionFont)
    pdf.add_page()
    primary_font = 10
    radio_font = 8
    pdf.set_font('dejavu', '', primary_font)

    # for circle
    # pdf.text(10.3, 1, u'\u25CF')

    # Student VIP Logo
    # w_image = 3
    # h_image = w_image * 183 / 275
    # pdf.image("studentVIPLOGO.png", 0.5, 0, w_image, h_image)

    pdf.text(5.6, 5.85, data['associationName'])  # University Name

    # Member Information
    pdf.text(5.6, 7.4, data['lastName'])  # Last Name
    if 'middleInitial' in data:
        pdf.text(12.3, 7.4, data['middleInitial'])  # Middle Initial
    pdf.text(14.85, 7.4, data['firstName'])  # First Name
    pdf.text(16.4, 8.85, data['dateOfBirth'])  # Date of Birth
    pdf.text(16.4, 9.7, data['planEnrollmentDate'])  # Plan enrollment date
    if 'studentId' in data:
        pdf.text(7.7, 9.7, data['studentId'])
    pdf.text(5.6, 10.95, data['homeAddress'])  # Home Address
    pdf.text(15.45, 10.95, data['city'])  # City
    pdf.text(5.6, 12.17, data['province'])  # Province
    pdf.text(7.5, 12.17, data['postalCode'])  # Postal Code
    pdf.set_font('dejavu', '', 9)
    if 'telephoneNumber' in data:
        pdf.text(9.65, 12.17, data['telephoneNumber'])  # Telephone Number
    if 'cellNumber' in data:
        pdf.text(12.5, 12.17, data['cellNumber'])  # Cell Number
    pdf.text(15.4, 12.17, data['email'])  # Email
    
    # This is to fill the question based on if the customer is a foreign student
    pdf.set_font('myraidPro', '', primary_font)
    x_question = 12.9
    y_question = 14.77
    question = ""
    if data['isForeignStudent'] is False:
        question = "Do you have a Provincial Heath Card?"
    elif data['isForeignStudent'] is True:
        question = "I confirm that I have UHIP"
        x_question += 1.7
    pdf.text(x_question, y_question, question)

    pdf.set_font('dejavu', '', radio_font)
    gender = data['gender']
    x_gender = 7.24
    y_gender = 8.15
    if gender.lower() == "male":
        pass
    elif gender.lower() == "female":
        x_gender += 1.55
    elif gender.lower() == "undisclosed":
        x_gender += 3.45
    elif gender.lower() == "non-binary":
        x_gender += 6.07
    else:
        print("Error! Please check gender")
    pdf.text(x_gender, y_gender, u'\u25CF')

    language = data['languagePreference']
    x_language = 9.45
    y_language = 8.82
    if language.lower() == "en":
        pass
    elif language.lower() == "fr":
        x_language += 1.85
    else:
        print("Error! Please check language preference")
    pdf.text(x_language, y_language, u'\u25CF')

    maritalStatus = data['maritalStatus']
    x_ms = 7.765
    y_ms = 12.865
    if maritalStatus.lower() == "single":
        pass
    elif maritalStatus.lower() == "married":
        x_ms += 1.92
    elif maritalStatus.lower() == "separated":
        x_ms += 4.14
    elif maritalStatus.lower() == "divorced":
        x_ms += 6.35
    elif maritalStatus.lower() == "widowed":
        x_ms += 8.58
    elif maritalStatus.lower() == "common law":
        y_ms += 0.55
    else:
        print("ERROR! Please check marital status value")
    pdf.text(x_ms, y_ms, u'\u25CF')

    parentCoverage = "no"
    x_pc = 13.14
    y_pc = 14.048
    if parentCoverage.lower() == "yes":
        pass
    elif parentCoverage.lower() == "no":
        x_pc += 1.9
    else:
        print("ERROR! Please check parent coverage value.")
    pdf.text(x_pc, y_pc, u'\u25CF')
    
    isForeignStudent = False
    x_fs = 9.81
    y_fs = 14.75
    if isForeignStudent is True:
        pass
    else:
        x_fs += 1.42
    pdf.text(x_fs, y_fs, u'\u25CF')
    
    hasUhip = False
    x_tq = 18.8
    y_tq = 14.75
    if hasUhip is True:
        pass
    else:
        x_tq += 1.27
    pdf.text(x_tq, y_tq, u'\u25CF')

    coverage = data['coverageType']
    x_coverage = 9.21
    y_coverage = 15.47
    if coverage.lower() == "single":
        pass
    elif coverage.lower() == "couple":
        x_coverage += 1.89
        y_coverage -= 0.01
    elif coverage.lower() == "family":
        x_coverage += 3.79
        y_coverage -= 0.012
    else:
        print("ERROR! Please check the coverage type")
    pdf.text(x_coverage, y_coverage, u'\u25CF')

    # Spouse Details
    if data['having_spouse'] is True:
        pdf.set_font('dejavu', '', primary_font)
        pdf.text(5.6, 21.25, data['spouseDetails']['lastName'])  # Last Name
        if 'middleInitial' in data['spouseDetails']:
            pdf.text(11.4, 21.25, data['spouseDetails']['middleInitial'])  # Middle Initial
        pdf.text(14.3, 21.25, data['spouseDetails']['firstName'])  # First Name
        pdf.text(5.6, 22.62, data['spouseDetails']['dateOfBirth'])  # Date of Birth

        if 'carrierName' in data['spouseDetails']:
            pdf.text(9.5, 24.75, data['spouseDetails']['carrierName'])

        pdf.set_font('dejavu', '', radio_font)
        spouse_gender = data['spouseDetails']['gender']
        x_sg = 12.74
        y_sg = 22.51
        if spouse_gender.lower() == "male":
            pass
        elif spouse_gender.lower() == "female":
            x_sg += 1.55
            y_sg += 0.02
        elif spouse_gender.lower() == "undisclosed":
            x_sg += 3.45
            y_sg += 0.02
        elif spouse_gender.lower() == "non-binary":
            x_sg += 6.07
            y_sg += 0.02
        pdf.text(x_sg, y_sg, u'\u25CF')

        spouse_isInsured = data['spouseDetails']['isInsured']
        x_si = 5.55
        y_si = 24.04
        if spouse_isInsured is True:
            pass
        else:
            x_si += 1.27
        pdf.text(x_si, y_si, u'\u25CF')

        if 'coverageType' in data['spouseDetails']:
            spouse_coverage = data['spouseDetails']['coverageType']
            x_sc = 9.39
            y_sc = 25.6
            if spouse_coverage.lower() == "single":
                pass
            elif spouse_coverage.lower() == "family":
                x_sc += 1.59
            pdf.text(x_sc, y_sc, u'\u25CF')

    # ------ Second Page --------
    pdf.add_page()
    # child_gender_font = 8
    border = 0
    if len(data['childrenDetails']) > 0:
        y_child = 3.83
        y_radio = 3.76
        y = 3.35
        pdf.set_y(y)
        border = 0
        for child in data['childrenDetails']:
            pdf.set_font('dejavu', '', primary_font)
            pdf.text(5.5, y_child, child['lastName'])
            pdf.text(9.7, y_child, child['firstName'])
            pdf.text(13.45, y_child, child['dateOfBirth'])
            # pdf.set_font('dejavu', '', child_gender_font)
            # pdf.text(15.6, y_child, child['gender'])
            pdf.set_x(15.7)
            pdf.multi_cell(w=2.05, h=0.7, text=child['gender'], border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
            pdf.set_font('dejavu', '', radio_font)
            if 'isFullTimeStudent' in child:
                if child['isFullTimeStudent'] is True:
                    pdf.text(18.06, y_radio, u'\u25CF')
            if 'isDisabled' in child:
                if child['isDisabled'] is True:
                    pdf.text(19.6, y_radio, u'\u25CF')
            y_child += 1.2
            y_radio += 1.2
            y += 1.2
            pdf.set_y(y)

    if len(data['plans']) > 0:
        x_plan = 5.2
        y_plan = 18.85
        x_product = 5.7
        h_plan_cell = 0.75
        pdf.set_y(y_plan)
        border = 0
        # print(pdf.get_string_width("Voluntary Benefits: Dependant Critical Illness"))
        for plan in data['plans']:
            pdf.set_font('dejavu', '', primary_font)
            pdf.set_x(x_plan)
            pdf.multi_cell(w=7.25, h=h_plan_cell, text=plan['planname'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
            pdf.ln(h_plan_cell * 0.8)
            planProducts = plan['products']
            for product in planProducts:
                pdf.set_x(x_product)
                pdf.multi_cell(w=6.75, h=h_plan_cell, text=product['name'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
                if 'planCoverage' in product:
                    coverage = product['planCoverage']
                else:
                    coverage = data['coverageType']
                pdf.multi_cell(w=2.55, h=h_plan_cell, text=coverage, border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
                pdf.multi_cell(w=1.94, h=h_plan_cell, text=f"${processInput(product['price'], 'price')}", border=border, align='R', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
                pdf.multi_cell(w=1.83, h=h_plan_cell, text=f"${processInput(product['tax'], 'price')}", border=border, align='R', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
                pdf.multi_cell(w=2.04, h=h_plan_cell, text=f"${processInput(product['total'], 'price')}", border=border, align='R', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
                pdf.ln(h_plan_cell)

            # if pdf.get_string_width(plan['planName']) > 5.772:
            #     pdf.ln(h_plan_cell * 0.5)
            # else:
            #     pdf.ln(h_plan_cell * 1.2)
            # pdf.ln(h_plan_cell)

        pdf.set_x(12.5)
        pdf.set_font('helvetica', 'B', primary_font)
        pdf.multi_cell(w=2.5, h=h_plan_cell, text='Total', border='TB', align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
        pdf.set_font('dejavu', '', primary_font)
        if 'totalPremium' in data:
            pdf.multi_cell(w=1.94, h=h_plan_cell, text=f"${processInput(data['totalPremium'], 'price')}", border='TB', align='R', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
        if 'totalTax' in data:
            pdf.multi_cell(w=1.83, h=h_plan_cell, text=f"${processInput(data['totalTax'], 'price')}", border='TB', align='R', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
        if 'totalAmount' in data:
            pdf.multi_cell(w=2.06, h=h_plan_cell, text=f"${processInput(data['totalAmount'], 'price')}", border='TB', align='R', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)

    # ------ Third Page --------
    pdf.add_page()
    pdf.set_font('dejavu', '', primary_font)

    # if len(data['beneficiaries']) > 0:
    #     x_pb = 5.35
    #     y_pb = 1.9
    #     h_pb_cell = 0.6
    #     pdf.set_y(y_pb)
    #     border = 0
    #     for pb in data['beneficiaries']:
    #         if pb['type'].lower() == "primary":
    #             pdf.set_x(x_pb)
    #             pdf.multi_cell(w=3.1, h=h_pb_cell, txt=pb['lastName'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.multi_cell(w=3.75, h=h_pb_cell, txt=pb['firstName'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.multi_cell(w=0.9, h=h_pb_cell, txt=f"{processInput(pb['age'], 'misc')}", border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.multi_cell(w=2.23, h=h_pb_cell, txt=f"{processInput(pb['percentage'], 'misc')}%", border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.multi_cell(w=2.75, h=h_pb_cell, txt=pb['relationship'], border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             if "trusteeName" in pb:
    #                 # pass
    #                 pdf.multi_cell(w=2.75, h=h_pb_cell, txt=pb['trusteeName'], border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.ln(1.17)
    # 
    # if len(data['beneficiaries']) > 0:
    #     x_cb = 5.35
    #     y_cb = 8.3
    #     h_cb_cell = 0.6
    #     pdf.set_y(y_cb)
    #     border = 0
    #     for cb in data['beneficiaries']:
    #         if cb['type'].lower() == "contingent":
    #             pdf.set_x(x_cb)
    #             pdf.multi_cell(w=3.1, h=h_cb_cell, txt=cb['lastName'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.multi_cell(w=3.75, h=h_cb_cell, txt=cb['firstName'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.multi_cell(w=0.9, h=h_cb_cell, txt=f"{processInput(cb['age'], 'misc')}", border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.multi_cell(w=2.23, h=h_cb_cell, txt=f"{processInput(cb['percentage'], 'misc')}%", border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.multi_cell(w=2.75, h=h_cb_cell, txt=cb['relationship'], border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             if "trusteeName" in pb:
    #                 # pass
    #                 pdf.multi_cell(w=2.75, h=h_pb_cell, txt=cb['trusteeName'], border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
    #             pdf.ln(1.17)

    x_ds = 17.5
    y_ds = 7.9
    pdf.set_y(y_ds)
    pdf.set_x(x_ds)
    pdf.cell(w=3.22, h=1.24, text=data['dateSigned'], border=0, align='C')

    # Signature
    if data['signature'] is not None and 'data:image/png;base64,' in data['signature']:
        signature_file_name = f'signature_{data["firstName"]}.png'
        signature(data['signature'].split(',')[1], signature_file_name)
        pdf.image(signature_file_name, 5.2, 7.8, 3, 1.2)
        os.remove(signature_file_name)

    pdf.output(f'dummy_{data["firstName"]}_{data["lastName"]}.pdf')
    os.remove(tempFont)
    os.remove(questionFont)
    merging_pdf(data)


def merging_pdf(data):
    writer = PdfWriter()
    # try:
    output_path = f"{data['filePath']}{data['fileName']}"
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        templateFilePath = os.path.join(application_path, "Smartchoice-Template.pdf")
        copyFile = f'{application_path}/StudentEnrollmentTemplate_{data["firstName"]}_{data["lastName"]}.pdf'  # TODO: Change the name of the CopyFile later!
        shutil.copy2(templateFilePath, copyFile)
    except:
        print(f"ERROR: template.pdf file not found {templateFilePath}")

    file1 = open(copyFile, 'rb')
    test1 = PdfReader(file1)
    file2 = open(f'dummy_{data["firstName"]}_{data["lastName"]}.pdf', 'rb')
    test2 = PdfReader(file2)

    page1 = test1.pages[0]
    page_dummy = test2.pages[0]
    page1.merge_page(page_dummy)
    writer.add_page(page1)

    page2 = test1.pages[1]
    page2_dummy = test2.pages[1]
    page2.merge_page(page2_dummy)
    writer.add_page(page2)

    page3 = test1.pages[2]
    page3_dummy = test2.pages[2]
    page3.merge_page(page3_dummy)
    writer.add_page(page3)

    outputStream = open(output_path, 'wb')
    writer.write(outputStream)
    outputStream.close()

    file1.close()
    file2.close()

    os.remove(f'dummy_{data["firstName"]}_{data["lastName"]}.pdf')
    os.remove(copyFile)

    # except Exception as e:
    #     print(f"ERROR: {e}")


# noinspection PyBroadException
# def update_pdf(data):
#     writer = PdfWriter()
#
#     try:
#         input_path = f"{data['filePath']}{data['fileName']}"
#         output_path = f"{data['filePath']}{data['fileName']}"
#         # try:
#         #     if getattr(sys, 'frozen', False):
#         #         application_path = os.path.dirname(sys.executable)
#         #     elif __file__:
#         #         application_path = os.path.dirname(__file__)
#         #     templateFilePath = os.path.join(application_path, input_path)
#         # except:
#         #     print(f"ERROR: template.pdf file not found {templateFilePath}")
#
#         try:
#             if getattr(sys, 'frozen', False):
#                 application_path = os.path.dirname(sys.executable)
#             elif __file__:
#                 application_path = os.path.dirname(__file__)
#             fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
#         except:
#             print(f"ERROR: ttf file not found {fontPath}")
#
#         tempFont = f'{application_path}/DejaVuSansCondensed_{data["fileName"][:-4]}.ttf'
#         shutil.copy2(fontPath, tempFont)
#         # Signature
#         pdf.add_page()
#         if data['signature'] is not None and 'data:image/png;base64,' in data['signature']:
#             signature_file_name = f'signature_{data["fileName"].split(".")[0]}.png'
#             # rectangle dimensions in cm
#             x = 11
#             y = 23.3
#             w = 9.3
#             h = 0.98
#
#             # load image from base64
#             img_data = base64.b64decode(data['signature'].split(',')[1])
#             with open(signature_file_name, 'wb') as f:
#                 f.write(img_data)
#             img = Image.open(signature_file_name)
#
#             # calculate new image dimensions to fit inside rectangle
#             aspect_ratio = img.width / img.height
#             new_width = w
#             new_height = new_width / aspect_ratio
#             if new_height > h:
#                 new_height = h
#                 new_width = new_height * aspect_ratio
#
#             # resize image and center it inside the rectangle
#             x_pos = x + (w - new_width) / 2
#             y_pos = y + (h - new_height) / 2
#             # pdf.image(signature_file_name, x_pos, y_pos, new_width , new_height )
#
#             # signature(data['signature'].split(',')[1], signature_file_name)
#             pdf.image(signature_file_name, 11.5, 23.3, 2.8, 0.98)
#             # pdf.rect(11, 23.3, 9.3, 0.98)
#             os.remove(signature_file_name)
#
#         pdf.add_font('dejavu', '', tempFont)
#         pdf.set_font('dejavu', '', 9)
#         pdf.text(11.1, 22.45, data["date_signed"])
#         pdf.output(f'dummy_{data["fileName"]}')
#
#         file1 = open(f"{data['filePath']}{data['fileName']}", 'rb')
#         test1 = PdfReader(file1)
#         file2 = open(f'dummy_{data["fileName"]}', 'rb')
#         test2 = PdfReader(file2)
#
#         page = test1.pages[0]
#         page1 = test2.pages[0]
#         page.merge_page(page1)
#         writer.add_page(page)
#
#         outputStream = open(output_path, 'wb')
#         writer.write(outputStream)
#         outputStream.close()
#
#         file1.close()
#         file2.close()
#         os.remove(f'dummy_{data["fileName"]}')
#
#     except Exception as e:
#         print(f"ERROR: {e}")


# String version
# json_encoded_string = sys.argv[1]
# json_decoded_string = unquote(json_encoded_string)
# jsonData = json.loads(json_decoded_string)

# File version
json_file = sys.argv[1]
with open(json_file, 'r') as myFile:
    json_file = myFile.read()
jsonData = json.loads(json_file)

versionNo = "v1.0"
pdf = FPDF('P', 'cm', 'letter')

studentForm(jsonData)

# if jsonData["process"].upper() == "GENERATION":
#     first_page(jsonData)
# elif jsonData["process"].upper() == "UPDATION":
#     update_pdf(jsonData)
# else:
#     print(f"ERROR! Wrong process mentioned {jsonData['process']}")
