import sys
import json
from PyPDF2 import PdfFileWriter, PdfFileReader
from fpdf import FPDF
import os.path
from urllib.parse import unquote
import shutil


def print_text(pdf, full_name, relationship, certificate, carrier, policyNo, issueNo, y, displayVersion, fontSize, version, version_no):
    pdf.add_page()
    pdf.set_font('helvetica', '', 10)
    pdf.text(46, 702, full_name)
    pdf.set_font_size(9)
    pdf.text(46, y, f"{carrier}")
    pdf.text(82, y, f"{policyNo}")
    pdf.text(130.5, y, f"{str(certificate)}")
    pdf.text(204.5, y, f"{str(issueNo).rjust(2, '0')}")
    pdf.text(252.5, y, f"{str(relationship).rjust(2, '0')}")
    if displayVersion:
        pdf.set_font_size(fontSize)
        pdf.text(10, 10, f"{version_no}_{version}")


def print_card_g(greenshield, versionNo):
    pdf_g.add_page()
    writer = PdfFileWriter()
    pdf_g.set_font('helvetica', 'B', 10)
    place_holder = 0
    pdf_g.text(43, 210, f"{greenshield['customer']['firstName'].upper()} {greenshield['customer']['lastName'].upper()}")
    pdf_g.set_font_size(9.3)
    # pdf_g.text(43, 228, f"{greenshield['policyNumber']}-{str(place_holder).rjust(2, '0')}")
    pdf_g.text(43, 228, f"{greenshield['customer']['certMembershipId']}")
    pdf_g.set_font('helvetica', '', 7.5)
    pdf_g.text(43, 240, greenshield['serviceData']['name'].upper())
    place_holder += 1
    x1 = 284
    x2 = 338.5
    y = 198
    pdf_g.set_font('helvetica', 'B', 5.3)
    # pdf_g.text(x1, y, f"{greenshield['policyNumber']}-{str(place_holder).rjust(2, '0')}")

    if len(greenshield['dependants']) > 0:
        i = 0
        while i < len(greenshield['dependants']):
            dependant = greenshield['dependants'][i]
            pdf_g.text(x1, y, f"{dependant['certMembershipId']}")
            pdf_g.text(x2, y, f"{dependant['firstName'].upper()} {dependant['lastName'].upper()}")
            i += 1
            if len(greenshield['dependants']) <= 8:
                y += 8
            elif len(greenshield['dependants']) <= 9:
                y += 7
            else:
                y += 6.5
            # place_holder += 1

    if greenshield['displayVersion']:
        pdf_g.set_font('helvetica', '', int(greenshield['fontSize']))
        pdf_g.text(10, 780, f"{versionNo}_{greenshield['version']}")


    pdf_g.output(f"g_dummy_{greenshield['customer']['certMembershipId']}.pdf")

    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        filePath = os.path.join(application_path, "Greenshield_template.pdf")
        tempFile = f"{application_path}/Greenshield_template_{greenshield['customer']['certMembershipId']}.pdf"
        shutil.copy2(filePath, tempFile)
    except:
        print(f"ERROR: ttf file not found {filePath}")
    file1 = open(tempFile, 'rb')
    test = PdfFileReader(file1)
    # with open(f"g_dummy_{greenshield['customer']['certMembershipId']}.pdf", 'rb') as my_file:
    #     test1 = PdfFileReader(my_file)

    file2 = open(f"g_dummy_{greenshield['customer']['certMembershipId']}.pdf", 'rb')
    test1 = PdfFileReader(file2)

    page = test.getPage(0)
    page1 = test1.getPage(0)
    page.mergePage(page1)
    writer.add_page(page)

    outputstream = open(f"{greenshield['filePath']}{greenshield['fileName']}", 'wb')
    writer.write(outputstream)
    outputstream.close()
    file1.close()
    file2.close()
    os.remove(f"g_dummy_{greenshield['customer']['certMembershipId']}.pdf")
    os.remove(tempFile)


