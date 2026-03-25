import json
import re

# -------------------------------
# UTILITIES
# -------------------------------

def normalize_date(date_str):
    if not date_str:
        return "unknown"
    try:
        return date_str[:4]
    except:
        return "unknown"

def clean_text(text, max_len=300):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)  # remove extra spaces
    return text.strip()[:max_len]

# -------------------------------
# MAIN CHUNK BUILDER (IMPROVED)
# -------------------------------

def build_chunks(profile):

    profile_id = profile.get("id")
    name = profile.get("name", "Unknown")
    location = profile.get("city", "Unknown")
    about = clean_text(profile.get("about", ""), 400)
    projects = profile.get("projects","")
    about_project = ''

    for i in projects:
        about_ =i["description"]
        start = i["start_date"]
        title = i["title"]
        about_project = about_ + " Starting Date " + start + "Title of the project " + title
        
    # -------------------------------
    # 1. SUMMARY (HIGH PRIORITY)
    # -------------------------------

    summary = f"""User name is {name} current location : {location} About the user: {about} here is the profile id of the User {profile_id} User has build some projects {about_project}"""
    with open("userData/about.txt","w",encoding="utf-8") as f:
        f.write(summary)


    # -------------------------------
    # 2. COMPANY
    # -------------------------------

    company = profile.get("current_company", {})
    current = 1
    work = open("userData/work.txt","w",encoding="utf-8")
    if(company!={}):
        if company and company.get("name"):
            if(current == 1):
                text = f"""Current Job Role of User {name} Organization: {company['name']}"""
                current +=1
            else:
                text = f"""Previous Job Role of User {name} Organization: {company['name']}"""
            work.write(text)


    # -------------------------------
    # 3. EDUCATION
    # -------------------------------
    edu = 1
    stud = open("userData/education.txt","w",encoding="utf-8")
    educations = profile.get("education", [])
    if educations !=[]:
        for edu in educations:
            title = edu.get("title", "Unknown Institute")
            start = normalize_date(edu.get("start_year"))
            end = normalize_date(edu.get("end_year"))

            if(edu==1):
                text = f"""
                User {name} currently studies in Institute: {title} Duration: {start}-{end}
                """
                edu+=1
            else:
                text = f"""
                User {name} Previouly studied in Institute: {title} Duration: {start}-{end}
                """
            stud.write(text)


    # -------------------------------
    # 4. CERTIFICATIONS
    # -------------------------------
    cert_ = open("userData/certificates.txt","w",encoding="utf-8")
    certs = profile.get("certifications", [])
    if certs!=[] :
        for cert in certs:
            title = cert.get("title", "")
            issuer = cert.get("subtitle", "")
            cred_id = cert.get("credential_id", "")

            text = f"""
            User  {name} gained a certificate {title}
            Issuer: {issuer}
            Credential ID: {cred_id}
            """
            cert_.write(text)


# -------------------------------
# 5. ACTIVITY (SMART + ATTRIBUTION)
# -------------------------------

    acti = open("userData/activites.txt","w",encoding="utf-8")
    activities = profile.get("activity", [])

    if(activities!=[]):
        for act in activities:
            raw_text = act.get("title", "")
            interaction = act.get("interaction", "")
            link = act.get("link", "")

            if not raw_text:
                continue

            clean_activity = clean_text(raw_text, 250)

            # classify
            if "shared" in interaction:
                action_type = "posted"

            elif "commented" in interaction:
                action_type = "commented"

            elif "liked" in interaction:
                action_type = "liked"

            else:
                action_type = "interacted"


            # 🔥 individual chunk (IMPORTANT for retrieval)
            text = f"""User {name} has {action_type} {clean_activity} here is the Link: {link}"""

            acti.write(text)



    # -------------------------------
    # 6. SOCIAL SIGNAL
    # -------------------------------

    followers = profile.get("followers", 0)
    connections = profile.get("connections", 0)

    text = f"""User {name} has Total of Followers: {followers} and Totol Connections: {connections}"""
    with open("userData/about.txt","a+") as soc:
        soc.write(text)




if __name__ == "__main__":
    with open("samples/linkedINdata.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    build_chunks(data)

