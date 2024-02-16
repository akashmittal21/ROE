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
    img_file = open(fileName, 'wb')
    img_file.write(decoded_data)
    img_file.close()


def convert_date_format(date_string):
    # Split the date string by '-'
    parts = date_string.split('-')

    # Rearrange the parts in MM/DD/YYYY format
    mm_dd_yyyy = f"{parts[1]}/{parts[2]}/{parts[0]}"

    return mm_dd_yyyy


def get_member_details(data, ctype):
    member = {
        "first_name": "",
        "last_name": "",
        "date_of_birth": "",
        "hours_per_week": "",
        "email": "",
        "job_title": "",
        "date_of_hiring": "",
        "gender": "",
        "street_address_line1": "",
        "street_address_line2": "",
        "having_spouse": "",
        "dependant_carrier1_check": False,
        "dependant_carrier1": "",
        "dependant_carrier2_check": False,
        "dependant_carrier2": "",
        "province": "",
        "city": "",
        "postal_code": "",
        "language": "",
        "planCoverage": "",
        "planName": "",
        "spouseInformation": {},
        "dependantInformation": [],
        "dateSigned": "",
        "signature": ""
    }

    if ctype.lower() != "athabasca":
        member["first_name"] = data.get("first_name")
        member["last_name"] = data.get("last_name")
        member["date_of_birth"] = data.get("date_of_birth")
        member["gender"] = data.get("gender")
        member["email"] = data.get("email")
        member["hours_per_week"] = data.get("hours_per_week")
        member["street_address_line1"] = data.get("street_address_line1")
        member["street_address_line2"] = data.get("street_address_Line2")
        member["city"] = data.get("city")
        member["province"] = data.get("province")
        member["postal_code"] = data.get("postal_code")
        member["having_spouse"] = data.get("having_spouse")
        member["date_of_hiring"] = data.get("date_of_hiring")
        member["spouseInformation"] = data.get("spouse_details")
        member["dependantInformation"] = data.get("children_details")
        member["signature"] = data.get("signature")
        member["job_title"] = data.get("job_title")
        member["dateSigned"] = data.get("planEnrollmentDate")
        plans = data.get("plans")
        for plan in plans:
            products = plan.get("products")
            if "all-in" in plan.get("planname").lower():
                member["planName"] = plan.get("planname")
                for product in products:
                    member["planCoverage"] = product.get("planCoverage")
                    break
        if member["province"].lower() == "quebec" or member["province"].lower() == "qc":
            member["language"] = "French"
        else:
            member["language"] = "English"
        if member["having_spouse"] is True:
            if data["spouse_details"]["spouse_carrier_name"] is not None:
                if data["spouse_details"]["spouse_carrier_name"] != "":
                    member["dependant_carrier1_check"] = True
                    member["dependant_carrier1"] = data["spouse_details"]["spouse_carrier_name"]

        for child in member["dependantInformation"]:
            if child.get("child_carrier_name") is not None and child.get("child_carrier_name") != "" and not member["dependant_carrier1_check"]:
                member["dependant_carrier1_check"] = True
                member["dependant_carrier1"] = child.get("child_carrier_name")
            elif child.get("child_carrier_name") is not None and child.get("child_carrier_name") != "" and not member["dependant_carrier2_check"]:
                member["dependant_carrier2_check"] = True
                member["dependant_carrier2"] = child.get("child_carrier_name")

    else:
        member["first_name"] = data.get("firstName")
        member["last_name"] = data.get("lastName")
        member["date_of_birth"] = data.get("dateOfBirth")
        member["gender"] = data.get("gender")
        member["email"] = data.get("email")
        member["hours_per_week"] = data.get("hours_per_week")
        member["street_address_line1"] = data.get("homeAddress")
        # member["street_address_line2"] = data.get("street_address_Line2")
        member["city"] = data.get("city")
        member["province"] = data.get("province")
        member["postal_code"] = data.get("postalCode")
        member["having_spouse"] = data.get("having_spouse")
        member["date_of_hiring"] = data.get("date_of_hiring")
        member["spouseInformation"] = data.get("spouseDetails")
        member["dependantInformation"] = data.get("childrenDetails")
        member["signature"] = data.get("signature")
        member["job_title"] = data.get("job_title")
        member["dateSigned"] = data.get("dateSigned")
        if data['languagePreference'].lower() == "fr":
            member["language"] = "French"
        else:
            member["language"] = "English"
        member["planCoverage"] = data["coverageType"]
        spouse_details = data['spouseDetails']
        member["spouseInformation"]["first_name"] = spouse_details.get('firstName')
        member["spouseInformation"]["last_name"] = spouse_details.get('lastName')
        member["spouseInformation"]["date_of_birth"] = spouse_details.get('dateOfBirth')
        member["spouseInformation"]["gender"] = spouse_details.get('gender')
        if "carrierName" in spouse_details and spouse_details.get("isInsured") is True:
            member["dependant_carrier1_check"] = True
            member["dependant_carrier1"] = spouse_details.get("carrierName")
        if len(data["childrenDetails"]) > 0:
            for dependant in data['childrenDetails']:
                dependant_info = {
                    "first_name": dependant.get("firstName"),
                    "last_name": dependant.get("lastName"),
                    "date_of_birth": dependant.get("dateOfBirth"),
                    "gender": dependant.get("gender"),
                    "enrolledInUniversity": dependant.get("isFullTimeStudent") or False,
                    "isDisabled": dependant.get("isDisabled") or False,
                    "graduationDay": ""
                }
                member["dependantInformation"].append(dependant_info)
                if dependant.get("child_carrier_name") is not None and dependant.get("child_carrier_name") != "" and not member["dependant_carrier1_check"]:
                    member["dependant_carrier1_check"] = True
                    member["dependant_carrier1"] = dependant.get("child_carrier_name")
                elif dependant.get("child_carrier_name") is not None and dependant.get("child_carrier_name") != "" and not member["dependant_carrier2_check"]:
                    member["dependant_carrier2_check"] = True
                    member["dependant_carrier2"] = dependant.get("child_carrier_name")

    return member


