import GUI 
import tkinter as tk


def main():
    # Create the main application window
    app = tk.Window(themename='flatly', title='URL Submission App')
    
    # Button to prompt the user to enter a URL
    submit_btn = tk.Button(app, text='Submit path', command=GUI.process_path, bootstyle=(PRIMARY))
    submit_btn.pack(pady=20, padx=20)
    
    # Start the application
    app.mainloop()


if __name__ == "__main__":
    main()