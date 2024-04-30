import json
import sys
import base64
import warnings
from datetime import datetime

from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader, PageObject
import os.path
import shutil
from PIL import Image
from io import BytesIO
import logging
from urllib.parse import unquote


def convert_date(date_str):
    try:
        date_object = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        try:
            date_object = datetime.strptime(date_str, '%m-%d-%Y')
        except ValueError:
            return "Invalid date format. Please provide either yyyy-mm-dd or mm-dd-yyyy."

    formatted_date = date_object.strftime('%B %d, %Y')
    return formatted_date


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


def second_page(plan, cell_height, border):
    pdf.set_font_size(7.8)
    # if pdf.get_y() > 21:
    #     pdf.add_page()
    #     # pdf.set_y(5.5)
    if len(plan['priceDetails']) > 0:
        pdf.set_x(1.6)
        pdf.cell(8.7, cell_height, txt=plan["planLevel"], align='L')
        pdf.ln(cell_height)
        for province in plan['priceDetails']:
            # for key in province:
            priceDetails = plan['priceDetails']
            pdf.set_x(2)
            pdf.multi_cell(w=12.1, h=cell_height, txt=f'{province}', border=border, align='L',
                           new_x="RIGHT",
                           new_y="TOP", max_line_height=0.45, split_only=False)
            pdf.multi_cell(w=1.6, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["single"]),
                           border=border,
                           align='R', new_x="RIGHT", new_y="TOP")
            pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["couple"]),
                           border=border,
                           align='R', new_x="RIGHT", new_y="TOP")
            pdf.multi_cell(w=2, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["family"]),
                           border=border,
                           align='R', new_x="RIGHT", new_y="TOP")
            pdf.ln(cell_height)
    else:
        pdf.set_x(1.6)
        pdf.multi_cell(w=12.5, h=cell_height, txt=plan["planLevel"], border=border, align='L', new_x="RIGHT",
                       new_y="TOP", max_line_height=0.45, split_only=False)
        pdf.multi_cell(w=1.6, h=cell_height, txt='${:.2f}'.format(plan["price_single"]), border=border,
                       align='R', new_x="RIGHT", new_y="TOP")
        pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(plan["price_couple"]), border=border,
                       align='R', new_x="RIGHT", new_y="TOP")
        pdf.multi_cell(w=2, h=cell_height, txt='${:.2f}'.format(plan["price_family"]), border=border,
                       align='R', new_x="RIGHT", new_y="TOP")
        pdf.ln(cell_height)
    # pdf.text(1.45, 11.1, "Applicable taxes extra")


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
        if os.path.exists(tempFont):
            os.remove(tempFont)
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {fontPath}")

    pdf.add_font('dejavu', '', tempFont)
    pdf.add_page()
    primary_font = 10
    border = 0
    pdf.set_font('dejavu', '', primary_font)

    pdf.set_y(4.5)
    pdf.set_x(1.25)
    pdf.multi_cell(9.3, 1, txt=data.get('company_name'), border=0, max_line_height=0.5, split_only=False)
    # pdf.text(1.4, 5.15, data["company_name"].title())  # Company Name
    pdf.text(1.4, 7.1, data["company_street_address"])  # Company Street Address 1
    if "company_street_address_line2" in data:
        pdf.text(1.4, 8.6, data["company_street_address_line2"])    # Street address line 2
    if "company_apt" in data:
        pdf.text(1.4, 10.1, data.get("company_apt", ""))
    pdf.text(6.2, 10.1, data["company_city"].title())  # Company City
    pdf.text(6.2, 11.6, data["company_postal_code"])  # Company Postal Code
    pdf.text(1.4, 11.6, data["company_province"].title())  # Company Province

    signature_name = ""

    # Printing Administrators
    if len(data["administrators"]) > 0:
        pdf.set_font('dejavu', '', 7.8)
        cell_height = 0.6
        y = 5.5
        pdf.set_y(y)
        x = 11.05
        for admin in data["administrators"]:
            if "ideabytes" not in admin['admin_email'] and "aitestpro" not in admin['admin_email'] and "groupbenefitz" not in admin['admin_email'] and "groupbenefits" not in admin['admin_email'] and "advisor" not in admin['admin_role'].lower():
                pdf.set_x(x)
                pdf.multi_cell(w=3.0, h=cell_height, txt=admin['admin_name'].title(), border=border, align='L', new_x="RIGHT",
                               new_y="TOP", max_line_height=0.4, split_only=False)
                pdf.multi_cell(w=2.9, h=cell_height, txt=admin['admin_role'].title(), border=border, align='L', new_x="RIGHT",
                               new_y="TOP", max_line_height=0.4, split_only=False)  # Administrator's Role
                pdf.multi_cell(w=3.32, h=cell_height, txt=admin['admin_email'], border=border, align='L', new_x="RIGHT",
                               new_y="TOP", max_line_height=0.3, split_only=False)  # Administrator's Email

                # if admin['admin_role'].lower() == "plan administrator":
                #     signature_name = admin['admin_name'].title()

                pdf.ln(cell_height)

    pdf.set_font('dejavu', '', 9.3)
    pdf.text(1.4, 14, convert_date(data["policy_start_date"]))  # Policy Start Date
    pdf.set_font('dejavu', '', primary_font)
    pdf.set_y(13.4)
    pdf.set_x(6.15)
    pdf.cell(4.4, 1, str(data["no_of_employees"]), border=0, align='C')  # Number of Employees

    # To check if Wallet is selected
    if data["wallet_selected"] == 0 or data["wallet_selected"] is False:
        pdf.text(1.4, 15.5, "No")
    else:
        pdf.text(1.4, 15.5, "Yes")

    # To check if tier is selected
    if data["tier_selected"] == 0 or data["tier_selected"] is False:
        pdf.text(6.2, 15.5, "No")
    else:
        pdf.text(6.2, 15.5, "Yes")

    if "workingProvinceList" in data:
        if pdf.get_string_width(", ".join(province.strip() for province in data['workingProvinceList'])) > 23.8:
            pdf.set_font_size(7)
        else:
            pdf.set_font_size(8)
        pdf.set_y(16.4)
        pdf.set_x(1.3)
        pdf.multi_cell(9.3, 1, ", ".join(province.strip() for province in data['workingProvinceList']), border=0, max_line_height=0.4)
    pdf.set_font_size(7)
    pdf.set_text_color(0, 0, 255)
    pdf.set_y(21.9)
    pdf.set_x(8)
    pdf.cell(1, 1, "(View)", link=data['terms_conditions_link'])
    pdf.set_y(21.9)
    pdf.set_x(15.8)
    pdf.cell(1, 1, "(View)", link=data['advisor_disclosure_link'])

    pdf.set_text_color(0, 0, 0)

    pdf.set_font('dejavu', '', 12)
    # Filling the checkboxes for terms_conditions and advisor_disclosure
    if data['terms_conditions'] is True:  # terms and conditions
        pdf.text(1.3, 22.55, u'\u2713')
    if data['advisor_disclosure'] is True:  # advisor disclosure
        pdf.text(11.05, 22.55, u'\u2713')

    pdf.set_font('dejavu', '', primary_font)
    # To check how the payment is made
    if data["use_CreditCard"] is True:
        pdf.text(1.4, 23.85, "Credit Card")
    elif data["pad_Payment"] is True:
        pdf.text(1.4, 23.85, "Pre-Authorized Debit")
    elif data["invoice_Payment"] is True:
        pdf.text(1.4, 23.85, "Invoice Method")
    else:
        if "paymentMethod" in data:
            pdf.text(1.4, 23.85, data["paymentMethod"])

    pdf.text(1.4, 25.3, data["advisor_name"].title())  # Advisor Name

    pdf.set_text_color(255, 255, 255)
    pdf.set_font_size(5)
    pdf.text(0.7, 27.5, versionNo)

    pdf.set_font_size(primary_font)
    pdf.set_text_color(0, 0, 0)
    # if "date_signed" in data:
    #     pdf.text(11.1, 22.45, data["date_signed"])  # Date Signed

    pdf.set_font_size(6)
    pdf.text(16, 25.5, f"({data.get('loginGroupContactName').title()} - {data.get('loginGroupContactRole').title()})")

    # Signature
    if data['signature'] is not None and 'data:image/png;base64,' in data['signature']:
        signature_file_name = f'signature_{data["company_name"]}.png'  # Need to be updated for generating and updating
        signature(data['signature'].split(',')[1], signature_file_name)
        pdf.image(signature_file_name, 11.5, 24.7, 2.8, 0.98)
        os.remove(signature_file_name)

    second_page_check = False
    # Printing Plans
    # if len(data["selected_plans"]) > 0:
    #     pdf.set_font('dejavu', '', 7.8)
    #     y = 12.9
    #     cell_height = 0.6
    #     pdf.set_y(y)
    #     for plan in data["selected_plans"]:
    #         pdf.set_x(11)
    #         pdf.multi_cell(w=3.8, h=cell_height, txt=plan["planLevel"], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.3, split_only=False)
    #         pdf.multi_cell(w=1.4, h=cell_height, txt='${:.2f}'.format(plan["price_single"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
    #         pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(plan["price_couple"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
    #         pdf.multi_cell(w=1.7, h=cell_height, txt='${:.2f}'.format(plan["price_family"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
    #         pdf.ln(cell_height)

    # Reset line height = 20.3

    selected_plan = False
    bulk_plan = False

    pdf.set_font_size(7)
    pdf.text(11.1, 21.6, "Applicable taxes extra.")

    cell_height_header = 0.7

    if len(data['corporateBulkPlans']) > 0:
        bulk_plan = True

        cell_height = 0.5
        # pdf.set_font('dejavu', '', 7.8)
        border = 0

        pdf.set_y(11.8)
        pdf.set_x(11)
        pdf.set_fill_color(24, 44, 76)
        pdf.set_font('helvetica', 'B', 7.8)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(5.2, cell_height_header, " Plan", align='L', fill=True)
        pdf.cell(2.2, cell_height_header, "Headcount", align='L', fill=True)
        pdf.cell(1.9, cell_height_header, "Price", align='C', fill=True)
        pdf.ln(cell_height_header)
        pdf.set_text_color(0, 0, 0)

        x = 11
        y = 12.9
        # pdf.set_y(y)
        pdf.set_x(x)
        pdf.set_font('helvetica', 'BU', 7.8)
        pdf.cell(8.7, cell_height, "Group Plans", align='L')
        pdf.ln(cell_height)
        pdf.set_font('dejavu', '', 7.8)
        # if selected_plan is True:
        #     y = 19.6
        #     x = 1.3
        # else:

        for plan in data['corporateBulkPlans']:
            pdf.set_x(x)
            pdf.multi_cell(w=5.2, h=cell_height, txt=plan["planLevel"], border=border, align='L', new_x="RIGHT",
                           new_y="TOP", max_line_height=0.45, split_only=False)
            pdf.multi_cell(w=1.5, h=cell_height, txt=str(plan["quantity"]), border=border, align='C', new_x="RIGHT",
                           new_y="TOP", max_line_height=0.45, split_only=False)
            pdf.multi_cell(w=2.1, h=cell_height, txt=f'${plan["price"] * plan["quantity"]}', border=border, align='R',
                           new_x="RIGHT", new_y="TOP", max_line_height=0.45, split_only=False)
            pdf.ln(cell_height)
        pdf.ln(0.2)

    if bulk_plan is False:
        pdf.set_y(11.8)
    pdf.set_fill_color(24, 44, 76)
    pdf.set_font('helvetica', 'B', 7.8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_x(11)
    pdf.cell(4.1, cell_height_header, " Plan", align='L', fill=True)
    pdf.cell(1.8, cell_height_header, " Single", align='L', fill=True)
    pdf.cell(1.7, cell_height_header, " Couple", align='L', fill=True)
    pdf.cell(1.7, cell_height_header, " Family", align='L', fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(cell_height_header)

    if "paidByCompany" in data:
        if len(data["paidByCompany"]) > 0:
            selected_plan = True
            pdf.set_font('dejavu', '', 7.8)
            y = 12.9
            y_table = 11.8
            cell_height = 0.5
            # if bulk_plan is False:
            #     pdf.set_y(y_table)

            pdf.set_x(11)
            pdf.set_font('helvetica', 'BU', 7.8)
            pdf.cell(8.7, cell_height, "Corporate Paid Plans", align='L')
            pdf.ln(cell_height)
            pdf.set_font('dejavu', '', 7.8)
            for plan in data["paidByCompany"]:
                if pdf.get_y() + (cell_height * len(plan['priceDetails'])) > 20.9:
                    if second_page_check is False:
                        pdf.add_page()
                        second_page_check = True
                        pdf.set_y(5.5)
                # print(f"second page condition {second_page_check}")
                if second_page_check is True:
                    # print(pdf.get_y() + (cell_height * len(plan['priceDetails'])) > 25)
                    if pdf.get_y() + (cell_height * len(plan['priceDetails'])) > 25:
                        pdf.add_page()
                        pdf.set_y(5.5)
                    second_page(plan, cell_height, border)
                else:
                    if len(plan['priceDetails']) > 0:
                        pdf.set_x(11)
                        pdf.cell(8.7, cell_height, txt=plan["planLevel"], align='L')
                        pdf.ln(cell_height)
                        for province in plan['priceDetails']:
                            priceDetails = plan['priceDetails']
                            # for key in province:
                            pdf.set_x(11.4)
                            pdf.multi_cell(w=3.6, h=cell_height, txt=f'{province}', border=border, align='L',
                                           new_x="RIGHT",
                                           new_y="TOP", max_line_height=0.45, split_only=False)
                            pdf.multi_cell(w=1.4, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["single"]),
                                           border=border,
                                           align='R', new_x="RIGHT", new_y="TOP")
                            pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["couple"]),
                                           border=border,
                                           align='R', new_x="RIGHT", new_y="TOP")
                            pdf.multi_cell(w=1.7, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["family"]),
                                           border=border,
                                           align='R', new_x="RIGHT", new_y="TOP")
                            if pdf.get_string_width(province) > 3.5:
                                pdf.ln(cell_height * 1.2)
                            else:
                                pdf.ln(cell_height * 0.9)
                    else:
                        pdf.set_x(11)
                        pdf.multi_cell(w=4, h=cell_height, txt=plan["planLevel"], border=border, align='L', new_x="RIGHT",
                                       new_y="TOP", max_line_height=0.45, split_only=False)
                        pdf.multi_cell(w=1.4, h=cell_height, txt='${:.2f}'.format(plan["price_single"]), border=border,
                                       align='R', new_x="RIGHT", new_y="TOP")
                        pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(plan["price_couple"]), border=border,
                                       align='R', new_x="RIGHT", new_y="TOP")
                        pdf.multi_cell(w=1.7, h=cell_height, txt='${:.2f}'.format(plan["price_family"]), border=border,
                                       align='R', new_x="RIGHT", new_y="TOP")
                        pdf.ln(cell_height)

    if "coveredByCompany" in data:
        if len(data["coveredByCompany"]) > 0:
            if selected_plan is False:
                selected_plan = True
            pdf.set_font('dejavu', '', 7.8)
            y = 12.9
            cell_height = 0.5
            # pdf.set_y(y)
            pdf.set_x(11)
            pdf.set_font('helvetica', 'BU', 7.8)
            if second_page_check is False:
                pdf.set_x(11)
                pdf.cell(8.7, cell_height, "Employee permitted upgrade via Payroll Deduction", align='L')
            else:
                pdf.set_x(1.6)
                pdf.cell(8.7, cell_height, "Employee permitted upgrade via Payroll Deduction", align='L')
            pdf.ln(cell_height)
            pdf.set_font('dejavu', '', 7.8)

            for plan in data["coveredByCompany"]:
                if pdf.get_y() + (cell_height * len(plan['priceDetails'])) > 20.9:
                    if second_page_check is False:
                        pdf.add_page()
                        second_page_check = True
                        pdf.set_y(5.5)
                if second_page_check is True:
                    if pdf.get_y() + (cell_height * len(plan['priceDetails'])) > 25:
                        pdf.add_page()
                        pdf.set_y(5.5)
                    second_page(plan, cell_height, border)
                    # pdf.ln(cell_height)
                else:
                    if len(plan['priceDetails']) > 0:
                        pdf.set_x(11)
                        pdf.cell(8.7, cell_height, txt=plan["planLevel"], align='L')
                        pdf.ln(cell_height)
                        for province in plan['priceDetails']:
                            priceDetails = plan['priceDetails']
                            # for key in province:
                            pdf.set_x(11.4)
                            pdf.multi_cell(w=3.6, h=cell_height, txt=f'{province}', border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.45, split_only=False)
                            pdf.multi_cell(w=1.4, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["single"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
                            pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["couple"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
                            pdf.multi_cell(w=1.7, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["family"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
                            if pdf.get_string_width(province) > 3.5:
                                pdf.ln(cell_height * 1.2)
                            else:
                                pdf.ln(cell_height * 0.9)
                    else:
                        pdf.set_x(11)
                        pdf.multi_cell(w=4, h=cell_height, txt=plan["planLevel"], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.45, split_only=False)
                        pdf.multi_cell(w=1.4, h=cell_height, txt='${:.2f}'.format(plan["price_single"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
                        pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(plan["price_couple"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
                        pdf.multi_cell(w=1.7, h=cell_height, txt='${:.2f}'.format(plan["price_family"]), border=border, align='R', new_x="RIGHT", new_y="TOP")
                        pdf.ln(cell_height)

    if "paidByEmployee" in data:
        if len(data["paidByEmployee"]) > 0:
            if selected_plan is False:
                selected_plan = True
            pdf.set_font('dejavu', '', 7.8)
            y = 12.9
            cell_height = 0.4
            # pdf.set_y(y)
            pdf.set_font('helvetica', 'BU', 7.8)
            if second_page_check is False:
                pdf.set_x(11)
                pdf.cell(8.7, cell_height, "Voluntary permitted plans - Employee pays directly", align='L')
            else:
                pdf.set_x(1.6)
                pdf.cell(8.7, cell_height, "Voluntary permitted plans - Employee pays directly", align='L')
            pdf.ln(cell_height)
            pdf.set_font('dejavu', '', 7.8)
            for plan in data["paidByEmployee"]:
                if pdf.get_y() + (cell_height * len(plan['priceDetails'])) > 20.9:
                    if second_page_check is False:
                        pdf.add_page()
                        second_page_check = True
                        pdf.set_y(5.5)
                if second_page_check is True:
                    if pdf.get_y() + (cell_height * len(plan['priceDetails'])) > 25.1:
                        pdf.add_page()
                        pdf.set_y(5.5)
                    second_page(plan, cell_height, border)
                else:
                    if len(plan['priceDetails']) > 0:
                        pdf.set_x(11)
                        pdf.cell(8.7, cell_height, txt=plan["planLevel"], align='L')
                        pdf.ln(cell_height)
                        for province in plan['priceDetails']:
                            # for key in province:
                            priceDetails = plan['priceDetails']
                            pdf.set_x(11.4)
                            pdf.multi_cell(w=3.6, h=cell_height, txt=f'{province}', border=border, align='L',
                                           new_x="RIGHT",
                                           new_y="TOP", max_line_height=0.45, split_only=False)
                            pdf.multi_cell(w=1.4, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["single"]),
                                           border=border,
                                           align='R', new_x="RIGHT", new_y="TOP")
                            pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["couple"]),
                                           border=border,
                                           align='R', new_x="RIGHT", new_y="TOP")
                            pdf.multi_cell(w=1.7, h=cell_height, txt='${:.2f}'.format(priceDetails[province]["family"]),
                                           border=border,
                                           align='R', new_x="RIGHT", new_y="TOP")
                            if pdf.get_string_width(province) > 3.5:
                                pdf.ln(cell_height * 1.2)
                            else:
                                pdf.ln(cell_height * 0.9)
                    else:
                        pdf.set_x(11)
                        pdf.multi_cell(w=4, h=cell_height, txt=plan["planLevel"], border=border, align='L', new_x="RIGHT",
                                       new_y="TOP", max_line_height=0.45, split_only=False)
                        pdf.multi_cell(w=1.4, h=cell_height, txt='${:.2f}'.format(plan["price_single"]), border=border,
                                       align='R', new_x="RIGHT", new_y="TOP")
                        pdf.multi_cell(w=1.8, h=cell_height, txt='${:.2f}'.format(plan["price_couple"]), border=border,
                                       align='R', new_x="RIGHT", new_y="TOP")
                        pdf.multi_cell(w=1.7, h=cell_height, txt='${:.2f}'.format(plan["price_family"]), border=border,
                                       align='R', new_x="RIGHT", new_y="TOP")
                        pdf.ln(cell_height)

    # if "corporateBulkPlans" in data:
    #     if len(data['corporateBulkPlans']) > 0:
    #         bulk_plan = True
    #         cell_height = 0.5
    #         pdf.set_font('dejavu', '', 7.8)
    #         border = 0
    #         if selected_plan is True:
    #             y = 19.6
    #             x = 1.3
    #         else:
    #             x = 11
    #             y = 12.9
    #
    #         pdf.set_y(y)
    #         for plan in data['corporateBulkPlans']:
    #             pdf.set_x(x)
    #             pdf.multi_cell(w=5.2, h=cell_height, txt=plan["planLevel"], border=border, align='L', new_x="RIGHT", new_y="TOP", max_line_height=0.45, split_only=False)
    #             pdf.multi_cell(w=1.5, h=cell_height, txt=str(plan["quantity"]), border=border, align='C', new_x="RIGHT", new_y="TOP", max_line_height=0.45, split_only=False)
    #             pdf.multi_cell(w=2.1, h=cell_height, txt=f'${plan["price"] * plan["quantity"]}', border=border, align='R', new_x="RIGHT", new_y="TOP", max_line_height=0.45, split_only=False)
    #             pdf.ln(cell_height)
    #
    #         pdf.set_font_size(7)
    #         pdf.text(1.4, 21.6, "Applicable taxes extra.")

    # checking_length(data['company_name'], 1.5, 5.35, pdf)

    pdf.output(f'dummy_{data["company_name"]}.pdf')
    os.remove(tempFont)
    merging_pdf(data, selected_plan, bulk_plan)


def merging_pdf(data, selected_plan, bulk_plan):
    writer = PdfWriter()
    try:
        output_path = f"{data['filePath']}{data['fileName']}"

        # if selected_plan is True and bulk_plan is True:
        #     template_file_name = "Template_Corporate_ROE_Bulk_and_Selected_v3.2.pdf"
        # elif selected_plan is True and bulk_plan is False:
        template_file_name = "Template_Corporate_ROE_Selected_v3.3.pdf"
        # elif selected_plan is False and bulk_plan is True:
        #     template_file_name = "Template_Corporate_ROE_Bulk_v3.2.pdf"

        try:
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            templateFilePath = os.path.join(application_path, template_file_name)
            copyFile = f'{application_path}/corporate_enrollment_template_{data["company_name"]}.pdf'
            shutil.copy2(templateFilePath, copyFile)
        except:
            print(f"ERROR: template.pdf file not found {templateFilePath}")

        file1 = open(copyFile, 'rb')
        test1 = PdfReader(file1)
        file2 = open(f'dummy_{data["company_name"]}.pdf', 'rb')
        test2 = PdfReader(file2)

        no_of_pages = len(test2.pages)

        i = 0
        for i in range(no_of_pages):
            if i == 0:
                page1 = test1.pages[0]
            else:
                page1 = test1.pages[1]

            new_page = PageObject.create_blank_page(None, page1.mediabox.width, page1.mediabox.height)

            page1_text = test2.pages[i]
            # page1.merge_page(page1_text)
            # writer.add_page(page1)
            new_page.merge_page(page1)
            new_page.merge_page(page1_text)
            writer.add_page(new_page)

        # page2 = test1.pages[1]
        # page3 = test2.pages[1]
        # page2.merge_page(page3)
        # writer.add_page(page2)

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

        file1 = open(f"{data['filePath']}{data['fileName']}", 'rb')
        test1 = PdfReader(file1)

        no_of_pages = len(test1.pages)

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
        for i in range(no_of_pages):
            pdf.add_page()
            if i == 0:
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
                    pdf.image(signature_file_name, 11.5, 24.7, 2.8, 0.98)
                    # pdf.rect(11, 23.3, 9.3, 0.98)
                    os.remove(signature_file_name)

                pdf.add_font('dejavu', '', tempFont)
                pdf.set_font('dejavu', '', 9)
                pdf.set_fill_color(223, 230, 237)

                if "paymentMethod" in data:
                    pdf.text(1.4, 23.85, data["paymentMethod"])
                    # pdf.set_y(9.7)
                    # pdf.set_x(6.2)
                # pdf.cell(5, 1, data['], align='L', fill=True)
                pdf.text(11.1, 23.85, convert_date(data["date_signed"]))
        pdf.output(f'dummy_{data["fileName"]}')

        file2 = open(f'dummy_{data["fileName"]}', 'rb')
        test2 = PdfReader(file2)

        for x in range(no_of_pages):
            page = test1.pages[x]
            page1 = test2.pages[x]
            page.merge_page(page1)
            writer.add_page(page)

        outputStream = open(output_path, 'wb')
        writer.write(outputStream)
        outputStream.close()

        file1.close()
        file2.close()
        os.remove(f'dummy_{data["fileName"]}')
        os.remove(tempFont)

    except Exception as e:
        print(f"ERROR: {e}")


# String version
json_encoded_string = sys.argv[1]
json_decoded_string = unquote(json_encoded_string)
jsonData = json.loads(json_decoded_string)

# File version
# json_file = sys.argv[1]
# with open(json_file, 'r') as myFile:
#     json_file = myFile.read()
# jsonData = json.loads(json_file)

versionNo = "v2.5.3"
pdf = FPDF('P', 'cm', 'letter')

if "process" in jsonData:
    if jsonData["process"].upper() == "GENERATION":
        first_page(jsonData)
    elif jsonData["process"].upper() == "UPDATION":
        update_pdf(jsonData)
else:
    print(f"ERROR! Wrong process mentioned {jsonData['process']}")