def check_sponsor_information(ctype, plan_name, plan_coverage, province):
    province_list1 = ["British Columbia", "Manitoba", "Saskatchewan", "BC", "MB", "SK"]

    association_details = {
        "associationName": None,
        "policyNumber": None,
        "division": None,
        "associationClass": None
    }

    if ctype.lower() == "athabasca":
        association_details["associationName"] = "The GroupBenefitz Platform Inc. (Athabasca University Voluntary Student Plan)"
        association_details["policyNumber"] = "815082"
        association_details["division"] = "001"
        association_details["associationClass"] = "A"
    else:
        association_details["associationName"] = "The GroupBenefitz Platform Inc."
        association_details["policyNumber"] = "814458"
        if any(province.lower() in plan_name.lower() for province in province_list1):
            association_details["division"] = "001"
            if "gold" in plan_name.lower():
                association_details["associationClass"] = "A"
            if "silver" in plan_name.lower():
                association_details["associationClass"] = "B"
            if "bronze" in plan_name.lower():
                association_details["associationClass"] = "C"
        else:
            if province.lower() in province_list1:
                association_details["division"] = "001"
                if "gold" in plan_name.lower():
                    association_details["associationClass"] = "A"
                if "silver" in plan_name.lower():
                    association_details["associationClass"] = "B"
                if "bronze" in plan_name.lower():
                    association_details["associationClass"] = "C"
            else:
                association_details["division"] = "002"
                if "gold" in plan_name.lower():
                    association_details["associationClass"] = "D"
                if "silver" in plan_name.lower():
                    association_details["associationClass"] = "E"
                if "bronze" in plan_name.lower():
                    association_details["associationClass"] = "F"

    return association_details


