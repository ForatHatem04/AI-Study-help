"""Simple GUI for AI Study Helper.

This Tkinter application lets users select documents, configure summary and quiz
options, and generate outputs without using the command line.
"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ai_study.extractors import extract_text_from_files
from ai_study.quiz import build_quiz_html, generate_mcqs
from ai_study.summarizer import summarize_text


class StudyHelperGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AI Study Helper")
        self.files: list[str] = []

        self._build_layout()

    def _build_layout(self) -> None:
        self.root.geometry("840x620")
        self.root.resizable(False, False)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            # Fall back silently if the theme is unavailable.
            pass

        accent_color = "#4C6FFF"
        style.configure("Accent.TButton", background=accent_color, foreground="white")
        style.map(
            "Accent.TButton",
            background=[("active", "#3A5AE5")],
            foreground=[("active", "white")],
        )
        style.configure("TFrame", padding=2)
        style.configure("TLabel", padding=2)

        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(main)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(
            header,
            text="Study Helper Dashboard",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Select your study materials, choose detailed summary and quiz options, and generate downloads in one click.",
            wraplength=780,
            font=("Segoe UI", 10),
            foreground="#4a4a4a",
        ).pack(anchor=tk.W)

        # File selection section
        file_frame = ttk.LabelFrame(main, text="Source Files", padding=10)
        file_frame.pack(fill=tk.X, pady=5)

        ttk.Button(file_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Clear", command=self.clear_files).pack(side=tk.LEFT, padx=5)

        self.file_list = tk.Listbox(file_frame, height=4)
        self.file_list.pack(fill=tk.X, expand=True, pady=8)

        # Options section
        options = ttk.LabelFrame(main, text="Options", padding=10)
        options.pack(fill=tk.X, pady=5)

        ttk.Label(options, text="Summary sentences:").grid(row=0, column=0, sticky=tk.W, padx=(0, 6))
        self.summary_var = tk.StringVar(value="25")
        ttk.Spinbox(options, from_=20, to=60, textvariable=self.summary_var, width=6).grid(
            row=0, column=1, sticky=tk.W
        )

        ttk.Label(options, text="Number of questions:").grid(row=0, column=2, sticky=tk.W, padx=(16, 6))
        self.questions_var = tk.StringVar(value="15")
        ttk.Spinbox(options, from_=5, to=50, textvariable=self.questions_var, width=6).grid(
            row=0, column=3, sticky=tk.W
        )

        # Output paths
        output = ttk.LabelFrame(main, text="Outputs", padding=10)
        output.pack(fill=tk.X, pady=5)

        default_downloads = Path.home() / "Downloads"
        ttk.Label(output, text="Summary file:").grid(row=0, column=0, sticky=tk.W)
        self.summary_path = tk.StringVar(value=str(default_downloads / "summary.txt"))
        ttk.Entry(output, textvariable=self.summary_path, width=40).grid(row=0, column=1, padx=6)
        ttk.Button(output, text="Browse", command=self.pick_summary_path).grid(row=0, column=2)

        ttk.Label(output, text="Quiz HTML:").grid(row=1, column=0, sticky=tk.W, pady=(6, 0))
        self.quiz_path = tk.StringVar(value=str(default_downloads / "quiz.html"))
        ttk.Entry(output, textvariable=self.quiz_path, width=40).grid(row=1, column=1, padx=6, pady=(6, 0))
        ttk.Button(output, text="Browse", command=self.pick_quiz_path).grid(row=1, column=2, pady=(6, 0))

        # Action buttons
        actions = ttk.Frame(main, padding=(0, 8))
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="Generate", style="Accent.TButton", command=self.generate).pack(side=tk.RIGHT)

        # Summary display
        display = ttk.LabelFrame(main, text="Generated Summary", padding=10)
        display.pack(fill=tk.BOTH, expand=True, pady=5)

        self.summary_box = tk.Text(display, wrap=tk.WORD, height=14, font=("Segoe UI", 10))
        scrollbar = ttk.Scrollbar(display, orient=tk.VERTICAL, command=self.summary_box.yview)
        self.summary_box.configure(yscrollcommand=scrollbar.set)
        self.summary_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_var = tk.StringVar(value="Select files to begin.")
        ttk.Label(main, textvariable=self.status_var).pack(anchor=tk.W, pady=(4, 0))

    def add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Choose documents", filetypes=[("Supported files", ".pdf .doc .docx .ppt .pptx")]
        )
        if paths:
            self.files.extend(paths)
            self.refresh_file_list()

    def clear_files(self) -> None:
        self.files = []
        self.refresh_file_list()

    def refresh_file_list(self) -> None:
        self.file_list.delete(0, tk.END)
        for file in self.files[-50:]:  # Prevent excessively tall lists
            self.file_list.insert(tk.END, file)
        self.status_var.set(f"Selected {len(self.files)} file(s).")

    def pick_summary_path(self) -> None:
        path = filedialog.asksaveasfilename(title="Save summary as", defaultextension=".txt")
        if path:
            self.summary_path.set(path)

    def pick_quiz_path(self) -> None:
        path = filedialog.asksaveasfilename(title="Save quiz as", defaultextension=".html")
        if path:
            self.quiz_path.set(path)

    def generate(self) -> None:
        try:
            if not self.files:
                messagebox.showwarning("No files", "Please select at least one document.")
                return

            summary_length = max(20, int(self.summary_var.get()))
            questions = min(50, int(self.questions_var.get()))
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter numeric values for summary length and questions.")
            return

        try:
            self.status_var.set("Processing...")
            self.root.update_idletasks()

            content = extract_text_from_files(self.files)
            summary = summarize_text(content, max_sentences=summary_length)
            quiz_questions = generate_mcqs(content, amount=questions)

            summary_file = Path(self.summary_path.get()).expanduser()
            quiz_file = Path(self.quiz_path.get()).expanduser()

            summary_file.parent.mkdir(parents=True, exist_ok=True)
            quiz_file.parent.mkdir(parents=True, exist_ok=True)

            summary_file.write_text(summary, encoding="utf-8")
            build_quiz_html(quiz_questions, summary, str(quiz_file))

            self.summary_box.delete("1.0", tk.END)
            self.summary_box.insert(tk.END, summary or "No summary generated.")

            self.status_var.set(f"Saved summary to {summary_file} and quiz to {quiz_file}.")
            messagebox.showinfo("Done", "Summary and quiz generated successfully.")
        except Exception as exc:  # pragma: no cover - GUI runtime safety
            messagebox.showerror("Error", f"An error occurred: {exc}")
            self.status_var.set("Something went wrong. Please try again.")


def launch() -> None:
    root = tk.Tk()
    StudyHelperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