def print_card_e(equitable, versionNo):
    writer = PdfFileWriter()
    output = PdfFileWriter()
    displayVersion = equitable['displayVersion']
    fontSize = int(equitable['fontSize'])
    version = equitable['version']
    # place_holder = 1
    # certificate = '0000000200'
    y = 730
    carrier = equitable['serviceData']['carrier']
    issue_no = equitable['serviceData']['issueNo']
    policy_no = equitable['serviceData']['policyNo']
    full_name = f"{equitable['customer']['firstName'].capitalize()} {equitable['customer']['lastName'].capitalize()}"
    print_text(pdf_e, full_name, equitable['customer']['relationship'], equitable['customer']['certMembershipId'], carrier, policy_no, issue_no, y, displayVersion, fontSize, version, versionNo)

    if len(equitable['dependants']) > 0:
        i = 0
        while i < len(equitable['dependants']):
            dependant = equitable['dependants'][i]
            dependant_full_name = f"{dependant['firstName'].capitalize()} {dependant['lastName'].capitalize()}"
            print_text(pdf_e, dependant_full_name, dependant['relationship'], dependant['certMembershipId'], carrier, policy_no, issue_no, y, displayVersion, fontSize, version, versionNo)
            i += 1
            # place_holder += 1

    pdf_e.output(f"e_dummy_{equitable['serviceData']['policyNo']}_{equitable['customer']['certMembershipId']}.pdf")

    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        filePath = os.path.join(application_path, "Equitable_template.pdf")
        tempFile = f"{application_path}/Equitable_template_{equitable['serviceData']['policyNo']}_{equitable['customer']['certMembershipId']}.pdf"
        shutil.copy2(filePath, tempFile)
    except:
        print(f"ERROR: ttf file not found {filePath}")
    file1 = open(tempFile, 'rb')
    test = PdfFileReader(file1)
    file2 = open(f"e_dummy_{equitable['serviceData']['policyNo']}_{equitable['customer']['certMembershipId']}.pdf", 'rb')
    test1 = PdfFileReader(file2)
    total_pages = test1.getNumPages()

    g = 0
    while g < total_pages:
        output.add_page(test.getPage(0))
        g += 1
    output.write(f"equitable_template_duplicate_{equitable['serviceData']['policyNo']}_{equitable['customer']['certMembershipId']}.pdf")

    file3 = open(f"equitable_template_duplicate_{equitable['serviceData']['policyNo']}_{equitable['customer']['certMembershipId']}.pdf", 'rb')
    test3 = PdfFileReader(file3)

    x = 0
    while x < total_pages:
        page = test3.getPage(x)
        page1 = test1.getPage(x)
        page.mergePage(page1)
        writer.add_page(page)
        x += 1

    outputstream = open(f"{equitable['filePath']}{equitable['fileName']}", 'wb')
    writer.write(outputstream)
    outputstream.close()
    file1.close()
    file2.close()
    file3.close()
    os.remove(f"e_dummy_{equitable['serviceData']['policyNo']}_{equitable['customer']['certMembershipId']}.pdf")
    os.remove(f"equitable_template_duplicate_{equitable['serviceData']['policyNo']}_{equitable['customer']['certMembershipId']}.pdf")
    os.remove(tempFile)


pdf_g = FPDF('P', 'pt', [611, 791])
pdf_e = FPDF('P', 'pt', [595, 842])

# String version
# json_encoded_string = sys.argv[1]
# json_decoded_string = unquote(json_encoded_string)
# data = json.loads(json_decoded_string)

# Version No
version = "v1.1"

# File version
json_file = sys.argv[1]
with open(json_file, 'r') as myFile:
    json_file = myFile.read()
data = json.loads(json_file)

if data['service'].upper() == "GREENSHIELD":
    print_card_g(data, version)
elif data['service'].upper() == "EQUITABLE":
    print_card_e(data, version)
else:
    print(f"Please check the service name")

# While doing the output for equitable life, we will need to create two different variables for PDFWriter that way the final pdf won't have the pages that are
# being duplicated (same PDFWriter object will add the pages being duplicated to final pdf i.e. the first few pages will be the duplicate template pages and then
# output pages)
# Need to write the code that creates the copy of the templates files (greenshield and equitablelife) and changes the names of the output files so that they contain
# first name and date of birth - for easier distinction
