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
        return "File not found."

    # Get the file extension
    file_extension = filename.split('.')[-1]
    print(file_extension)
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


def process_candidate_data(name: str, linkedin_file, exp_file, jd_file):
    app_state = {}
    if name is None:
        return "Candidate name is mandatory", app_state
    app_state["name"] = name
    try:
        # Read LinkedIn profile
        if linkedin_file:
            with open(linkedin_file.name, "r", encoding="utf-8") as f:
                profile_text = f.read()
            save_file(name, linkedin_file, True)
        else:
            profile_text = load_file(name, "profile.pdf")
        app_state["profile_text"] = profile_text

        # Read Resume
        if exp_file:
            with open(exp_file.name, "r", encoding="utf-8") as f:
                exp_summary = f.read()
            save_file(name, exp_file, False)
        else:
            exp_summary = load_file(name, "experience.txt")
        exp_summary = str(chunk_experience(exp_summary, model_name=default_chat_model, name=name))
        app_state["exp_summary"] = exp_summary

        # Read JD
        if jd_file:
            with open(jd_file.name, "r", encoding="utf-8") as f:
                jd_text = f.read()
            app_state["job_description"] = jd_text

    except Exception as e:
        print(f"Exception {e} while processing candidate data")
        return "failed", {}

    return "Success", app_state