def first_page(data, pdf, member_type):
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        fontPath = os.path.join(application_path, "DejaVuSansCondensed.ttf")
        tempFont = f'{application_path}/tempfont_equitable.ttf'
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {fontPath}")

    pdf.add_font('dejavu', '', tempFont)

    pdf.add_page()
    pdf.set_font("dejavu", '', 9)

    member_details = get_member_details(data, member_type)
    # print(member_details)

    # Plan Sponsor Section
    sponsor_information = check_sponsor_information(member_type, member_details.get("planName"), member_details.get("planCoverage"), member_details.get("province"))
    sponsor_data = data['equitableFormData']
    pdf.text(1.25, 8.5, sponsor_information.get("associationName"))  # Name of PolicyHolder
    pdf.text(1.25, 9.5, sponsor_information.get("policyNumber"))  # Policy Number
    pdf.text(8, 9.5, sponsor_information.get("division"))
    pdf.text(14.6, 9.5, sponsor_information.get("associationClass"))
    if sponsor_data.get("certificateNumber") is not None:
        pdf.text(1.25, 10.5, f'{sponsor_data.get("certificateNumber")}')
    pdf.text(1.25, 11.5, f'{member_details.get("hours_per_week")}')
    pdf.text(8, 11.5, member_details.get("job_title"))
    pdf.text(1.25, 12.55, convert_date_format(member_details.get("date_of_hiring")))

    # Plan Member Section
    pdf.text(1.25, 14.35, f"{member_details.get('first_name')} {member_details.get('last_name')}")
    pdf.text(1.25, 15.35, convert_date_format(member_details.get("date_of_birth")))
    # gender
    pdf.set_font_size(8)
    if member_details.get("gender").lower() == "male":
        pdf.text(8.52, 14.92, u'\u2713')
    elif member_details.get("gender").lower() == "female":
        pdf.text(10.58, 14.92, u'\u2713')
    else:
        pdf.text(8.52, 15.35, u'\u2713')
        pdf.set_y(14.95)
        pdf.set_x(12)
        pdf.multi_cell(2.9, 0.5, member_details.get("gender"), border=0)
    # language
    if member_details.get("language").lower() == "english":
        pdf.text(15.05, 15.36, u'\u2713')
    else:
        pdf.text(17.32, 15.36, u'\u2713')
    pdf.set_font_size(9)
    pdf.text(1.22, 16.35, member_details.get('street_address_line1'))
    pdf.text(8.52, 16.35, member_details.get('city'))
    pdf.text(15.0, 16.35, member_details.get('province'))
    pdf.text(18.1, 16.35, member_details.get('postal_code'))
    pdf.text(1.22, 17.35, data.get("email") or "")
    pdf.set_font_size(8)

    # Section 4
    health_coverage_provinces = ["British Columbia", "Manitoba", "Saskatchewan", "BC", "MB", "SK"]
    if member_details.get("province").lower() in [prov.lower() for prov in health_coverage_provinces]:
        pdf.text(13.39, 23.26, u'\u2713')
    pdf.set_font_size(9)

    # ------ PAGE 2 --------
    pdf.add_page()
    pdf.set_font_size(9)
    # Plan Coverage
    # Single coverage
    plan_coverage = member_details.get("planCoverage").strip().lower()
    if plan_coverage == "single":
        pdf.text(1.5, 6.65, u'\u2713')
        pdf.text(2.78, 6.65, u'\u2713')
    # couple coverage
    elif plan_coverage == "couple":
        pdf.text(1.5, 7.28, u'\u2713')
        pdf.text(2.78, 7.28, u'\u2713')
    # Family coverage
    else:
        pdf.text(10.2, 6.65, u'\u2713')
        pdf.text(11.45, 6.65, u'\u2713')

    # Dependent insurance check
    if member_details.get("dependant_carrier1_check") is True:
        pdf.text(3.56, 10.62, u'\u2713')
        pdf.set_y(10.7)
        pdf.set_x(4.2)
        pdf.multi_cell(6.4, 0.5, member_details.get("dependant_carrier1"), border=0)
    else:
        pdf.text(4.73, 10.62, u'\u2713')
    if member_details.get("dependant_carrier2_check") is True:
        pdf.text(13.35, 10.62, u'\u2713')
        pdf.set_y(10.7)
        pdf.set_x(14.05)
        pdf.multi_cell(6.4, 0.5, member_details.get("dependant_carrier2"), border=0)
    else:
        pdf.text(14.52, 10.62, u'\u2713')

    pdf.set_font_size(9)
    # Spouse Information
    if member_details.get("having_spouse") is True:
        spouse_information = member_details.get("spouseInformation")
        pdf.text(1.25, 16.85, f'{spouse_information.get("first_name")} {spouse_information.get("last_name")}')
        pdf.text(12.2, 17.3, convert_date_format(spouse_information.get("date_of_birth")))

        pdf.set_font_size(9)
        if spouse_information.get("gender").lower() == "male":
            pdf.text(16.12, 16.9, u'\u2713')
        elif spouse_information.get("gender").lower() == "female":
            pdf.text(17.42, 16.9, u'\u2713')
        else:
            pdf.text(16.12, 17.34, u'\u2713')
            pdf.set_y(17.35)
            pdf.set_x(16)
            pdf.multi_cell(4.5, 0.5, spouse_information.get("gender"), border=0)

    pdf.set_font_size(9)
    # Dependent information
    if len(member_details.get("dependantInformation")) > 0:
        y_name = 19.9
        y_dob = 20.1
        y_male = 19.13
        y_female = 19.53
        y_other = 19.93
        y_gender = 19.93
        y_full_time = 19.53
        y_disabled = 19.93
        y_grad_date = 20.1
        y_buffer = 1.55
        for dependant in member_details.get("dependantInformation"):
            pdf.text(1.25, y_name, f'{dependant.get("first_name")} {dependant.get("last_name")}')
            pdf.text(8.4, y_dob, convert_date_format(dependant.get("date_of_birth")))
            if dependant.get("gender").lower() == "male":
                pdf.text(10.58, y_male, u'\u2713')
            elif dependant.get("gender").lower() == "female":
                pdf.text(10.58, y_female, u'\u2713')
            else:
                pdf.text(10.58, y_other, u'\u2713')
                pdf.set_y(y_gender)
                pdf.set_x(10.55)
                pdf.multi_cell(3.7, 0.5, f'{dependant.get("gender")}', border=0)
            if dependant.get("enrolledInUniversity") is True:
                pdf.text(14.34, y_full_time, u'\u2713')
            if dependant.get("isDisabled"):
                pdf.text(14.34, y_disabled, u'\u2713')
            if dependant.get("graduationDay") is not None:
                pdf.text(17.4, y_grad_date, dependant.get("graduationDay"))
            y_name += y_buffer
            y_dob += y_buffer
            y_male += 1.58
            y_female += 1.58
            y_other += 1.58
            y_gender += y_buffer
            y_full_time += y_buffer
            y_disabled += y_buffer
            y_grad_date += y_buffer

    pdf.set_font_size(9)
    pdf.add_page()

    pdf.add_page()
    pdf.text(15.2, 5.1, convert_date_format(member_details.get("dateSigned")))
    if member_details['signature'] is not None and 'data:image/png;base64,' in member_details['signature']:
        signature_file_name = f'signature_equitable_{member_details["first_name"]}_{member_details["date_of_birth"]}.png'
        signature(member_details['signature'].split(',')[1], signature_file_name)
        pdf.image(signature_file_name, 1.5, 4.3, 3, 1.2)  # signature
        os.remove(signature_file_name)

    pdf.output(f'dummy_equitable_{member_details["first_name"]}_{member_details["date_of_birth"]}.pdf')
    merging_pdf(member_details)


def merging_pdf(member_details):
    writer = PdfWriter()
    try:
        output_path = f"equitable_{member_details['first_name']}_{member_details['date_of_birth']}.pdf"
        try:
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            templateFilePath = os.path.join(application_path, "Equitable Life Application Form.pdf")
            copyFile = f"Temp Equitable Form {member_details['first_name']}_{member_details['date_of_birth']}.pdf"
            shutil.copy2(templateFilePath, copyFile)
        except:
            print(f"ERROR: template.pdf file not found {templateFilePath}")

        file1 = open(copyFile, 'rb')
        test1 = PdfReader(file1)
        file2 = open(f'dummy_equitable_{member_details["first_name"]}_{member_details["date_of_birth"]}.pdf', 'rb')
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

        os.remove(f'dummy_equitable_{member_details["first_name"]}_{member_details["date_of_birth"]}.pdf')
        os.remove(copyFile)

    except Exception as e:
        print(f"ERROR: {e}")


def generate_equitable_roe(data, member_type):
    versionNo = "v1.0.1"
    pdf = FPDF('P', 'cm', 'Letter')
    first_page(data, pdf, member_type=member_type)
