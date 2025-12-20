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
        self.root.geometry("940x700")
        self.root.resizable(False, False)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            # Fall back silently if the theme is unavailable.
            pass

        accent_color = "#4C6FFF"
        surface_color = "#f5f7fb"
        style.configure("Accent.TButton", background=accent_color, foreground="white", padding=6)
        style.map(
            "Accent.TButton",
            background=[("active", "#3A5AE5")],
            foreground=[("active", "white")],
        )
        style.configure("TFrame", padding=2)
        style.configure("Card.TLabelframe", background=surface_color, padding=12)
        style.configure("Card.TLabelframe.Label", background=surface_color, font=("Segoe UI", 11, "bold"))
        style.configure("Card.TFrame", background=surface_color)
        style.configure("Muted.TLabel", foreground="#4a4a4a")

        self.root.configure(background=surface_color)

        main = ttk.Frame(self.root, padding=18, style="Card.TFrame")
        main.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(main, style="Card.TFrame")
        header.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(
            header,
            text="Study Helper Studio",
            font=("Segoe UI", 22, "bold"),
            background=surface_color,
        ).pack(anchor=tk.W)
        ttk.Label(
            header,
            text=(
                "Drop in your study materials, request extended summaries (20+ sentences), and"
                " build up to 50 MCQs saved straight to your Downloads folder."
            ),
            wraplength=860,
            font=("Segoe UI", 11),
            style="Muted.TLabel",
            background=surface_color,
        ).pack(anchor=tk.W, pady=(4, 0))

        content = ttk.Frame(main, style="Card.TFrame")
        content.pack(fill=tk.BOTH, expand=True)

        # File selection section
        file_frame = ttk.LabelFrame(content, text="Source Files", style="Card.TLabelframe")
        file_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        file_actions = ttk.Frame(file_frame, style="Card.TFrame")
        file_actions.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(file_actions, text="Add Files", style="Accent.TButton", command=self.add_files).pack(
            side=tk.LEFT
        )
        ttk.Button(file_actions, text="Clear", command=self.clear_files).pack(side=tk.LEFT, padx=6)

        self.file_list = tk.Listbox(file_frame, height=8, font=("Segoe UI", 10))
        self.file_list.pack(fill=tk.BOTH, expand=True, pady=6)

        ttk.Label(
            file_frame,
            text="Tip: you can select multiple PDFs, Word docs, or PowerPoints at once.",
            style="Muted.TLabel",
            background=surface_color,
        ).pack(anchor=tk.W)

        # Options section
        options = ttk.LabelFrame(content, text="Summary & Quiz Options", style="Card.TLabelframe")
        options.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        ttk.Label(options, text="Summary sentences (min 20):", background=surface_color).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 6), pady=(0, 6)
        )
        self.summary_var = tk.StringVar(value="30")
        ttk.Spinbox(options, from_=20, to=80, textvariable=self.summary_var, width=7).grid(
            row=0, column=1, sticky=tk.W, pady=(0, 6)
        )

        ttk.Label(options, text="Number of MCQs (max 50):", background=surface_color).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 6), pady=(0, 6)
        )
        self.questions_var = tk.StringVar(value="25")
        ttk.Spinbox(options, from_=5, to=50, textvariable=self.questions_var, width=7).grid(
            row=1, column=1, sticky=tk.W, pady=(0, 6)
        )

        ttk.Label(options, text="Save locations (Downloads by default)", background=surface_color).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 4)
        )

        default_downloads = Path.home() / "Downloads"
        ttk.Label(options, text="Summary file:", background=surface_color).grid(row=3, column=0, sticky=tk.W)
        self.summary_path = tk.StringVar(value=str(default_downloads / "summary.txt"))
        ttk.Entry(options, textvariable=self.summary_path, width=40).grid(row=3, column=1, padx=6)
        ttk.Button(options, text="Browse", command=self.pick_summary_path).grid(row=3, column=2)

        ttk.Label(options, text="Quiz HTML:", background=surface_color).grid(row=4, column=0, sticky=tk.W, pady=(6, 0))
        self.quiz_path = tk.StringVar(value=str(default_downloads / "quiz.html"))
        ttk.Entry(options, textvariable=self.quiz_path, width=40).grid(row=4, column=1, padx=6, pady=(6, 0))
        ttk.Button(options, text="Browse", command=self.pick_quiz_path).grid(row=4, column=2, pady=(6, 0))

        ttk.Label(
            options,
            text="Both files will be created automatically if they don't exist.",
            style="Muted.TLabel",
            background=surface_color,
        ).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(6, 0))

        # Action buttons
        actions = ttk.Frame(main, padding=(0, 10), style="Card.TFrame")
        actions.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(actions, text="Generate Study Pack", style="Accent.TButton", command=self.generate).pack(
            side=tk.RIGHT
        )

        # Summary display
        display = ttk.LabelFrame(main, text="Generated Summary Preview", style="Card.TLabelframe")
        display.pack(fill=tk.BOTH, expand=True, pady=8)

        self.summary_box = tk.Text(display, wrap=tk.WORD, height=16, font=("Segoe UI", 10))
        scrollbar = ttk.Scrollbar(display, orient=tk.VERTICAL, command=self.summary_box.yview)
        self.summary_box.configure(yscrollcommand=scrollbar.set)
        self.summary_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_var = tk.StringVar(value="Select files to begin.")
        ttk.Label(main, textvariable=self.status_var, style="Muted.TLabel", background=surface_color).pack(
            anchor=tk.W, pady=(6, 0)
        )

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

            summary_length = max(24, int(self.summary_var.get()))
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

            summary_file = Path(self.summary_path.get() or "").expanduser()
            quiz_file = Path(self.quiz_path.get() or "").expanduser()

            # Default to Downloads if the user cleared the fields.
            default_downloads = Path.home() / "Downloads"
            if not summary_file.name:
                summary_file = default_downloads / "summary.txt"
            if not quiz_file.name:
                quiz_file = default_downloads / "quiz.html"

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
