import sys
import base64
from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader
import os.path
import shutil
from PIL import Image
from io import BytesIO


def signature(string, fileName):
    decoded_data = base64.b64decode(string)
    image = Image.open(BytesIO(decoded_data))
    original_width, original_height = image.size
    max_width = 300
    max_height = 150

    image = image.resize((max_width, max_height), resample=Image.Resampling.LANCZOS)
    image.save(fileName, format='PNG')



def first_page(data, pdf):

    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
        tempFont = f'{application_path}/tempfont.ttf'
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {fontPath}")

    pdf.add_font('dejavu', '', tempFont)

    pdf.add_page()
    pdf.set_font("dejavu", '', 9)

    # TODO: Add check for Section 1
    pdf.text(1.25, 8.5, "The Groupbenefitz Platform Inc.")      # Name of PolicyHolder
    pdf.text(1.25, 9.5, "814458")                                 # Policy Number
    pdf.text(8, 9.5, "002")
    pdf.text(14.6, 9.5, "E")

    # pdf.text(1.25, 10.5, "Certifcate Number")

    pdf.text(1.25, 11.5, "40")
    pdf.text(8, 11.5, "Principal")
    pdf.text(1.25, 12.55, "01/01/2000")

    # TODO: CLean up Section 2
    pdf.text(1.25, 14.35, f"{data['first_name']} {data['last_name']}")
    pdf.text(1.25, 15.35, "06/14/1956")

    # TODO: Add check for gender
    pdf.set_font_size(8)
    pdf.text(8.52, 14.92, u'\u2713')

    # TODO: Add check for language
    pdf.text(15.05, 15.36, u'\u2713')

    pdf.set_font_size(9)
    pdf.text(1.22, 16.35, "39 Prince Rupert Avenue")
    pdf.text(8.52, 16.35, "Toronto")
    pdf.text(15.0, 16.35, "Ontario")
    pdf.text(18.1, 16.35, "M6P 2A8")

    pdf.text(1.22, 17.35, "brendon.hemily@gmail.com")

    pdf.set_font_size(8)
    # TODO: Add check for provincial health coverage
    pdf.text(13.39, 23.26, u'\u2713')
    pdf.set_font_size(9)

    # ------ PAGE 2 --------
    pdf.add_page()
    pdf.set_font_size(8)
    # TODO: Add check for coverage
    # pdf.text(1.5, 6.63, u'\u2713')
    # pdf.text(2.78, 6.63, u'\u2713')
    pdf.text(1.5, 7.28, u'\u2713')
    pdf.text(2.78, 7.28, u'\u2713')

    # TODO: Add check for spouse insurance info
    # pdf.text(3.58, 10.6, u'\u2713')
    pdf.text(4.73, 10.6, u'\u2713')

    pdf.set_font_size(9)
    # TODO: Add spouse details
    pdf.text(1.25, 16.85, "Karen Levy")
    pdf.text(12.2, 17.3, "04/05/1961")

    # TODO: Add check for spouse gender
    pdf.set_font_size(8)
    # pdf.text(16.12, 16.9, u'\u2713')
    pdf.text(17.42, 16.9, u'\u2713')

    pdf.set_font_size(9)
    pdf.add_page()

    pdf.add_page()
    pdf.text(15.2, 5.1, "12/01/2023")
    signature_base64 = "data:image/png;base64,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"
    signature_file_name = f'signature.png'  # Need to be updated for generating and updating
    signature(signature_base64.split(',')[1], signature_file_name)
    pdf.image(signature_file_name, 1.5, 4.3, 3, 1.2)

    pdf.output('dummy_equitable.pdf')
    merging_pdf()

def merging_pdf():
    writer = PdfWriter()
    try:
        output_path = f"equitable_sample.pdf"
        try:
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            templateFilePath = os.path.join(application_path, "Equitable Life Application Form.pdf")
            copyFile = f'Temp Equitable Form.pdf'
            shutil.copy2(templateFilePath, copyFile)
        except:
            print(f"ERROR: template.pdf file not found {templateFilePath}")

        file1 = open(copyFile, 'rb')
        test1 = PdfReader(file1)
        file2 = open(f'dummy_equitable.pdf', 'rb')
        test2 = PdfReader(file2)

        no_of_pages = len(test2.pages)

        i = 0
        for i in range(no_of_pages):
            page = test1.pages[i]
            page1 = test2.pages[i]
            page.merge_page(page1)
            writer.add_page(page)

        # page2 = test1.pages[1]
        # page3 = test2.pages[1]
        # page2.merge_page(page3)
        # writer.add_page(page2)

        outputStream = open(output_path, 'wb')
        writer.write(outputStream)
        outputStream.close()

        file1.close()
        file2.close()

        os.remove(f'dummy_equitable.pdf')
        os.remove(copyFile)

    except Exception as e:
        print(f"ERROR: {e}")


def generate_equitable_roe(data):
    pdf = FPDF('P', 'cm', 'Letter')
    first_page(data, pdf)