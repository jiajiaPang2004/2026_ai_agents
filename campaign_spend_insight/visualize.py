from tools import generate_html_report

if __name__ == "__main__":
    print("Refreshing Campaign Spend Distribution Report...")
    try:
        path = generate_html_report("distribution_report.html")
        print(f"\nReport updated successfully!")
        print(f"File Path: {path}")
        print("\nYou can now see insights directly beneath each table.")
    except Exception as e:
        print(f"Error: {e}")
