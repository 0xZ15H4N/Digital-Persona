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
    user_info = {}
    try:
        profile_id = profile.get("id")
        name = profile.get("name", "Unknown")
        location = profile.get("city", "Unknown")
        about = clean_text(profile.get("about", ""), 400)
        projects = profile.get("projects","")
        about_project = ''
        followers = profile.get("followers", 0)
        connections = profile.get("connections", 0)
        for i in projects:
            about_ =i["description"] if i != None else "Unknown"
            start = i["start_date"] if i != None else "Unknown"
            title = i["title"] if i != None else "Unknown"
            about_project = about_ + " Starting Date " + start + "Title of the project " + title
            
        user_info["about_user"] = f"""User name is {name} current location : {location} About the user: {about} here is the profile id of the User {profile_id} User has build some projects {about_project} User {name} has Total of Followers: {followers} and Totol Connections: {connections}"""

        company = profile.get("current_company", {})
        current = 1
        if(company!={}):
            if company and company.get("name"):
                if(current == 1):
                    user_exp = f"""Current Job Role of User {name} Organization: {company['name']}"""
                    current +=1
                else:
                    user_exp = f"""Previous Job Role of User {name} Organization: {company['name']}"""
            if(user_exp!=""):
                user_info["exp_user"] = user_exp

        edu_ = 1
        educations = profile.get("education", [])
        lst = []
        if educations !=[]:
            for edu in educations:
                title = edu.get("title", "Unknown Institute")
                start = normalize_date(edu.get("start_year"))
                end = normalize_date(edu.get("end_year"))

                if(edu_==1):
                    user_edu = f"""
                    User {name} currently studies in Institute: {title} Duration: {start}-{end}
                    """
                    edu_+=1
                else:
                    user_edu = f"""
                    User {name} Previouly studied in Institute: {title} Duration: {start}-{end}
                    """
                lst.append(user_edu)
        
        user_info["edu_user"] = lst

        certs = profile.get("certifications", [])
        lst = []
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
                lst.append(text)

        user_info["cert_user"] = lst

        lst = []
        activities = profile.get("activity", [])
        if(activities!=[]):
            for act in activities:
                raw_text = act.get("title", "")
                interaction = act.get("interaction", "")
                link = act.get("link", "")

                if not raw_text:
                    continue

                clean_activity = clean_text(raw_text, 250)
                if(interaction!=""):
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
                lst.append(text)
        user_info["act_user"] = lst    
        return {"status":"ok","chunks":user_info},200
    

    except Exception as e :
        return {"status":"Failed","reason":str(e)},500





if __name__ == "__main__":
    with open("samples/linkedINdata.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    build_chunks(data)

