import sys
import base64
from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader
import os.path
import shutil
from PIL import Image
from io import BytesIO
from datetime import datetime


def convert_date(date_string):
    date_object = datetime.strptime(date_string, "%Y-%m-%d")
    formatted_date = date_object.strftime("%y-%m-%d")
    return formatted_date

def signature(string, fileName):
    decoded_data = base64.b64decode(string)
    img_file = open(fileName, 'wb')
    img_file.write(decoded_data)
    img_file.close()


def convert_date_format(date_string):
    if "-" in date_string and date_string != "":
        parts = date_string.split('-')
        mm_dd_yyyy = f"{parts[1]}/{parts[2]}/{parts[0]}"
        return mm_dd_yyyy
    else:
        return date_string


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
        member["date_of_hiring"] = ""
        member["spouseInformation"] = data.get("spouseDetails")
        member["dependantInformation"] = data.get("childrenDetails")
        member["signature"] = data.get("signature")
        member["job_title"] = "Student"
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
        member["dependantInformation"] = []
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
        tempFont = f'{application_path}/tempfont_provincial.ttf'
        shutil.copy2(fontPath, tempFont)
    except:
        print(f"ERROR: ttf file not found {fontPath}")

    pdf.add_font('dejavu', '', tempFont)

    pdf.add_page()
    pdf.set_font("dejavu", '', 9)

    member_details = get_member_details(data, member_type)
    # print(member_details)
    phrData = data.get('phrMemberDetails')

    # Section 1
    pdf.text(15.6, 2.25, u'\u2713')
    pdf.text(3.9, 3.45, "The GroupBenefitz Platform Inc.")
    pdf.text(17.2, 3.45, "28700001")

    # Section 2
    pdf.text(5, 5.1, member_details.get("last_name"))
    pdf.text(14, 5.1, member_details.get("first_name"))
    pdf.text(5, 5.65, member_details.get('date_of_birth'))

    if member_details.get("gender").lower() == "male":
        pdf.text(12.87, 5.6, u'\u2713')
    elif member_details.get("gender").lower() == "female":
        pdf.text(15.06, 5.6, u'\u2713')

    hiring_date = data.get("date_of_hiring").split('-')
    pdf.text(15.9, 6.3, hiring_date[2])
    pdf.text(17.8, 6.3, hiring_date[1])
    pdf.text(19.4, 6.3, hiring_date[0])

    if 'dateOfArrival' in phrData:
        date_of_arrival = phrData['dateOfArrival'].split('-')
        pdf.text(5.4, 7.4, date_of_arrival[2])
        pdf.text(7.3, 7.4, date_of_arrival[1])
        pdf.text(8.9, 7.4, date_of_arrival[0])

    landed_status = phrData['isLandedImmigrant']
    applying_for_landed_status = phrData['applyingForLandingStatus']
    if landed_status is True:
        pdf.text(18.5, 7.3, u'\u2713')
    else:
        pdf.text(19.75, 7.3, u'\u2713')
        if applying_for_landed_status is True:
            pdf.text(18.5, 7.8, u'\u2713')
        else:
            pdf.text(19.75, 7.8, u'\u2713')

    country_of_origin = phrData['countryOfOrigin']
    pdf.text(5, 8.25, country_of_origin)

    coverage_required_employee = phrData['coverageRequired']
    if coverage_required_employee is True:
        pdf.text(7.7, 8.8, u'\u2713')
    else:
        pdf.text(9.45, 8.8, u'\u2713')

    planStartDateMember = member_details.get('dateSigned').split('-')
    pdf.text(5.4, 9.9, planStartDateMember[2])
    pdf.text(7.3, 9.9, planStartDateMember[1])
    pdf.text(8.9, 9.9, planStartDateMember[0])

    # Section 3
    dependent_coverage = phrData['dependentDetails']['coverageRequired']
    if dependent_coverage is True:
        pdf.text(7.6, 11.95, u'\u2713')
    else:
        pdf.text(9, 11.95, u'\u2713')

    dependent_date_of_arrival = phrData['dependentDetails']['dateOfArrival'].split('-')
    pdf.text(15.9, 11.95, dependent_date_of_arrival[2])
    pdf.text(17.8, 11.95, dependent_date_of_arrival[1])
    pdf.text(19.4, 11.95, dependent_date_of_arrival[0])

    plansStartDateDependent = member_details['dateSigned'].split('-')
    pdf.text(5.4, 12.7, plansStartDateDependent[2])
    pdf.text(7.3, 12.7, plansStartDateDependent[1])
    pdf.text(8.9, 12.7, plansStartDateDependent[0])

    dependent_landed_status = phrData['dependentDetails']['isLandedImmigrant']
    applying_for_landed_status_dependent = phrData['dependentDetails']['applyingForLandingStatus']
    if dependent_landed_status is True:
        pdf.text(10.2, 13.85, u'\u2713')
    else:
        pdf.text(11.72, 13.85, u'\u2713')
        if applying_for_landed_status_dependent is True:
            pdf.text(10.27, 14.35, u'\u2713')
        else:
            pdf.text(11.79, 14.35, u'\u2713')

    dependent_stay = phrData['dependentDetails']['stayFor3Months']
    if dependent_stay is True:
        pdf.text(10.2, 14.8, u'\u2713')
    else:
        pdf.text(11.72, 14.8, u'\u2713')

    dependent_country_of_origin = phrData['dependentDetails']['countryOfOrigin']
    pdf.text(16, 13.85, dependent_country_of_origin)

    table_cell_height = 0.4
    border = 0
    pdf.set_font("dejavu", '', 8)
    if member_details.get("having_spouse") is True:
        spouse_information = member_details.get("spouseInformation")
        pdf.set_y(15.4)
        pdf.set_x(1.35)
        pdf.cell(3.94, table_cell_height, spouse_information['last_name'], border=border, align='C')
        pdf.cell(4.67, table_cell_height, spouse_information['first_name'], border=border, align='C')
        pdf.cell(4.31, table_cell_height, "Spouse", border=border, align='C')
        if spouse_information['gender'].lower() == "male":
            spouse_gender = 'M'
        elif spouse_information['gender'].lower() == "female":
            spouse_gender = 'F'
        else:
            spouse_gender = ''
        pdf.cell(1.9, table_cell_height, spouse_gender, border=border, align='C')
        pdf.cell(4.2, table_cell_height, convert_date(spouse_information['date_of_birth']), border=border, align='C')
        pdf.ln(table_cell_height)

    if len(member_details.get("dependantInformation")) > 0:
        if member_details.get("having_spouse") is not True:
            pdf.set_y(15.4)
            # pdf.set_x(1.35)

        for dependent in member_details.get("dependantInformation"):
            pdf.set_x(1.35)
            pdf.cell(3.94, table_cell_height, dependent['last_name'], border=border, align='C')
            pdf.cell(4.67, table_cell_height, dependent['first_name'], border=border, align='C')
            pdf.cell(4.31, table_cell_height, "Child", border=border, align='C')
            if dependent['gender'].lower() == "male":
                dependent_gender = 'M'
            elif dependent['gender'].lower() == "female":
                dependent_gender = 'F'
            pdf.cell(1.9, table_cell_height, dependent_gender, border=border, align='C')
            pdf.cell(4.2, table_cell_height, convert_date(dependent['date_of_birth']), border=border, align='C')
            pdf.ln(table_cell_height)

    pdf.set_font("dejavu", '', 9)
    # Section 4
    if member_details['signature'] is not None and 'data:image/png;base64,' in member_details['signature']:
        signature_file_name = f'signature_provincial_{member_details["first_name"]}_{member_details["last_name"]}.png'
        signature(member_details['signature'].split(',')[1], signature_file_name)
        pdf.image(signature_file_name, 4.5, 21.55, 4, 0.55)  # signature
        os.remove(signature_file_name)

    pdf.text(16, 22, member_details['dateSigned'])

    # Section 5
    pdf.text(3.9, 23, "The GroupBenefitz Platform Inc.")
    pdf.text(3.9, 23.5, "Plan Administrator")
    pdf.text(3.9, 23.95, "585 - 1000 Innovation Drive")
    pdf.text(3.9, 24.4, "Kanata")
    pdf.text(8.7, 24.4, "Ontario")
    pdf.text(14.6, 24.4, "K2K 3E7")

    pdf.output(f'dummy_provincial_{member_details["first_name"]}_{member_details["last_name"]}.pdf')
    merging_pdf(member_details)


def merging_pdf(member_details):
    writer = PdfWriter()
    try:
        output_path = f"provincial_{member_details['first_name']}_{member_details['last_name']}.pdf"
        try:
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            templateFilePath = os.path.join(application_path, "Provincial_health_replacement_form.pdf")
            copyFile = f"Temp Provincial Form {member_details['first_name']}_{member_details['last_name']}.pdf"
            shutil.copy2(templateFilePath, copyFile)
        except:
            print(f"ERROR: template.pdf file not found {templateFilePath}")

        file1 = open(copyFile, 'rb')
        test1 = PdfReader(file1)
        file2 = open(f'dummy_provincial_{member_details["first_name"]}_{member_details["last_name"]}.pdf', 'rb')
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

        os.remove(f'dummy_provincial_{member_details["first_name"]}_{member_details["last_name"]}.pdf')
        os.remove(copyFile)

    except Exception as e:
        print(f"ERROR: {e}")


def generate_provincial_roe(data, member_type):
    versionNo = "v1.0.1"
    pdf = FPDF('P', 'cm', 'Letter')
    first_page(data, pdf, member_type=member_type)
