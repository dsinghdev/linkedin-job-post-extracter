import subprocess
import sys

def main():
    # Run scraping and cleaning
    print("Running scrape_and_clean.py...")
    scrape_clean_proc = subprocess.run([sys.executable, "scrape_and_clean.py"], capture_output=True, text=True)
    if scrape_clean_proc.returncode != 0:
        print("Error running scrape_and_clean.py:")
        print(scrape_clean_proc.stderr)
        return
    else:
        print("Scraping and cleaning completed successfully.")

    # Run LLM extraction
    print("Running llm_extraction.py...")
    llm_proc = subprocess.run([sys.executable, "llm_extraction.py"], capture_output=True, text=True)
    if llm_proc.returncode != 0:
        print("Error running llm_extraction.py:")
        print(llm_proc.stderr)
        return
    else:
        print("LLM extraction completed successfully.")

    print("All steps completed! Check the 'data/new' folder for results.")

if __name__ == "__main__":
    main()
