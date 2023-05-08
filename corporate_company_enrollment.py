import json
import sys
import base64
import warnings
from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader
import os.path
import shutil
from PIL import Image
from io import BytesIO
import logging
from urllib.parse import unquote


def checking_length(data, x, y, pdf):
    if len(data) > 29:
        pdf.set_font_size(7)
    elif len(data) > 22:
        pdf.set_font_size(8)
    else:
        pdf.set_font_size(9)

    if len(data) > 32:
        data1 = data[0:33]
        data2 = data[33:len(data)]
        pdf.text(x, y - 0.18, data1)
        pdf.text(x, y + 0.15, data2)
    else:
        pdf.text(x, y, data)


def signature(string, fileName):
    decoded_data = base64.b64decode(string)
    image = Image.open(BytesIO(decoded_data))
    original_width, original_height = image.size
    max_width = 300
    max_height = 150

    image = image.resize((max_width, max_height), resample=Image.Resampling.LANCZOS)
    image.save(fileName, format='PNG')

    # img_file = open(fileName, 'wb')
    # img_file.write(decoded_data)
    # img_file.close()
    # quit(0)


def first_page(data):
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
        tempFont = f'{application_path}/DejaVuSansCondensed_{data["company_name"]}.ttf'
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {fontPath}")

    pdf.add_font('dejavu', '', tempFont)
    pdf.add_page()
    primary_font = 10
    border = 0
    pdf.set_font('dejavu', '', primary_font)

    pdf.text(1.4, 5.15, data["company_name"].title())  # Company Name
    pdf.text(1.4, 7.1, data["company_street_address"])  # Company Street Address
    pdf.text(6.2, 8.6, data["company_city"].title())  # Company City
    pdf.text(6.2, 10.1, data["company_postal_code"])  # Company Postal Code
    pdf.text(1.4, 10.1, data["company_province"].title())  # Company Province

    # Printing Administrators
    if len(data["administrators"]) > 0:
        pdf.set_font('dejavu', '', 7.8)
        cell_height = 0.6
        y = 5.5
        pdf.set_y(y)
        x = 11.05
        for admin in data["administrators"]:
            pdf.set_x(x)
            pdf.multi_cell(w=3.0, h=cell_height, txt=admin['admin_name'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)
            pdf.multi_cell(w=2.9, h=cell_height, txt=admin['admin_role'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.4, split_only=False)  # Administrator's Role
            pdf.multi_cell(w=3.32, h=cell_height, txt=admin['admin_email'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3, split_only=False)  # Administrator's Email
            pdf.ln(cell_height)

    pdf.set_font('dejavu', '', 9.3)
    pdf.text(1.4, 12.5, data["policy_start_date"])  # Policy Start Date
    pdf.set_font('dejavu', '', primary_font)
    pdf.text(6.2, 12.5, str(data["no_of_employees"]))  # Number of Employees

    # To check if Wallet is selected
    if data["wallet_selected"] == 0 or data["wallet_selected"] is False:
        pdf.text(1.4, 14.0, "No")
    else:
        pdf.text(1.4, 14.0, "Yes")

    # To check if tier is selected
    if data["tier_selected"] == 0 or data["tier_selected"] is False:
        pdf.text(6.2, 14.0, "No")
    else:
        pdf.text(6.2, 14.0, "Yes")

    # Printing Plans
    if len(data["selected_plans"]) > 0:
        pdf.set_font('dejavu', '', 7.8)
        y = 12.9
        cell_height = 0.6
        pdf.set_y(y)
        for plan in data["selected_plans"]:
            pdf.set_x(11)
            pdf.multi_cell(w=3.8, h=cell_height, txt=plan["planLevel"], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3, split_only=False)
            pdf.multi_cell(w=1.4, h=cell_height, txt='${:.2f}'.format(plan["price_single"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
            pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(plan["price_couple"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
            pdf.multi_cell(w=1.7, h=cell_height, txt='${:.2f}'.format(plan["price_family"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
            pdf.ln(cell_height)

    pdf.set_font('dejavu', '', 12)
    # Filling the checkboxes for terms_conditions and advisor_disclosure
    if data['terms_conditions'] is True:  # terms and conditions
        pdf.text(1.3, 21.15, u'\u2713')
    if data['advisor_disclosure'] is True:  # advisor disclosure
        pdf.text(11.05, 21.15, u'\u2713')

    pdf.set_font('dejavu', '', primary_font)
    # To check how the payment is made
    if data["use_CreditCard"] is True:
        pdf.text(1.4, 22.45, "Credit Card")
    elif data["pad_Payment"] is True:
        pdf.text(1.4, 22.45, "Pre-Authorized Debit")
    elif data["invoice_Payment"] is True:
        pdf.text(1.4, 22.45, "Invoice Method")
    else:
        if "paymentMethod" in data:
            pdf.text(1.4, 22.45, data["paymentMethod"])
        else:
            pdf.text(1.4, 22.45, "None")


    pdf.text(1.4, 23.9, data["advisor_name"])  # Advisor Name
    # pdf.text(11.1, 22.45, data["date_signed"])  # Date Signed

    # Signature
    if data['signature'] is not None and 'data:image/png;base64,' in data['signature']:
        signature_file_name = f'signature_{data["company_name"]}.png'  # Need to be updated for generating and updating
        signature(data['signature'].split(',')[1], signature_file_name)
        # pdf.image(signature_file_name, 10.5, 23.1, 3, 1.2)
        os.remove(signature_file_name)

    # checking_length(data['company_name'], 1.5, 5.35, pdf)

    pdf.output(f'dummy_{data["company_name"]}.pdf')
    os.remove(tempFont)
    merging_pdf(data)


def merging_pdf(data):
    writer = PdfWriter()
    try:
        output_path = f"{data['filePath']}{data['fileName']}"
        try:
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            templateFilePath = os.path.join(application_path, "Template-No Wallet and No Tier-v2.pdf")
            copyFile = f'{application_path}/corporate_enrollment_template_{data["company_name"]}.pdf'
            shutil.copy2(templateFilePath, copyFile)
        except:
            print(f"ERROR: template.pdf file not found {templateFilePath}")

        file1 = open(copyFile, 'rb')
        test1 = PdfReader(file1)
        file2 = open(f'dummy_{data["company_name"]}.pdf', 'rb')
        test2 = PdfReader(file2)

        page = test1.pages[0]
        page1 = test2.pages[0]
        page.merge_page(page1)
        writer.add_page(page)

        outputStream = open(output_path, 'wb')
        writer.write(outputStream)
        outputStream.close()

        file1.close()
        file2.close()

        os.remove(f'dummy_{data["company_name"]}.pdf')
        os.remove(copyFile)

    except Exception as e:
        print(f"ERROR: {e}")


# noinspection PyBroadException
def update_pdf(data):
    writer = PdfWriter()

    try:
        input_path = f"{data['filePath']}{data['fileName']}"
        output_path = f"{data['filePath']}{data['fileName']}"
        # try:
        #     if getattr(sys, 'frozen', False):
        #         application_path = os.path.dirname(sys.executable)
        #     elif __file__:
        #         application_path = os.path.dirname(__file__)
        #     templateFilePath = os.path.join(application_path, input_path)
        # except:
        #     print(f"ERROR: template.pdf file not found {templateFilePath}")

        try:
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
        except:
            print(f"ERROR: ttf file not found {fontPath}")

        tempFont = f'{application_path}/DejaVuSansCondensed_{data["fileName"][:-4]}.ttf'
        shutil.copy2(fontPath, tempFont)
        # Signature
        pdf.add_page()
        if data['signature'] is not None and 'data:image/png;base64,' in data['signature']:
            signature_file_name = f'signature_{data["fileName"].split(".")[0]}.png'
            # rectangle dimensions in cm
            x = 11
            y = 23.3
            w = 9.3
            h = 0.98

            # load image from base64
            img_data = base64.b64decode(data['signature'].split(',')[1])
            with open(signature_file_name, 'wb') as f:
                f.write(img_data)
            img = Image.open(signature_file_name)

            # calculate new image dimensions to fit inside rectangle
            aspect_ratio = img.width / img.height
            new_width = w
            new_height = new_width / aspect_ratio
            if new_height > h:
                new_height = h
                new_width = new_height * aspect_ratio

            # resize image and center it inside the rectangle
            x_pos = x + (w - new_width) / 2
            y_pos = y + (h - new_height) / 2
            # pdf.image(signature_file_name, x_pos, y_pos, new_width , new_height )

            # signature(data['signature'].split(',')[1], signature_file_name)
            pdf.image(signature_file_name, 11.5, 23.3, 2.8, 0.98)
            # pdf.rect(11, 23.3, 9.3, 0.98)
            os.remove(signature_file_name)

        pdf.add_font('dejavu', '', tempFont)
        pdf.set_font('dejavu', '', 9)
        pdf.text(11.1, 22.45, data["date_signed"])
        pdf.output(f'dummy_{data["fileName"]}')

        file1 = open(f"{data['filePath']}{data['fileName']}", 'rb')
        test1 = PdfReader(file1)
        file2 = open(f'dummy_{data["fileName"]}', 'rb')
        test2 = PdfReader(file2)

        page = test1.pages[0]
        page1 = test2.pages[0]
        page.merge_page(page1)
        writer.add_page(page)

        outputStream = open(output_path, 'wb')
        writer.write(outputStream)
        outputStream.close()

        file1.close()
        file2.close()
        os.remove(f'dummy_{data["fileName"]}')

    except Exception as e:
        print(f"ERROR: {e}")


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

if jsonData["process"].upper() == "GENERATION":
    first_page(jsonData)
elif jsonData["process"].upper() == "UPDATION":
    update_pdf(jsonData)
else:
    print(f"ERROR! Wrong process mentioned {jsonData['process']}")
