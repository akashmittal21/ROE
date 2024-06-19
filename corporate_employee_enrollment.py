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
from urllib.parse import unquote

from equitable_roe import generate_equitable_roe
from provincial_roe import generate_provincial_roe


def warn(*args, **kwargs):
    pass


def process_input(value):
    if isinstance(value, str):
        if '$' in value:
            try:
                value_as_float = round(float(value.replace('$', '')), 2)
                return f"${value_as_float}"
            except ValueError:
                return "Invalid input. Please provide a valid number or a string with '$'."
        else:
            try:
                value_as_float = round(float(value), 2)
                return f"${value_as_float}"
            except ValueError:
                return "Invalid input. Please provide a valid number or a string with '$'."
    elif isinstance(value, (int, float)):
        return f"${round(value, 2)}"
    else:
        return "Invalid input type. Please provide a string, number, or float."


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
    if text is True:
        return 'Y'
    elif text is False:
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

    pdf.text(14.95 + x_pad, y, price(plan['planPrice'], pad_length))
    pdf.text(16.45 + x_pad, y, price(plan['tax'], pad_length))
    pdf.text(18.35 + x_pad, y, price(plan['totalPrice'], pad_length))


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
    if 'companyLogo' in data:
        if data['companyLogo'] is not None and data['companyLogo'] != "":
            try:
                pdf.image(data['companyLogo'], 15, 0.7, 3, 1.5)
            except:
                print(f"Company Logo not found in {data['companyLogo']}")
    full_name = f"{data['first_name']} {data['last_name']}"
    pdf.text(1.4, 5.35, full_name)  # Full Name
    checking_length(data['company_name'], 11.1, 5.35, pdf)
    if 'employerName' in data:
        checking_length(data['employerName'], 16, 5.35, pdf)
    checking_length(data['email'], 1.4, 6.8, pdf)
    pdf.set_font_size(9)
    pdf.text(16, 6.8, data['date_of_hiring'])  # Date of Hire
    pdf.text(6.25, 6.8, data['phone_number'] or "")  # Phone number
    # pdf.text(11.1, 6.8, data['job_title'] or "")  # employee title
    checking_length(data['job_title'], 11.1, 6.8, pdf)
    pdf.set_font_size(9)
    pdf.text(18.6, 6.8, str(data['hours_per_week']) or "")  # No of hours
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
    if data['having_spouse'] is True:
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

    if "workingProvince" in data:
        pdf.set_y(7.7)
        pdf.set_x(11)
        pdf.set_font_size(9)
        pdf.multi_cell(2.5, 1, data.get("workingProvince"), border=0, max_line_height=0.4)

    # 4 different check marks in the form
    pdf.set_font('dejavu', '', 11)
    if data['working_20hours'] is True:  # working 20 hours
        pdf.text(13.8, 7.86, u'\u2713')
    if data['provincial_health_coverage'] is True:  # checking for provincial health coverage
        pdf.text(13.8, 8.65, u'\u2713')

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

    # plan_second_page = False
    # if int(len(data['plans'])) > 0:
    #     # i = 0
    #     y = 19.5
    #     plan_line_counter = 0
    #     plan_counter = 0
    #     if isinstance((data['totalAmount']), float) or isinstance((data['totalAmount']), int):
    #         pad_length = len(str(format(float(data['totalAmount']), ".2f"))) + 1
    #     else:
    #         pad_length = len(str(format(float(data['totalAmount'].replace(',', '')), ".2f"))) + 1
    #     x_pad = 0.15 * (7 - pad_length)
    #     if child_second_page is True:
    #         y1 = 14.55
    #     else:
    #         pdf2.add_page()
    #         pdf2.set_font('dejavu', '', 7.8)
    #         y1 = 5.8
    #     for plan in data['plans']:
    #         if "planOptions" in plan:
    #             planOptions = plan['planOptions']
    #             if len(planOptions) > 0:
    #                 for option in planOptions:
    #                     if option['value'].lower() == 'yes':
    #                         condition = "Year-Round Family Virtual Care activated"
    #                     elif option['value'].lower() == 'no':
    #                         condition = "Contact advisor to activate Year-Round Family Virtual Care"
    #                     else:
    #                         clinic_name = option['value']
    #                 exec_string = f"{plan['details']} - {clinic_name} - {condition}"
    #             else:
    #                 exec_string = f"{plan['details']}"
    #         else:
    #             exec_string = f"{plan['details']}"
    #         temp_planname = split_string(pdf, plan['planname'], 7.72)
    #         temp_details = split_string(pdf, exec_string, 4.95)
    #         if len(temp_planname) > 1 or len(temp_details) > 1:
    #             if len(temp_planname) > len(temp_details):
    #                 plan_line_counter += (len(temp_planname))
    #             else:
    #                 plan_line_counter += (len(temp_details))
    #         else:
    #             plan_line_counter += 1
    #
    #         # if spouse_email is not None:
    #         if len(spouse_email) == 0:
    #             plan_line_counter += 0
    #         elif 0 < len(spouse_email) <= 36:
    #             plan_line_counter += 1
    #         else:
    #             plan_line_counter += 1
    #
    #         if plan_line_counter <= 4 and plan_counter < 3:
    #             printing_plans(pdf, plan, pad_length, y, x_pad, exec_string, spouse_email)
    #             if len(temp_planname) > 1 or len(temp_details) > 1:
    #                 if len(temp_planname) > len(temp_details):
    #                     y += line_break_width * (len(temp_planname) - 1)
    #                 else:
    #                     y += line_break_width * (len(temp_details) - 1)
    #             else:
    #                 y += 0
    #             if len(spouse_email) == 0:
    #                 y += 0
    #             elif 0 < len(spouse_email) <= 36:
    #                 y += line_break_width
    #             else:
    #                 y += 2 * line_break_width
    #             y += new_line_width
    #             plan_counter += 1
    #         else:
    #             plan_second_page = True
    #             printing_plans(pdf2, plan, pad_length, y1, x_pad, exec_string, spouse_email)
    #
    #             if len(temp_planname) > 1 or len(temp_details) > 1:
    #                 if len(temp_planname) > len(temp_details):
    #                     y1 += line_break_width * (len(temp_planname) - 1)
    #                 else:
    #                     y1 += line_break_width * (len(temp_details) - 1)
    #             else:
    #                 y1 += 0
    #             if len(spouse_email) == 0:
    #                 y1 += 0
    #             elif 0 < len(spouse_email) <= 36:
    #                 y1 += line_break_width
    #             else:
    #                 y1 += 2 * line_break_width
    #             y1 += new_line_width
    #             plan_counter += 1
    #     if plan_second_page is True:
    #         pdf2.text(18.35 + x_pad, y1 - 0.05, price(data['totalAmount'], pad_length))
    #     else:
    #         pdf.text(18.35 + x_pad, y - 0.05, price(data['totalAmount'], pad_length))

    pdf.set_font(size=7.8)
    border = 0
    cell_height = 0.55
    # if len(data['plans']) > 0:
    y_cc = 23.4
    y_cp = 18.98
    y_ep = 4.53
    plan_second_page = False
        # for plan in data['plans']:
        #     if "cp_plans" in plan:
    pdf.set_y(y_cp)
    lineBreak = False
    pdf_cp = pdf
    if len(data['cp_plans']) > 0:
        for cp_plan in data['cp_plans']:
            if "planOptions" in cp_plan:
                planOptions = cp_plan["planOptions"]
                if len(planOptions) > 0:
                    for option in planOptions:
                        if option['value'].lower() == 'yes':
                            condition = "Year-Round Family Virtual Care activated"
                        elif option['value'].lower() == 'no':
                            condition = "Contact advisor to activate Year-Round Family Virtual Care"
                        else:
                            clinic_name = option['value']
                    cp_exec_string = f"{cp_plan['details']} - {clinic_name} - {condition}"
                    lineBreak = True
                else:
                    cp_exec_string = f"{cp_plan['details']}"
                    lineBreak = False
            else:
                cp_exec_string = f"{cp_plan['details']}"
                lineBreak = False

            if pdf_cp.get_y() + (cell_height * 2) > 21.3:
                if child_second_page is False:
                    plan_second_page = True
                    pdf.set_text_color(255, 255, 255)
                    pdf.set_font_size(10)
                    pdf.text(14.5, 18.3, "(Check Addendum)")
                    pdf.set_text_color(0, 0, 0)
                    pdf_cp = pdf2
                    pdf2.add_page()
                    pdf2.set_y(5.4)

            pdf_cp.set_font('dejavu', '', 7.8)
            pdf_cp.set_x(1.3)
            pdf_cp.multi_cell(5.9, cell_height, cp_plan['planname'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
            pdf_cp.multi_cell(6.1, cell_height, cp_exec_string, border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
            # pdf.multi_cell(1.6, cell_height, f"", border=border, align='R', new_x="RIGHT", new_y="TOP")
            # pdf.multi_cell(3.3, cell_height, f"C:${cp_plan['companyShare']} E:${cp_plan['employeeShare']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
            if lineBreak is True:
                pdf_cp.ln(cell_height * 2.1)
            else:
                pdf_cp.ln(cell_height)
            for product in cp_plan['products']:
                if "employerName" in data and data["employerName"] != "":
                    planPrice = ""
                    planTax = ""
                    planTotal = ""
                else:
                    planPrice = f"${product['price']}"
                    planTax = f"${product['tax']}"
                    planTotal = f"${product['total']}"
                pdf_cp.set_x(1.6)
                pdf_cp.multi_cell(5.6, cell_height, product['name'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
                pdf_cp.multi_cell(6.4, cell_height, product['planCoverage'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
                # pdf_cp.multi_cell(6.9, cell_height, product['planCoverage'], border=border, align='L', new_x="RIGHT",
                #                   new_y="TOP", max_line_height=0.3)
                # pdf_cp.multi_cell(5, cell_height, f"Paid by Company", border=border, align='L', new_x="RIGHT",
                #                   new_y="TOP")
                pdf_cp.multi_cell(1.5, cell_height, planPrice, border=border, align='R', new_x="RIGHT", new_y="TOP")
                # pdf.multi_cell(3.3, cell_height, f"", border=border, align='R', new_x="RIGHT", new_y="TOP")
                pdf_cp.multi_cell(2.8, cell_height, planTax, border=border, align='R', new_x="RIGHT", new_y="TOP")
                total_cell_x = pdf_cp.get_x()
                pdf_cp.multi_cell(2.2, cell_height, planTotal, border=border, align='R', new_x="RIGHT", new_y="TOP")
                pdf_cp.ln(cell_height)
        #
        # if pdf_cp.get_y() < 21.38:
        if "employerName" in data and data["employerName"] != "":
            pass
        else:
            pdf_cp.set_x(total_cell_x)
            pdf_cp.multi_cell(2.2, cell_height, f"{process_input(data['cp_totalAmount'])}", border="TB", align='R', new_x="RIGHT", new_y="TOP")

            # elif "cc_plans" in plan:
    pdf.set_y(y_cc)
    pdf_cc = pdf
    if len(data['cc_plans']) > 0:
        for cc_plan in data['cc_plans']:
            if "planOptions" in cc_plan:
                planOptions = cc_plan["planOptions"]
                if len(planOptions) > 0:
                    for option in planOptions:
                        if option['value'].lower() == 'yes':
                            condition = "Year-Round Family Virtual Care activated"
                        elif option['value'].lower() == 'no':
                            condition = "Contact advisor to activate Year-Round Family Virtual Care"
                        else:
                            clinic_name = option['value']
                    cc_exec_string = f"{cc_plan['details']} - {clinic_name} - {condition}"
                    lineBreak = True
                else:
                    cc_exec_string = f"{cc_plan['details']}"
                    lineBreak = False
            else:
                cc_exec_string = f"{cc_plan['details']}"
                lineBreak = False

            # pdf.line(0, 22, 23, 22)
            if pdf.get_y() + (cell_height * 2) > 25.8:
                if child_second_page is False:
                    if plan_second_page is False:
                        plan_second_page = True
                        pdf2.add_page()
                        pdf.set_text_color(255, 255, 255)
                        pdf.set_font_size(10)
                        pdf.text(16, 22.7, "(Check Addendum)")
                        pdf.set_text_color(0, 0, 0)
                        pdf_cc = pdf2
                        pdf2.set_y(11.8)

            pdf_cc.set_font('dejavu', '', 7.8)
            pdf_cc.set_x(1.3)
            pdf_cc.multi_cell(5.9, cell_height, cc_plan['planname'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
            pdf_cc.multi_cell(4.5, cell_height, cc_exec_string, border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
            pdf_cc.multi_cell(1.6, cell_height, f"", border=border, align='R', new_x="RIGHT", new_y="TOP")
            # pdf.multi_cell(3.3, cell_height, f"C:${cc_plan['companyShare']} E:${cc_plan['employeeShare']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
            if lineBreak is True:
                pdf_cc.ln(cell_height * 2.2)
            else:
                pdf_cc.ln(cell_height)
            for product in cc_plan['products']:
                pdf_cc.set_x(1.6)
                pdf_cc.multi_cell(5.6, cell_height, product['name'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
                pdf_cc.multi_cell(4.5, cell_height, product['planCoverage'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
                pdf_cc.multi_cell(1.6, cell_height, f"${product['price']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
                # pdf.multi_cell(3.3, cell_height, f"", border=border, align='R', new_x="RIGHT", new_y="TOP")
                pdf_cc.multi_cell(1.7, cell_height, f"${product['tax']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
                total_cell_x = pdf_cc.get_x()
                pdf_cc.multi_cell(1.9, cell_height, f"${product['total']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
                pdf_cc.multi_cell(1.6, cell_height, f"{process_input(cc_plan['companyShare'])}", border=border, align='R', new_x="RIGHT",
                               new_y="TOP")
                pdf_cc.multi_cell(1.6, cell_height, f"{process_input(cc_plan['employeeShare'])}", border=border, align='R', new_x="RIGHT",
                               new_y="TOP")
                pdf_cc.ln(cell_height)

        if pdf.get_y() > 25.56:
            pdf.set_y(25.44)

        if pdf_cc.get_y() < 25.9:
            pdf_cc.set_x(total_cell_x)
            pdf_cc.multi_cell(1.9, 0.5, f"{process_input(data['cc_totalAmount'])}", border="TB", align='R', new_x="RIGHT", new_y="TOP")
            pdf_cc.multi_cell(1.6, 0.5, f"{process_input(data['companyShareCC']['totalContribution'])}", border="TB", align='R',
                           new_x="RIGHT",
                           new_y="TOP")
            pdf_cc.multi_cell(1.6, 0.5, f"{process_input(data['employeeShareCC']['totalContribution'])}", border="TB", align='R',
                           new_x="RIGHT",
                           new_y="TOP")

            # elif "ep_plans" in plan:
    pdf.add_page()
    pdf.set_y(y_ep)
    pdf_ep = pdf
    if len(data['ep_plans']) > 0:
        for ep_plan in data['ep_plans']:

            if "planOptions" in ep_plan:
                planOptions = ep_plan["planOptions"]
                if len(planOptions) > 0:
                    for option in planOptions:
                        if option['value'].lower() == 'yes':
                            condition = "Year-Round Family Virtual Care activated"
                        elif option['value'].lower() == 'no':
                            condition = "Contact advisor to activate Year-Round Family Virtual Care"
                        else:
                            clinic_name = option['value']
                    ep_exec_string = f"{ep_plan['details']} - {clinic_name} - {condition}"
                    lineBreak = True
                else:
                    ep_exec_string = f"{ep_plan['details']}"
                    lineBreak = False
            else:
                ep_exec_string = f"{ep_plan['details']}"
                lineBreak = False

            if pdf_ep.get_y() + (cell_height * 2) > 6.8:
                if child_second_page is False:
                    if plan_second_page is False:
                        plan_second_page = True
                        pdf2.add_page()
                        pdf.set_text_color(255, 255, 255)
                        pdf.set_font_size(10)
                        pdf.text(16.5, 3.85, "(Check Addendum)")
                        pdf.set_text_color(0, 0, 0)
                        pdf_ep = pdf2
                        pdf2.set_y(18.2)

            pdf_ep.set_font('dejavu', '', 7.8)
            pdf_ep.set_x(1.3)
            pdf_ep.multi_cell(5.9, cell_height, ep_plan['planname'], border=border, align='L', new_x="RIGHT", new_y="TOP",
                           max_line_height=0.3)
            pdf_ep.multi_cell(6.1, cell_height, ep_exec_string, border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
            # pdf.multi_cell(1.6, cell_height, f"", border=border, align='R', new_x="RIGHT", new_y="TOP")
            # pdf.multi_cell(3.3, cell_height, f"C:${ep_plan['companyShare']} E:${ep_plan['employeeShare']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
            if lineBreak is True:
                pdf_ep.ln(cell_height * 2.1)
            else:
                pdf_ep.ln(cell_height * 1.2)
            for product in ep_plan['products']:
                pdf_ep.set_x(1.6)
                pdf_ep.multi_cell(5.6, cell_height, product['name'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
                pdf_ep.multi_cell(6.4, cell_height, product['planCoverage'], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3)
                pdf_ep.multi_cell(1.5, cell_height, f"${product['price']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
                # pdf.multi_cell(3.3, cell_height, f"", border=border, align='R', new_x="RIGHT", new_y="TOP")
                pdf_ep.multi_cell(2.8, cell_height, f"${product['tax']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
                total_cell_x = pdf_ep.get_x()
                pdf_ep.multi_cell(2.2, cell_height, f"${product['total']}", border=border, align='R', new_x="RIGHT", new_y="TOP")
                pdf_ep.ln(cell_height)

        if pdf_ep.get_y() < 6.93:
            pdf_ep.set_x(total_cell_x)
            pdf_ep.multi_cell(2.2, cell_height, f"{process_input(data['ep_totalAmount'])}", border="TB", align='R', new_x="RIGHT", new_y="TOP")
        else:
            pdf_ep.set_x(total_cell_x)
            pdf_ep.multi_cell(2.2, cell_height, f"{process_input(data['ep_totalAmount'])}", border="TB", align='R',
                              new_x="RIGHT", new_y="TOP")

    # End
    pdf.set_font('dejavu', '', 11)
    if data['termsandconditions'] is True:  # terms and conditions
        pdf.text(1.3, 8.1, u'\u2713')
    if data['disclouseradvisor'] is True:  # advisor disclosure
        pdf.text(11.05, 8.1, u'\u2713')
    pdf.set_font('dejavu', '', 9)
    if 'companyLogo' in data:
        if data['companyLogo'] is not None and data['companyLogo'] != "":
            try:
                pdf.image(data['companyLogo'], 15, 0.7, 3, 1.5)
            except:
                print(f"Company Logo not found in {data['companyLogo']}")
    pdf.text(1.4, 9.65, data['paymentMethod'])  # payment method
    pdf.text(11.1, 9.65, data['planEnrollmentDate'])  # enrollment date
    if "advisor" in data:
        if data['advisor'] != "":
            pdf.text(1.4, 11.1, data['advisor'])
        else:
            pdf.text(1.4, 11.1, data['advisorName'])
    else:
        pdf.text(1.4, 11.1, data['advisorName'])  # advisor name
    if data['signature'] is not None and 'data:image/png;base64,' in data['signature']:
        signature_file_name = f'signature_{data["first_name"]}_{data["date_of_birth"]}.png'
        signature(data['signature'].split(',')[1], signature_file_name)
        # pdf.rect(11, 10.52, 3.6, 1)
        pdf.image(signature_file_name, 11, 10.65, 3.6, 0.9)  # signature
        os.remove(signature_file_name)

    pdf.set_font('dejavu', '', 10)
    pdf.set_text_color(255, 255, 255)
    # pdf2.set_font('dejavu', '', 10)
    # pdf2.set_text_color(255, 255, 255)
    # if child_second_page is True:
    #     pdf.text(12.7, 13.6, f"({int(len(data['children_details']))} See Addendum)")
    # if plan_second_page is True:
    #     pdf.text(13, 18.45, f"({len(data['plans'])} See Addendum)")
    # if child_second_page is True and plan_second_page is False:
    #     pdf2.text(12.7, 4.65, '(Continued)')
    # elif child_second_page is False and plan_second_page is True:
    #     pdf2.text(13, 4.8, '(Continued)')
    # elif child_second_page is True and plan_second_page is True:
    #     pdf2.text(12.7, 4.65, '(Continued)')
    #     pdf2.text(13, 13.5, '(Continued)')
    pdf.set_font_size(int(data['fontSize']))
    # pdf2.set_font_size(int(data['fontSize']))
    # pdf.set_text_color(0,0,0)
    # pdf2.set_text_color(0, 0, 0)
    # if data['displayVersion']:
    #     pdf.text(0.35, 27.8, f"{versionNo}_{data['version']}")
    #     pdf2.text(0.35, 27.8, f"{versionNo}_{data['version']}")

    pdf.output(f'dummy_{data["first_name"]}_{data["date_of_birth"]}.pdf')
    pdf2.output(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf')
    os.remove(tempFont)

    if "attachEquitableForm" in data:
        if data.get("attachEquitableForm") is True:
            generate_equitable_roe(data, "employee")

    if "attachProvincialForm" in data:
        if data.get("attachProvincialForm") is True:
            generate_provincial_roe(data, 'employee')

    merging_pdf(child_second_page, data, plan_second_page)


# merging the template with the text generated in dummy pdfs
def merging_pdf(child_second_page, data, plan_second_page):
    writer = PdfWriter()
    # try:
    output_path = f"{data['filePath']}{data['fileName']}"

    if "employerName" not in data:
        fileName = "template_corporate_employee_v2.1 No Employer.pdf"
    else:
        if data["employerName"] != "":
            fileName = "template_corporate_employee_v2.1.pdf"
        else:
            fileName = "template_corporate_employee_v2.1 No Employer.pdf"

    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        templateFilePath = os.path.join(application_path, fileName)
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
    page2 = test.pages[1]
    page3 = test1.pages[1]
    page2.merge_page(page3)
    writer.add_page(page2)

    if os.path.exists(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf'):
        file3 = open(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf', 'rb')
        test4 = PdfReader(file3)
        if child_second_page is True and plan_second_page is False:
            page3 = test.pages[3]
        elif child_second_page is False and plan_second_page is True:
            page3 = test.pages[2]
        elif child_second_page is True and plan_second_page is True:
            page3 = test.pages[4]
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

    if "attachEquitableForm" in data:
        if data.get("attachEquitableForm") is True:
            filenames = [output_path, f"equitable_{data['first_name']}_{data['last_name']}.pdf"]
            merger = PdfMerger()
            for file in filenames:
                merger.append(PdfReader(open(file, 'rb')))
            merger.write(output_path)
            os.remove(filenames[1])

    if "attachProvincialForm" in data:
        if data.get("attachProvincialForm") is True:
            filenames = [output_path, f"provincial_{data['first_name']}_{data['last_name']}.pdf"]
            merger = PdfMerger()
            for file in filenames:
                merger.append(PdfReader(open(file, 'rb')))
            merger.write(output_path)
            os.remove(filenames[1])

    if os.path.exists(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf'):
        file3.close()
        os.remove(f'dummy1_{data["first_name"]}_{data["date_of_birth"]}.pdf')
    # except Exception as e:
    #     print(f"ERROR: {e}")

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

# # File version
# json_file = sys.argv[1]
# with open(json_file, 'r') as myFile:
#     json_file = myFile.read()
# data = json.loads(json_file)

versionNo = "v2.3.2"
pdf = FPDF('P', 'cm', 'letter')
pdf2 = FPDF('P', 'cm', 'letter')
pdf3 = FPDF('P', 'cm', 'letter')
pdf3 = FPDF('P', 'cm', 'letter')
first_page(data, versionNo)

# TODO: Don't throw any error if the information is not found and generate the ROE

# TODO: Remove spaces from all the template files
