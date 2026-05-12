from pypdf import PdfReader, PdfWriter
from chunk_experience import chunk_experience
from get_llm_model import default_chat_model

def save_file(name, file):
    try:
        ext = file.split('.')[-1]
        file_path = f"docs/{name}/{file.name}"
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
    ext = filename.split('.')[-1]
    final_text = ""
    if ext == 'pdf':
        reader = PdfReader(f"docs/{name}/{filename}")
        for page in reader.pages:
            text = page.extract_text()
            if text:
                final_text += text
    else:
        with open(f"docs/{name}/{filename}", "r", encoding="utf-8") as f:
            final_text = f.read()
    return final_text


def process_candidate_data(name: str, linkedin_file, exp_file):
    app_state = {}
    app_state["candidate_name"] = name
    try:
        # Read LinkedIn profile
        if linkedin_file is not None:
            with open(linkedin_file.name, "r", encoding="utf-8") as f:
                linkedin_text = f.read()
            save_file(name, linkedin_file)
            app_state["linkedin_text"] = linkedin_text

        # Read Resume
        if exp_file is not None:
            with open(exp_file.name, "r", encoding="utf-8") as f:
                exp_text = f.read()
            save_file(name, exp_file)
            app_state["exp_text"] = chunk_experience(exp_text, model_name=default_chat_model, name=name)
    except Exception as e:
        print(f"Exception {e} while processing candidate data")
        return "failed", {}
    return "Success", app_state

def process_jd(jd_file, state):
    try:
        # Read jd file
        if jd_file is not None:
            with open(jd_file.name, "r", encoding="utf-8") as f:
                jd_text = f.read()
            state["job_description"] = jd_text
    except Exception as e:
        print(f"Exception {e} while processing candidate data")
        return "failed", state
    return "Success", state
