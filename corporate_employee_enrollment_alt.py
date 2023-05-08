import json
import sys
import base64
import warnings
import re
from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader
import os.path
import shutil
import logging
from urllib.parse import unquote


def warn(*args, **kwargs):
    pass


# from pdf2image import convert_from_path

# Checking for gender and replacing the corresponding text
def gender_text(gender):
    if gender.upper() == 'FEMALE':
        return 'F'
    elif gender.upper() == 'MALE':
        return 'M'
    elif gender.upper() == 'UNDISCLOSED':
        return 'U'
    else:
        return 'NB'


# checking for different true and false fields and replacing them with Y and N respectively
def check(text):
    if text == True:
        return 'Y'
    elif text == False:
        return 'N'
    else:
        return 'N'


# changing the price to a correct format and right justifying the outcome
def price(price, length):
    if isinstance(price, float) or isinstance(price, int):
        price = float(price)
    else:
        price = float(price.replace(',', ''))
    # price = format(round(price, 2), '.2f')
    price = '{:,.2f}'.format(price)
    temp = f"${price}"
    if len(temp) != length:
        l = length - len(temp)
        temp = temp.rjust(length + l, " ")
    return temp


# converting base64 into png
def signature(string, fileName):
    decoded_data = base64.b64decode(string)
    img_file = open(fileName, 'wb')
    img_file.write(decoded_data)
    img_file.close()


def split_string(pdf, target_string, target_length):
    temp_str = ""
    target_strs = []
    temp = target_string.split(" ")
    for word in temp:
        temp_str += word + " "
        temp_width = pdf.get_string_width(temp_str.strip())
        if temp_width >= target_length:
            target_strs.append(temp_str.strip()[:-len(word) - 1])
            temp_str = word + " "
    target_strs.append(temp_str.strip())
    return target_strs


# printing the plans on first and second page
def printing_plans(pdf, plan, pad_length, y, x_pad, exec_string, spouse_email):
    temp_planname = split_string(pdf, plan['planname'], 7.72)
    y_temp = 0
    for temp in temp_planname:
        pdf.text(1.3, y + y_temp, temp)
        y_temp += 0.35

    temp_details = split_string(pdf, exec_string, 4.95)
    y_temp = 0
    for temp in temp_details:
        pdf.text(9.2, y + y_temp, temp)
        y_temp += 0.35
    # if spouse_email is not None:
    if (len(spouse_email) > 0) and (len(spouse_email) <= 36):
        pdf.text(9.2, y + y_temp, spouse_email[0:36])
    else:
        pdf.text(9.2, y + y_temp, spouse_email[0:36])
        pdf.text(9.2, y + y_temp + 0.35, spouse_email[36:len(spouse_email)])

    pdf.text(14.75 + x_pad, y, price(plan['planPrice'], pad_length))
    pdf.text(16.15 + x_pad, y, price(plan['tax'], pad_length))
    pdf.text(17.6 + x_pad, y, price(plan['totalPrice'], pad_length))
    pdf.text(19.05 + x_pad, y, price(plan['employeeShare'], pad_length))


# printing the list of children on first and second page
def printing_children(pdf, child, y):
    pdf.text(1.5, y, 'C')
    pdf.text(2.2, y, child['first_name'])  # first name
    pdf.text(4.7, y, child['last_name'])  # last name
    pdf.text(7.5, y, gender_text(child['gender']))  # gender
    pdf.text(8.5, y, child['date_of_birth'])  # date of birth
    pdf.text(11.1, y, check(child['is_child_having_healthcard']))  # checking if child is having healthcare
    # pdf.text(12.35, y, child['child_carrier_name'] or "N/A")  # child's healthcare provider name
    if child['child_carrier_name'] is not None:
        temp_child_carrier = split_string(pdf, child['child_carrier_name'], 2.51)
        y_temp = 0
        for temp in temp_child_carrier:
            pdf.text(12.35, y + y_temp, temp)
            y_temp += 0.35
    else:
        pdf.text(12.35, y, "N/A")
    pdf.text(15.45, y, check(child['enrolledInUniversity']))  # check if child is enrolled in university
    if child['graduationDay'] is None:
        pdf.text(17.3, y, "N/A")
    else:
        pdf.text(16.9, y, child['graduationDay'])  # graduation day
    pdf.text(19.45, y, check(child['isDisabled']))  # special needs


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


