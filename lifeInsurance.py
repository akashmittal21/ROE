import shutil
from urllib.parse import unquote
from fpdf import FPDF
from PyPDF2 import PdfReader, PageObject, PdfWriter
import os
import json
import sys


def create_dummy_pdf(customer_data: json):
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
        tempFont = f'{application_path}/DejaVuSansCondensed_temp.ttf'
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {tempFont}")

    pdf.add_font('dejavu', '', tempFont)

    pdf.set_font('dejavu', '', 10)

    # First Page
    pdf.add_page()
    pdf.text(0.95, 7.3, "Rhodes")          # Last Name
    pdf.text(7.5, 7.3, "Robert")          # First Name

    pdf.set_font_size(6)
    pdf.text(15.08, 7.085, u'\u25CF')           # Gender - Male Option

    pdf.set_font_size(10)
    pdf.text(17, 7.3, "10-11-1970")         # Date of Birth
    pdf.text(0.95, 8.35, "1000 Innovation Drive")        # Address
    pdf.text(10, 8.35, "Kanata")                        # City
    pdf.text(16.2, 8.35, "ON")                           # Province
    pdf.text(17.9, 8.35, "K2K 3E7")

    pdf.text(0.95, 9.4, "+1390-031-0123")
    pdf.text(12.85, 9.4, "robert.rhodes@mail.com")

    pdf.set_font_size(6)

    pdf.text(0.96, 11.1, u'\u25CF')                 # Yes option for applying for coverage

    pdf.text(0.96, 12.42, u'\u25CF')                # Member
    pdf.text(5.085, 12.42, u'\u25CF')               # Amount Member $25000
    pdf.text(19.72, 12.425, u'\u25CF')              # Smoking question - Member

    pdf.text(0.96, 13.7, u'\u25CF')  # Spouse
    pdf.text(5.085, 13.7, u'\u25CF')  # Amount Spouse $25000
    pdf.text(19.72, 13.7, u'\u25CF')  # Smoking question - Spouse

    pdf.set_font_size(10)

    pdf.text(0.95, 16.55, "Rhodes")  # Last Name - Spouse
    pdf.text(7.5, 16.55, "Candice")  # First Name - Spouse

    pdf.set_font_size(6)
    # pdf.text(15.08, 16.355, u'\u25CF')  # Gender Spouse- male Option
    pdf.text(15.08, 16.685, u'\u25CF')  # Gender Spouse- female Option

    pdf.set_font_size(10)
    pdf.text(17, 16.55, "01-05-1972")  # Date of Birth Spouse

    # Second Page
    pdf.add_page()

    pdf.set_font_size(6)

    pdf.text(0.86, 3.235, u'\u25CF')        # Payment method - PAD Option

    pdf.set_font_size(10)

    pdf.image("signature.png", 1.5, 11.5, 4, 1)           # Member Signature
    pdf.image("signature.png", 11.5, 11.5, 4, 1)          # Spouse Signature

    pdf.text(7.5, 12.5, "01-03-2024")                             # Member Date signed
    pdf.text(17.5, 12.5, "01-03-2024")                             # Spouse Date signed

    pdf.output(f'dummy_{"ia"}.pdf')
    merging_pdf(customer_data)


