import os
from pypdf import PdfReader, PdfWriter
from chunk_experience import chunk_experience
from get_llm_model import default_chat_model

def save_file(name, file, is_profile):
    try:
        ext = file.split('.')[-1]
        if is_profile:
            filename = f"profile.{ext}"
        else:
            filename = f"experience.{ext}"
        file_path = f"docs/{name}/{filename}"
        directory = os.path.dirname(file_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        if ext == 'pdf':
            reader = PdfReader(file)
            writer = PdfWriter()
            # Copy existing pages
            for page in reader.pages:
                writer.add_page(page)
            with open(file_path, "wb", encoding="utf-8") as f:
                writer.write(f)
        elif ext == "txt":
            with open(file_path, "wb", encoding="utf-8") as f:
                f.write(file.getbuffer())
        else:
            print("Unsupported file")
            return "Unsupported File"
    except Exception as e:
        print(f"Exception {e} while processing file {file}")
        return "File not processed"
    return "File processed"


def load_file(name, filename):
    file_path = f"docs/{name}/{filename}"
    print(f"Loading file {file_path}")
    # Check if file exists
    if not os.path.exists(file_path):
        return ""

    # Get the file extension
    file_extension = filename.split('.')[-1]
    final_text = ""
    if file_extension == 'pdf':
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                final_text += text
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            final_text = f.read()
    return final_text


def process_candidate_data(name: str, linkedin_file, exp_file, jd_file, state):
    app_state = state
    print(app_state)
    if name:
        app_state["name"] = name
    try:
        # Read LinkedIn profile
        if linkedin_file.get("files"):
            with open(linkedin_file["files"][0], "r", encoding="utf-8") as f:
                profile_text = f.read()
            save_file(name, linkedin_file["files"][0], True)
        elif linkedin_file.get("text"):
            profile_text = linkedin_file["text"]
        elif app_state.get("profile_text", "") != "":
            print("Profile already present in state")
            profile_text = app_state["profile_text"]
        else:
            profile_text = load_file(name, "profile.pdf")
        app_state["profile_text"] = profile_text

        # Read Resume
        if exp_file.get("files"):
            with open(exp_file["files"][0], "r", encoding="utf-8") as f:
                exp_summary = f.read()
            exp_summary = str(chunk_experience(exp_summary, model_name=default_chat_model, name=name))
            save_file(name, exp_file["files"][0], False)
        elif exp_file.get("text"):
            exp_summary = exp_file["text"]
        elif app_state.get("exp_summary", "") != "":
            exp_summary = app_state["exp_summary"]
            print("Experience already present in state")
        else:
            exp_summary = load_file(name, "experience.txt")
            # exp_summary = str(chunk_experience(exp_summary, model_name=default_chat_model, name=name))
            exp_summary =  "chunks={'Improving Blackduck Performance': ExperienceChunk(label='Upgrading Blackduck for better performance', keywords=['blackduck', 'modern stack', 'scanning tool', 'upgrade', 'performance improvement'], content=['upgraded the application to modern stack', 'improved scan time from 8+ hours to within 10-15 minutes', 'enabled 2000+ daily scans across 5000+ applications']), 'Expert Engineer Program': ExperienceChunk(label='Selected for Expert Engineer program and promoted to VP', keywords=['Expert Engineer program', 'promoted to VP', 'technical leadership training', 'firm-wide visibility and appreciation', 'visibility and recognition within firm-wide'], content=['joined the Expert Engineer program', 'promoted to VP in 2019', 'recieved lot of admiration and respect from management and team members']), 'Leading APAC Public Cloud SRE Team': ExperienceChunk(label='Led global public cloud SRE team and helped customers with AWS adoption', keywords=['APAC Public Cloud SRE Team', 'AWS adoption', 'platform operations', '24/7 support for customers using AWS platform', ' content'], content=['led a new APAC-based public cloud SRE team', 'helped customers with adopting and troubleshooting AWS technology', 'identified gaps in the setup for better operations']), 'Building Self-Service System': ExperienceChunk(label='Developed self-service system to reduce manual effort and support tickets', keywords=['self-service system', 'elasticsearch', 'indexes', 'cost-saving benefits', 'productivity gain'], content=['created a self-service system', 'reduced manual effort by 50%', 'increased productivity by 35%'])} topic_map={'Improved Blackduck Performance and AWS Adoption': ['Improving Blackduck Performance'], 'Technical Leadership and Industry Recognition': ['Expert Engineer Program'], 'Cloud Operations and Customer Support': ['Leading APAC Public Cloud SRE Team', 'Building Self-Service System']}"
        app_state["exp_summary"] = exp_summary

        # Read JD
        if jd_file.get("files"):
            with open(jd_file["files"][0], "r", encoding="utf-8") as f:
                jd_text = f.read()
            app_state["job_description"] = jd_text
        elif jd_file.get("text"):
            app_state["job_description"] = jd_file["text"]

    except Exception as e:
        print(f"Exception {e} while processing candidate data")
        return "## Failure while processing files", {}

    return "## Data has been processed successfully.", app_state