# Main form
def first_page(data, versionNo):
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
        tempFont = f'{application_path}/DejaVuSansCondensed_{data["first_name"]}_{data["date_of_birth"]}.ttf'
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {fontPath}")
    line_break_width = 0.35
    new_line_width = 0.35
    pdf.add_font('dejavu', '', tempFont, uni=True)
    pdf2.add_font('dejavu', '', tempFont)
    pdf.add_page()
    pdf.set_font('dejavu', '', 9)
    pdf.image(data['companyLogo'], 15, 0.7, 3, 2)
    full_name = f"{data['first_name']} {data['last_name']}"
    pdf.text(1.4, 5.35, full_name)  # Full Name
    checking_length(data['company_name'], 11.1, 5.35, pdf)
    checking_length(data['email'], 1.4, 6.8, pdf)
    pdf.set_font_size(9)
    pdf.text(16, 5.35, data['date_of_hiring'])  # Date of Hire
    pdf.text(6.25, 6.8, data['phone_number'] or "")  # Phone number
    # pdf.text(11.1, 6.8, data['job_title'] or "")  # employee title
    checking_length(data['job_title'], 11.1, 6.8, pdf)
    pdf.set_font_size(9)
    pdf.text(16, 6.8, str(data['hours_per_week']) or "")  # No of hours
    pdf.text(1.4, 8.3, data['date_of_birth'])  # Date of birth
    pdf.text(6.25, 8.3, data['gender'])  # Gender
    pdf.text(1.4, 10.8, data['street_address_line1'])  # Address line 1
    pdf.text(11.1, 10.8, data['street_address_line2'] or "")  # Address line 2
    pdf.text(1.4, 12.25, data['apt'] or "")  # apartment no
    pdf.text(6.25, 12.25, data['city'])  # city
    pdf.text(11.1, 12.25, data['province'])  # province
    pdf.text(16, 12.25, data['postal_code'])  # postal code
    # Spouse information
    y = 14.8
    dependent_line_counter = 0
    # Checking if there is an email available for the spouse
    if data['spouse_details'].get('email') is not None:
        spouse_email = f"Spouse email: {data['spouse_details'].get('email')}"
    else:
        spouse_email = ""
    # child_counter = 1
    if data['having_spouse'] == True:
        pdf.set_font('dejavu', '', 7.8)
        pdf.text(1.5, y, 'S')
        pdf.text(2.2, y, data['spouse_details']['first_name'].capitalize())  # first name
        pdf.text(4.7, y, data['spouse_details']['last_name'].capitalize())  # last name
        pdf.text(7.5, y, gender_text(data['spouse_details']['gender']))  # gender
        pdf.text(8.5, y, data['spouse_details']['date_of_birth'])  # date of birth
        pdf.text(11.1, y, check(data['spouse_details']['is_spouse_having_healthcard']))  # checking for healthcare
        pdf.text(15.3, y, 'N/A')  # post sec student (N/A) for spouse
        pdf.text(17.3, y, 'N/A')  # graduation day (N/A) for spouse
        pdf.text(19.3, y, 'N/A')  # special needs (N/A) for spouse
        # healthcare provider name
        if data['spouse_details']['spouse_carrier_name'] is not None:
            temp_spouse_carrier = split_string(pdf, data['spouse_details']['spouse_carrier_name'], 2.51)
            y_temp = 0
            for temp in temp_spouse_carrier:
                pdf.text(12.35, y + y_temp, temp)
                y_temp += 0.35
            if len(temp_spouse_carrier) > 1:
                y += line_break_width * (len(temp_spouse_carrier) - 1)
            else:
                y += 0
        else:
            pdf.text(12.35, y, "N/A")
            dependent_line_counter += 1
        y += 0.45

    # 4 different check marks in the form
    pdf.set_font('dejavu', '', 11)
    if data['working_20hours'] == True:  # working 20 hours
        pdf.text(11.05, 8, u'\u2713')
    if data['provincial_health_coverage'] == True:  # checking for provincial health coverage
        pdf.text(11.05, 8.68, u'\u2713')
    if data['termsandconditions'] == True:  # terms and conditions
        pdf.text(1.3, 22.57, u'\u2713')
    if data['disclouseradvisor'] == True:  # advisor disclosure
        pdf.text(11.05, 22.57, u'\u2713')

    # Dependent Information

    pdf.set_font('dejavu', '', 7.8)
    pdf.set_text_color(0, 0, 0)
    page_check = 0
    child_second_page = False
    if int(len(data['children_details'])) > 0:
        y1 = 5.8
        for child in data['children_details']:
            if child['child_carrier_name'] is not None:
                temp_child_carrier = split_string(pdf, child['child_carrier_name'], 2.51)
                if len(temp_child_carrier) > 1:
                    ytemp = line_break_width * len(temp_child_carrier)
                else:
                    ytemp = 0
            else:
                ytemp = 0

            if y + ytemp < 17.7:
                printing_children(pdf, child, y)
                if child['child_carrier_name'] is not None:
                    temp_child_carrier = split_string(pdf, child['child_carrier_name'], 2.51)

                    if len(temp_child_carrier) > 1:
                        y += line_break_width * (len(temp_child_carrier) - 1)
                    else:
                        y += 0
                y += new_line_width
                # child_counter += 1
            else:
                child_second_page = True
                if page_check == 0:
                    pdf2.add_page()
                    page_check = 1
                pdf2.set_font('dejavu', '', 7.8)
                printing_children(pdf2, child, y1)
                if child['child_carrier_name'] is not None:
                    temp_child_carrier = split_string(pdf2, child['child_carrier_name'], 2.51)
                    if len(temp_child_carrier) > 1:
                        y1 += line_break_width * (len(temp_child_carrier) - 1)
                    else:
                        y1 += 0
                y1 += new_line_width
    # plans and prices
    # print(y)

    plan_second_page = False
    if int(len(data['plans'])) > 0:
        # i = 0
        y = 19.5
        plan_line_counter = 0
        plan_counter = 0
        if isinstance((data['totalAmount']), float) or isinstance((data['totalAmount']), int):
            pad_length = len(str(format(float(data['totalAmount']), ".2f"))) + 1
        else:
            pad_length = len(str(format(float(data['totalAmount'].replace(',', '')), ".2f"))) + 1
        x_pad = 0.15 * (7 - pad_length)
        if child_second_page is True:
            y1 = 14.55
        else:
            pdf2.add_page()
            pdf2.image(data['companyLogo'], 15, 0.7, 3, 2)
            pdf2.set_font('dejavu', '', 7.8)
            y1 = 5.8
        for plan in data['plans']:
            if "planOptions" in plan:
                planOptions = plan['planOptions']
                if len(planOptions) > 0:
                    for option in planOptions:
                        if option['value'].lower() == 'yes':
                            condition = "Year-Round Family Virtual Care activated"
                        elif option['value'].lower() == 'no':
                            condition = "Contact advisor to activate Year-Round Family Virtual Care"
                        else:
                            clinic_name = option['value']
                    exec_string = f"{plan['details']} - {clinic_name} - {condition}"
                else:
                    exec_string = f"{plan['details']}"
            else:
                exec_string = f"{plan['details']}"
            temp_planname = split_string(pdf, plan['planname'], 7.72)
            temp_details = split_string(pdf, exec_string, 4.95)
            if len(temp_planname) > 1 or len(temp_details) > 1:
                if len(temp_planname) > len(temp_details):
                    plan_line_counter += (len(temp_planname))
                else:
                    plan_line_counter += (len(temp_details))
            else:
                plan_line_counter += 1

            # if spouse_email is not None:
            if len(spouse_email) == 0:
                plan_line_counter += 0
            elif 0 < len(spouse_email) <= 36:
                plan_line_counter += 1
            else:
                plan_line_counter += 1

            if plan_line_counter <= 4 and plan_counter < 3:
                printing_plans(pdf, plan, pad_length, y, x_pad, exec_string, spouse_email)
                if len(temp_planname) > 1 or len(temp_details) > 1:
                    if len(temp_planname) > len(temp_details):
                        y += line_break_width * (len(temp_planname) - 1)
                    else:
                        y += line_break_width * (len(temp_details) - 1)
                else:
                    y += 0
                if len(spouse_email) == 0:
                    y += 0
                elif 0 < len(spouse_email) <= 36:
                    y += line_break_width
                else:
                    y += 2 * line_break_width
                y += new_line_width
                plan_counter += 1
            else:
                plan_second_page = True
                printing_plans(pdf2, plan, pad_length, y1, x_pad, exec_string, spouse_email)

                if len(temp_planname) > 1 or len(temp_details) > 1:
                    if len(temp_planname) > len(temp_details):
                        y1 += line_break_width * (len(temp_planname) - 1)
                    else:
                        y1 += line_break_width * (len(temp_details) - 1)
                else:
                    y1 += 0
                if len(spouse_email) == 0:
                    y1 += 0
                elif 0 < len(spouse_email) <= 36:
                    y1 += line_break_width
                else:
                    y1 += 2 * line_break_width
                y1 += new_line_width
                plan_counter += 1
        if plan_second_page is True:
            pdf2.text(17.6 + x_pad, y1 - 0.05, price(data['totalAmount'], pad_length))
        else:
            pdf.text(17.6 + x_pad, y - 0.05, price(data['totalAmount'], pad_length))

    # End
    pdf.set_font('dejavu', '', 9)
    pdf.text(1.4, 24.15, data['paymentMethod'])  # payment method
    pdf.text(11.1, 24.15, data['planEnrollmentDate'])  # enrollment date
    pdf.text(1.4, 25.6, data['advisorName'])  # advisor name
    if data['signature'] is not None and 'data:image/png;base64,' in data['signature']:
        signature_file_name = f'signature_{data["first_name"]}_{data["date_of_birth"]}.png'
        signature(data['signature'].split(',')[1], signature_file_name)
        pdf.image(signature_file_name, 11.2, 24.8, 3, 1.2)  # signature
        os.remove(signature_file_name)

    pdf.set_font('dejavu', '', 10)
    pdf.set_text_color(255, 255, 255)
    pdf2.set_font('dejavu', '', 10)
    pdf2.set_text_color(255, 255, 255)
    if child_second_page is True:
        pdf.text(12.7, 13.6, f"({int(len(data['children_details']))} See Addendum)")
    if plan_second_page is True:
        pdf.text(13, 18.45, f"({len(data['plans'])} See Addendum)")
    if child_second_page is True and plan_second_page is False:
        pdf2.text(12.7, 4.65, '(Continued)')
    elif child_second_page is False and plan_second_page is True:
        pdf2.text(13, 4.8, '(Continued)')
    elif child_second_page is True and plan_second_page is True:
        pdf2.text(12.7, 4.65, '(Continued)')
        pdf2.text(13, 13.5, '(Continued)')
    pdf.set_font_size(int(data['fontSize']))
    pdf2.set_font_size(int(data['fontSize']))
    # pdf.set_text_color(0,0,0)
    # pdf2.set_text_color(0, 0, 0)
    if data['displayVersion']:
        pdf.text(0.35, 27.8, f"{versionNo}_{data['version']}")
        pdf2.text(0.35, 27.8, f"{versionNo}_{data['version']}")

    pdf.output(f'dummy_{data["first_name"]}_{data["date_of_birth"]}.pdf')
    pdf2.output(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf')
    os.remove(tempFont)

    merging_pdf(child_second_page, plan_second_page, data)


# merging the template with the text generated in dummy pdfs
def merging_pdf(child_second_page, plan_second_page, data):
    writer = PdfWriter()
    try:
        output_path = f"{data['filePath']}{data['fileName']}"
        try:
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            templateFilePath = os.path.join(application_path, "template-corporate-employee-gavin.pdf")
            copyFile = f'{application_path}/corporate_enrollment_template_{data["first_name"]}_{data["date_of_birth"]}.pdf'
            shutil.copy2(templateFilePath, copyFile)
        except:
            print(f"ERROR: template.pdf file not found {templateFilePath}")
        file1 = open(copyFile, 'rb')
        test = PdfReader(file1)
        file2 = open(f'dummy_{data["first_name"]}_{data["date_of_birth"]}.pdf', 'rb')
        test1 = PdfReader(file2)

        page = test.pages[0]
        page1 = test1.pages[0]
        page.merge_page(page1)
        writer.add_page(page)

        if os.path.exists(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf'):
            file3 = open(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf', 'rb')
            test4 = PdfReader(file3)
            if child_second_page is True and plan_second_page is False:
                page3 = test.pages[2]
            elif child_second_page is False and plan_second_page is True:
                page3 = test.pages[1]
            elif child_second_page is True and plan_second_page is True:
                page3 = test.pages[3]
            else:
                page3 = None

            if page3 != None:
                page4 = test4.pages[0]
                page3.merge_page(page4)
                writer.add_page(page3)

        outputstream = open(output_path, 'wb')
        writer.write(outputstream)
        outputstream.close()

        file1.close()
        file2.close()
        os.remove(f'dummy_{data["first_name"]}_{data["date_of_birth"]}.pdf')
        os.remove(copyFile)
        if os.path.exists(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf'):
            file3.close()
            os.remove(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf')
    except Exception as e:
        print(f"ERROR: {e}")

    # images = convert_from_path('enrollment.pdf', dpi=300)
    # for i in range(len(images)):
    #     images[i].save('page' + str(i) + '.jpg','JPEG')
    #
    # test = PdfFileReader(open('enrollment.pdf', 'rb'))
    # total_pages = test.getNumPages()
    #
    # for i in range(total_pages):
    #     pdf3.add_page()
    #     pdf3.image('page' + str(i) + '.jpg',0,0,22,28)
    #     os.remove('page' + str(i) + '.jpg')
    #
    # pdf3.output('enrollment.pdf')


warnings.warn = warn
warnings.filterwarnings("ignore", category=UserWarning, message="FFTM NOT subset.*")
warnings.filterwarnings('ignore', category=Warning)
# warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="FFTM NOT subset; don't know how to subset; dropped")
logging.getLogger("fpdf2").setLevel(logging.ERROR)


# String version
json_encoded_string = sys.argv[1]
json_decoded_string = unquote(json_encoded_string)
data = json.loads(json_decoded_string)

# File version
# json_file = sys.argv[1]
# with open(json_file, 'r') as myFile:
#     json_file = myFile.read()
# data = json.loads(json_file)

versionNo = "v1.0"
pdf = FPDF('P', 'cm', 'letter')
pdf2 = FPDF('P', 'cm', 'letter')
pdf3 = FPDF('P', 'cm', 'letter')
first_page(data, versionNo)