def create_dummy_pdf_va(customer_data: json):
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
        tempFont = f'{application_path}/DejaVuSansCondensed_temp.ttf'
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {tempFont}")

    pdf.add_font('dejavu', '', tempFont)

    pdf.set_font('dejavu', '', 10)

    # First Page
    pdf.add_page()
    pdf.text(0.95, 6.8, "Rhodes")          # Last Name
    pdf.text(7.5, 6.8, "Robert")          # First Name

    pdf.text(0.95, 7.85, "Toronto, Ontario")        # Member place of birth
    pdf.text(11.3, 7.85, "Principal")               # Member occupation

    pdf.set_font_size(6)
    pdf.text(15.1, 6.58, u'\u25CF')           # Gender - Male Option

    pdf.set_font_size(10)
    pdf.text(17, 6.8, "10-11-1970")         # Date of Birth
    pdf.text(0.95, 8.85, "1000 Innovation Drive")        # Address
    pdf.text(10, 8.85, "Kanata")                        # City
    pdf.text(16.2, 8.85, "ON")                           # Province
    pdf.text(17.9, 8.85, "K2K 3E7")

    pdf.text(0.95, 9.9, "+1390-031-0123")
    pdf.text(12.85, 9.9, "robert.rhodes@mail.com")

    pdf.set_font_size(10)

    pdf.text(0.95, 12.6, "Rhodes")  # Last Name - Spouse
    pdf.text(7.5, 12.6, "Candice")  # First Name - Spouse
    pdf.text(17, 12.6, "01-05-1972")  # Date of Birth Spouse

    pdf.set_font_size(6)
    pdf.text(7.26, 11.13, u'\u25CF')    # Spouse member question - no option

    pdf.text(4.08, 11.60, u'\u25CF')        # Spouse social status - married option

    # pdf.text(15.08, 16.355, u'\u25CF')  # Gender Spouse- male Option
    pdf.text(15.1, 12.77, u'\u25CF')  # Gender Spouse- female Option

    pdf.set_font_size(10)
    pdf.text(0.95, 13.7, "Toronto, Ontario")        # Spouse place of birth
    pdf.text(11.3, 13.7, "Principal")               # Spouse occupation

    pdf.set_font_size(6)

    pdf.text(0.99, 14.92, u'\u25CF')                 # Member term life option
    pdf.text(0.99, 16.23, u'\u25CF')                 # Member critical illness option
    pdf.text(0.99, 17.648, u'\u25CF')                 # Spouse term life option
    pdf.text(0.99, 19.06, u'\u25CF')                 # Spouse critical illness option
    pdf.text(0.99, 20.49, u'\u25CF')                # Dependant term life option
    pdf.text(0.99, 21.915, u'\u25CF')                 # Dependant critical illness option

    pdf.set_font_size(10)

    pdf.text(9.4, 15.6, f"$50,000")  # Member term life option
    pdf.text(9.4, 16.9, f"$50,000")  # Member critical illness option
    pdf.text(9.4, 18.3, f"$25,000")  # Spouse term life option
    pdf.text(9.4, 19.7, f"$25,000")  # Spouse critical illness option
    pdf.text(9.4, 21.15, f"$10,000")  # Dependant term life option
    pdf.text(9.4, 22.55, f"$10,000")  # Dependant critical illness option
    #
    # pdf.text(0.96, 12.42, u'\u25CF')                # Member
    # pdf.text(5.085, 12.42, u'\u25CF')               # Amount Member $25000
    # pdf.text(19.72, 12.425, u'\u25CF')              # Smoking question - Member
    #
    # pdf.text(0.96, 13.7, u'\u25CF')  # Spouse
    # pdf.text(5.085, 13.7, u'\u25CF')  # Amount Spouse $25000
    # pdf.text(19.72, 13.7, u'\u25CF')  # Smoking question - Spouse
    
    # Second Page
    pdf.add_page()
    
    # Third Page
    pdf.add_page()

    # Fourth Page
    pdf.add_page()

    pdf.set_font_size(6)

    pdf.text(0.86, 11.715, u'\u25CF')        # Payment method - PAD Option

    pdf.set_font_size(10)

    pdf.image("signature.png", 1.5, 22.5, 4, 1)           # Member Signature
    pdf.image("signature.png", 11.5, 22.5, 4, 1)          # Spouse Signature

    pdf.text(7.5, 23.5, "01-03-2024")                             # Member Date signed
    pdf.text(17.5, 23.5, "01-03-2024")                             # Spouse Date signed

    pdf.output(f'dummy_{"ia"}.pdf')
    merging_pdf(customer_data)


def merging_pdf(customer_data: json):
    writer = PdfWriter()
    # try:
    # output_path = f"{data['filePath']}{data['fileName']}"
    output_path = f"ia_test_form_group_application.pdf"
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        templateFilePath = os.path.join(application_path, "IA Voluntary Group Application v1.1.pdf")
        copyFile = f'{application_path}/ia_life_insurance_{"template"}.pdf'
        shutil.copy2(templateFilePath, copyFile)
    except:
        print(f"ERROR: template.pdf file not found {templateFilePath}")

    file1 = open(copyFile, 'rb')
    test1 = PdfReader(file1)
    file2 = open(f'dummy_{"ia"}.pdf', 'rb')
    test2 = PdfReader(file2)

    no_of_pages = len(test2.pages)

    i = 0
    for i in range(no_of_pages):
        if i == 0 or i == 3:
            page1 = test1.pages[i]
            page_dummy = test2.pages[i]
            page1.merge_page(page_dummy)
            writer.add_page(page1)
    # page2 = test1.pages[1]
    # page3 = test2.pages[1]
    # page2.merge_page(page3)
    # writer.add_page(page2)

    outputStream = open(output_path, 'wb')
    writer.write(outputStream)
    outputStream.close()

    file1.close()
    file2.close()

    os.remove(f'dummy_{"ia"}.pdf')
    os.remove(copyFile)

    # except Exception as e:
    #     print(f"ERROR: {e}")


# String version
# json_encoded_string = sys.argv[1]
# json_decoded_string = unquote(json_encoded_string)
# data = json.loads(json_decoded_string)

# # File version
# json_file = sys.argv[1]
# with open(json_file, 'r') as myFile:
#     json_file = myFile.read()
# data = json.loads(json_file)

data = ""

versionNo = "v1.0"
pdf = FPDF('P', 'cm', 'letter')
# create_dummy_pdf(data)
create_dummy_pdf_va(data)