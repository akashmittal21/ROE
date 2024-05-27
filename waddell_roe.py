import json
import sys
import base64
import warnings
import re
from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader, PdfMerger
import os.path
import shutil
import logging


def signature(string, fileName):
    decoded_data = base64.b64decode(string)
    img_file = open(fileName, 'wb')
    img_file.write(decoded_data)
    img_file.close()


def first_page(data, pdf):
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
        tempFont = f'{application_path}/tempfont_waddell_{data["first_name"]}.ttf'
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {fontPath}")

    pdf.add_font('dejavu', '', tempFont)

    pdf.add_page()
    pdf.set_font("dejavu", '', 9)

    full_name = f"{data['first_name']} {data['last_name']}"
    pdf.text(1.4, 5.35, data['first_name'])  # First Name
    pdf.text(11.1, 5.35, data['last_name'])  # Last Name

    border = 0
    pdf.set_y(6.25)
    pdf.set_x(1.3)
    pdf.multi_cell(9.3, 1, data.get('email'), border=border, max_line_height=0.5)

    pdf.text(11.1, 6.85, data['phone_number'])  # Phone number

    pdf.set_y(8.75)
    pdf.set_x(1.3)
    pdf.multi_cell(9.3, 1, data.get('street_address_line1'), border=border, max_line_height=0.5)

    pdf.text(11.1, 9.35, data['city'])

    pdf.text(1.4, 10.85, data['province'])  # Province
    pdf.text(11.1, 10.85, data['postal_code'])  # Postal Code

    cell_height = 0.6
    pdf.set_y(13.1)
    if len(data.get('plans')) > 0:
        for plan in data.get('plans'):
            pdf.set_x(1.3)
            pdf.multi_cell(7.9, cell_height, plan['planname'], border=border, align='L', new_x="RIGHT", new_y="TOP",max_line_height=0.3)
            pdf.multi_cell(5.1, cell_height, plan['details'], border=border, align='L', new_x="RIGHT", new_y="TOP",max_line_height=0.3)
            pdf.ln(cell_height)
            for product in plan['products']:
                pdf.set_x(1.6)
                pdf.multi_cell(7.6, cell_height, product['name'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
                pdf.multi_cell(4.5, cell_height, product['planCoverage'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
                pdf.multi_cell(1.55, cell_height, f"${product['price']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
                pdf.multi_cell(2, cell_height, f"${product['tax']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
                total_cell_x = pdf.get_x()
                pdf.multi_cell(2.2, cell_height, f"${product['total']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
                pdf.ln(cell_height)

        pdf.set_x(total_cell_x)
        pdf.multi_cell(2.2, cell_height, f"${round(float(data['totalAmount']), 2)}", border="TB", align='R',new_x="RIGHT", new_y="TOP")

    if data['termsandconditions'] is True:  # terms and conditions
        pdf.text(1.32, 22.05, u'\u2713')
    if data['disclouseradvisor'] is True:  # advisor disclosure
        pdf.text(11.07, 22.05, u'\u2713')

    pdf.text(1.4, 23.55, data['paymentMethod'])  # Payment Method
    pdf.text(11.1, 23.55, data['planEnrollmentDate'])  # Plan Enrollment date

    pdf.text(1.4, 25.15, data['advisorName'])  # Advisor Name
    if data['signature'] is not None and 'data:image/png;base64,' in data['signature']:
        signature_file_name = f'signature_{data["first_name"]}_{data["date_of_birth"]}.png'
        signature(data['signature'].split(',')[1], signature_file_name)
        pdf.image(signature_file_name, 11, 24.55, 4, 1)  # signature
        os.remove(signature_file_name)

    pdf.output(f'dummy_waddell_{data["first_name"]}_{data["date_of_birth"]}.pdf')
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
            templateFilePath = os.path.join(application_path, "Waddell_Enrollment_template.pdf")
            copyFile = f'{application_path}/enrollment_waddell_template_{data["first_name"]}_{data["date_of_birth"]}.pdf'
            shutil.copy2(templateFilePath, copyFile)
        except:
            print(f"ERROR: template.pdf file not found {templateFilePath}")
        file1 = open(copyFile, 'rb')
        test = PdfReader(file1)
        file2 = open(f'dummy_waddell_{data["first_name"]}_{data["date_of_birth"]}.pdf', 'rb')
        test1 = PdfReader(file2)

        page = test.pages[0]
        page1 = test1.pages[0]
        page.merge_page(page1)
        writer.add_page(page)

        outputstream = open(output_path, 'wb')
        writer.write(outputstream)
        outputstream.close()

        file1.close()
        file2.close()
        os.remove(f'dummy_waddell_{data["first_name"]}_{data["date_of_birth"]}.pdf')
        os.remove(copyFile)

    except Exception as e:
        print(f"ERROR: {e}")


def generate_waddell_roe(data):
    versionNo = "v1.0.0"
    pdf = FPDF('P', 'cm', 'Letter')
    first_page(data, pdf)
