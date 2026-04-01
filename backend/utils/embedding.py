import json
import re
from typing import Dict, List, Any


# -------------------------------
# UTILITIES
# -------------------------------

def normalize_date(date_str: str) -> str:
    try:
        if not date_str:
            return "unknown"
        return date_str[:4]
    except Exception:
        return "unknown"


def clean_text(text: str, max_len: int = 300) -> str:
    try:
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        return text.strip()[:max_len]
    except Exception:
        return ""


def safe_get(d: Dict, key: str, default=None):
    try:
        return d.get(key, default)
    except Exception:
        return default


# -------------------------------
# MAIN CHUNK BUILDER
# -------------------------------

def build_chunks(profile: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not isinstance(profile, dict):
            raise ValueError("Invalid profile format")

        user_info = {
            "about_user":"",
            "exp_user": "",
            "edu_user": [],
            "cert_user": [],
            "act_user": [],
            "project_user": []
        }

        # -------------------------------
        # BASIC INFO
        # -------------------------------
        name = safe_get(profile, "name", "Unknown")
        profile_id = safe_get(profile, "id", "Unknown")
        location = safe_get(profile, "city", "Unknown")
        about = clean_text(safe_get(profile, "about", ""), 400)

        followers = safe_get(profile, "followers", 0)
        connections = safe_get(profile, "connections", 0)

        user_info["about_user"] = f"User name is {name}" + f"User is located in {location}"+ f"Profile ID is {profile_id}" 
        user_info["about_user"] += f"About user: {about}" if about else ""
        user_info["about_user"] += f"User has {followers} followers" + f"User has {connections} connections"
  

        # -------------------------------
        # PROJECTS
        # -------------------------------
        projects = safe_get(profile, "projects", [])

        if isinstance(projects, list):
            for proj in projects:
                if not isinstance(proj, dict):
                    continue

                title = safe_get(proj, "title", "Unknown Project")
                desc = clean_text(safe_get(proj, "description", ""), 300)
                start = safe_get(proj, "start_date", "Unknown")

                chunk = f"Project {title}. Started: {start}. Description: {desc}"
                user_info["project_user"].append(chunk)

        # -------------------------------
        # EXPERIENCE
        # -------------------------------
        company = safe_get(profile, "current_company", {})

        if isinstance(company, dict) and company.get("name"):
            user_info["exp_user"]= f"{name} currently works at {company['name']}"

        # -------------------------------
        # EDUCATION
        # -------------------------------
        educations = safe_get(profile, "education", [])

        if isinstance(educations, list):
            for edu in educations:
                if not isinstance(edu, dict):
                    continue

                title = safe_get(edu, "title", "Unknown Institute")
                start = normalize_date(safe_get(edu, "start_year"))
                end = normalize_date(safe_get(edu, "end_year"))

                user_info["edu_user"].append(
                    f"{name} studied at {title} from {start} to {end}"
                )

        # -------------------------------
        # CERTIFICATIONS
        # -------------------------------
        certs = safe_get(profile, "certifications", [])

        if isinstance(certs, list):
            for cert in certs:
                if not isinstance(cert, dict):
                    continue

                title = safe_get(cert, "title", "")
                issuer = safe_get(cert, "subtitle", "")
                cred_id = safe_get(cert, "credential_id", "")

                if title:
                    user_info["cert_user"].append(
                        f"{name} earned certification {title} from {issuer}. Credential ID: {cred_id}"
                    )

        # -------------------------------
        # ACTIVITIES
        # -------------------------------
        activities = safe_get(profile, "activity", [])

        if isinstance(activities, list):
            for act in activities:
                if not isinstance(act, dict):
                    continue

                raw_text = clean_text(safe_get(act, "title", ""), 250)
                interaction = safe_get(act, "interaction", "")
                link = safe_get(act, "link", "")

                if not raw_text:
                    continue

                interaction_lower = interaction.lower()

                if "shared" in interaction_lower:
                    action_type = "posted"
                elif "commented" in interaction_lower:
                    action_type = "commented"
                elif "liked" in interaction_lower:
                    action_type = "liked"
                else:
                    action_type = "interacted"

                chunk = f"{name} {action_type}: {raw_text}. Link: {link}"
                user_info["act_user"].append(chunk)

        # -------------------------------
        # CLEAN EMPTY STRINGS
        # -------------------------------

        return {
            "status": "ok",
            "chunks": user_info
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


# -------------------------------
# TEST
# -------------------------------

