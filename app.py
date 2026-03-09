import customtkinter as ctk
from tkinter import messagebox, ttk
import database
import sys
import os

# Ensure the working directory is set to this file's folder so 'quiz.db' is created correctly
os.chdir(os.path.dirname(os.path.abspath(__file__)))

TIME_LIMIT_SECONDS = 60 # 60 seconds per quiz

# Configure CustomTkinter
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Quiz Application Premium")
        self.root.geometry("900x650")
        
        # Initialize database
        database.initialize_db()
        
        # Frame container
        self.container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.show_main_menu()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_container()
        
        frame = ctk.CTkFrame(self.container, corner_radius=15)
        frame.pack(expand=True, padx=40, pady=40)
        
        title = ctk.CTkLabel(frame, text="⚡ Knowledge Nexus", font=ctk.CTkFont(size=32, weight="bold"))
        title.pack(pady=(40, 20), padx=40)
        
        subtitle = ctk.CTkLabel(frame, text="Select your portal access level", font=ctk.CTkFont(size=14), text_color="gray")
        subtitle.pack(pady=(0, 30))
        
        ctk.CTkButton(frame, text="👤  Start Quiz (Student)", command=self.show_student_login, 
                      height=50, width=250, font=ctk.CTkFont(size=16, weight="bold"), 
                      corner_radius=25).pack(pady=15)
                      
        ctk.CTkButton(frame, text="🔒  Admin Portal", command=self.show_admin_login, 
                      height=50, width=250, font=ctk.CTkFont(size=16), 
                      fg_color="transparent", border_width=2, hover_color="#333333",
                      corner_radius=25).pack(pady=15)
                      
        ctk.CTkButton(frame, text="Exit", command=self.root.destroy, 
                      height=40, width=150, fg_color="#cf3e3e", hover_color="#a83232",
                      corner_radius=20).pack(pady=(30, 40))

    def show_admin_login(self):
        self.clear_container()
        
        frame = ctk.CTkFrame(self.container, corner_radius=15)
        frame.pack(expand=True, padx=40, pady=40)
        
        ctk.CTkLabel(frame, text="Admin Authentication", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(40, 30), padx=60)
        
        password_entry = ctk.CTkEntry(frame, show="*", placeholder_text="Enter Admin Password", 
                                      height=45, width=250, corner_radius=10)
        password_entry.pack(pady=10)
        
        def login():
            if password_entry.get() == "admin":
                self.show_admin_panel()
            else:
                messagebox.showerror("Error", "Invalid Security Clearance")
        
        ctk.CTkButton(frame, text="Authenticate", command=login, height=45, width=250, corner_radius=10).pack(pady=(20, 10))
        ctk.CTkButton(frame, text="Return", command=self.show_main_menu, height=45, width=250, 
                      fg_color="transparent", border_width=1, hover_color="#333333").pack(pady=(0, 40))

    def show_admin_panel(self):
        self.clear_container()
        
        # Header
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="Admin Dashboard", font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")
        ctk.CTkButton(header_frame, text="Logout", command=self.show_main_menu, fg_color="#cf3e3e", 
                      hover_color="#a83232", width=100, height=35).pack(side="right")
        
        # Tabview
        tabview = ctk.CTkTabview(self.container, corner_radius=15)
        tabview.pack(fill="both", expand=True)
        
        tab_q = tabview.add("Manage Questions")
        tab_r = tabview.add("View Results")
        
        self.build_manage_questions_tab(tab_q)
        self.build_view_results_tab(tab_r)

    def build_manage_questions_tab(self, parent):
        top_frame = ctk.CTkFrame(parent, fg_color="transparent")
        top_frame.pack(fill="x", pady=5)
        
        # Form
        form_frame = ctk.CTkFrame(top_frame, corner_radius=10)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Add New Question", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        grid_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=5)
        
        q_entry = ctk.CTkEntry(grid_frame, placeholder_text="Enter question text here...", width=400)
        q_entry.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")
        
        a_entry = ctk.CTkEntry(grid_frame, placeholder_text="Option A")
        a_entry.grid(row=1, column=0, pady=5, padx=(0, 5), sticky="ew")
        b_entry = ctk.CTkEntry(grid_frame, placeholder_text="Option B")
        b_entry.grid(row=1, column=1, pady=5, padx=(5, 0), sticky="ew")
        
        c_entry = ctk.CTkEntry(grid_frame, placeholder_text="Option C")
        c_entry.grid(row=2, column=0, pady=5, padx=(0, 5), sticky="ew")
        d_entry = ctk.CTkEntry(grid_frame, placeholder_text="Option D")
        d_entry.grid(row=2, column=1, pady=5, padx=(5, 0), sticky="ew")
        
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        ans_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        ans_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(ans_frame, text="Correct Answer:").pack(side="left", padx=(0, 10))
        ans_var = ctk.StringVar(value="A")
        ctk.CTkOptionMenu(ans_frame, variable=ans_var, values=["A", "B", "C", "D"], width=70).pack(side="left")
        
        def save_q():
            q = q_entry.get().strip()
            a = a_entry.get().strip()
            b = b_entry.get().strip()
            c = c_entry.get().strip()
            d = d_entry.get().strip()
            ans = ans_var.get()
            
            if not all([q, a, b, c, d]):
                messagebox.showerror("Error", "All question and option fields are required!")
                return
                
            database.add_question(q, a, b, c, d, ans)
            q_entry.delete(0, 'end')
            a_entry.delete(0, 'end')
            b_entry.delete(0, 'end')
            c_entry.delete(0, 'end')
            d_entry.delete(0, 'end')
            refresh_list()
            messagebox.showinfo("Success", "Question successfully added to the database.")
            
        ctk.CTkButton(form_frame, text="Save Question", command=save_q, height=40).pack(pady=15, padx=20, fill="x")
        
        # List Area
        list_frame = ctk.CTkFrame(parent, corner_radius=10)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # Style treeview for dark mode integration
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2b2b2b",
                        bordercolor="#343638",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat",
                        font=('Roboto', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        columns = ("ID", "Question", "Answer")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Question", text="Question Snippet")
        self.tree.heading("Answer", text="Ans")
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Question", width=500)
        self.tree.column("Answer", width=50, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0,10))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        def refresh_list():
            for item in self.tree.get_children():
                self.tree.delete(item)
            questions = database.get_all_questions()
            for q in questions:
                # Truncate long questions for display
                display_q = q[1] if len(q[1]) < 60 else q[1][:57] + "..."
                self.tree.insert("", "end", values=(q[0], display_q, q[6]))
                
        def delete_q():
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a question to delete.")
                return
            item = self.tree.item(selected[0])
            q_id = item['values'][0]
            if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this question?"):
                database.delete_question(q_id)
                refresh_list()
                
        ctk.CTkButton(parent, text="Delete Selected Question", command=delete_q, fg_color="#cf3e3e", hover_color="#a83232").pack(pady=5)
        refresh_list()

    def build_view_results_tab(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "Name", "Score", "Total", "Date")
        res_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        res_tree.heading("ID", text="ID")
        res_tree.heading("Name", text="Student Name")
        res_tree.heading("Score", text="Score")
        res_tree.heading("Total", text="Total Qs")
        res_tree.heading("Date", text="Timestamp")
        
        res_tree.column("ID", width=40, anchor="center")
        res_tree.column("Name", width=200)
        res_tree.column("Score", width=80, anchor="center")
        res_tree.column("Total", width=80, anchor="center")
        res_tree.column("Date", width=150)
        
        res_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=res_tree.yview)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0,10))
        res_tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate
        def refresh_results():
            for item in res_tree.get_children():
                res_tree.delete(item)
            results = database.get_all_results()
            for r in results:
                # Format timestamp slightly
                ts = r[4].split('.')[0] if '.' in r[4] else r[4]
                res_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], ts))
                
        refresh_results()
        
        ctk.CTkButton(parent, text="Refresh Logs", command=refresh_results).pack(pady=10)

    def show_student_login(self):
        self.clear_container()
        
        frame = ctk.CTkFrame(self.container, corner_radius=15)
        frame.pack(expand=True, padx=40, pady=40)
        
        ctk.CTkLabel(frame, text="Candidate Registration", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(40, 10), padx=60)
        ctk.CTkLabel(frame, text="Please enter your identity to begin the assessment", text_color="gray").pack(pady=(0, 20))
        
        name_entry = ctk.CTkEntry(frame, placeholder_text="Full Name", height=45, width=280, justify="center")
        name_entry.pack(pady=15)
        
        def start():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Your name is required to begin the sequence.")
                return
            
            questions = database.get_all_questions()
            if not questions:
                messagebox.showinfo("Status", "The quiz bank is currently empty. Please notify the administrator.")
                return
                
            self.start_quiz(name, questions)
            
        ctk.CTkButton(frame, text="Initiate Sequence ➔", command=start, height=45, width=280, font=ctk.CTkFont(weight="bold")).pack(pady=15)
        ctk.CTkButton(frame, text="Cancel", command=self.show_main_menu, height=40, width=280, 
                      fg_color="transparent", border_width=1, hover_color="#333333").pack(pady=(0, 40))

    def start_quiz(self, student_name, questions):
        self.student_name = student_name
        self.questions = questions
        self.current_q_idx = 0
        self.score = 0
        self.time_left = TIME_LIMIT_SECONDS
        self.timer_id = None
        self.answers = {} # question_id -> selected_option
        
        self.show_quiz_interface()
        self.update_timer()

    def show_quiz_interface(self):
        self.clear_container()
        
        # Header Status Bar
        header_frame = ctk.CTkFrame(self.container, height=60, corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False) # Keep fixed height
        
        ctk.CTkLabel(header_frame, text=f"👤 {self.student_name}", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=20)
        
        # Fancy Timer
        self.timer_label = ctk.CTkLabel(header_frame, text=f"⏳ {self.time_left}s", 
                                        font=ctk.CTkFont(size=16, weight="bold"), text_color="#ff5c5c")
        self.timer_label.pack(side="right", padx=20)
        
        # Progress Bar
        progress = (self.current_q_idx) / len(self.questions)
        self.progress_bar = ctk.CTkProgressBar(self.container, height=8)
        self.progress_bar.pack(fill="x", pady=(0, 20), padx=10)
        self.progress_bar.set(progress)
        
        # Question Card
        q_frame = ctk.CTkFrame(self.container, corner_radius=15)
        q_frame.pack(fill="both", expand=True)
        
        current_q = self.questions[self.current_q_idx]
        q_id = current_q[0]
        
        top_row = ctk.CTkFrame(q_frame, fg_color="transparent")
        top_row.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(top_row, text=f"Question {self.current_q_idx + 1} of {len(self.questions)}", 
                     text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w")
                     
        ctk.CTkLabel(q_frame, text=current_q[1], wraplength=700, justify="left", 
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=30, pady=(0, 30))
        
        # Options
        self.var_ans = ctk.StringVar(value=self.answers.get(q_id, ""))
        
        options_frame = ctk.CTkFrame(q_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=40, pady=10)
        
        def create_option(text, val):
            # Create a custom look for radio buttons using CTkRadioButton
            rb = ctk.CTkRadioButton(options_frame, text=text, variable=self.var_ans, value=val,
                                    font=ctk.CTkFont(size=15), border_width_checked=6, 
                                    hover_color="#1f538d")
            rb.pack(anchor="w", pady=12)
            
        create_option(f"{current_q[2]}", "A")
        create_option(f"{current_q[3]}", "B")
        create_option(f"{current_q[4]}", "C")
        create_option(f"{current_q[5]}", "D")
        
        # Bottom Navigation
        nav_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        nav_frame.pack(fill="x", pady=20)
        
        def prev_q():
            self.save_current_answer()
            if self.current_q_idx > 0:
                self.current_q_idx -= 1
                self.show_quiz_interface()
                
        def next_q():
            self.save_current_answer()
            if self.current_q_idx < len(self.questions) - 1:
                self.current_q_idx += 1
                self.show_quiz_interface()
                
        def submit():
            self.save_current_answer()
            if messagebox.askyesno("Confirm Submission", "Are you sure you want to finalize your answers and submit the sequence?"):
                self.finish_quiz()
                
        if self.current_q_idx > 0:
            ctk.CTkButton(nav_frame, text="← Previous", command=prev_q, width=120, height=40,
                          fg_color="#444444", hover_color="#555555").pack(side="left")
            
        if self.current_q_idx < len(self.questions) - 1:
            ctk.CTkButton(nav_frame, text="Next →", command=next_q, width=120, height=40).pack(side="right")
        else:
            ctk.CTkButton(nav_frame, text="✓ Submit Sequence", command=submit, width=150, height=40,
                          fg_color="#28a745", hover_color="#218838").pack(side="right")

    def save_current_answer(self):
        q_id = self.questions[self.current_q_idx][0]
        selected = self.var_ans.get()
        if selected:
            self.answers[q_id] = selected

    def update_timer(self):
        if hasattr(self, 'timer_id') and self.timer_id is None:
            return
            
        if self.time_left > 0:
            self.time_left -= 1
            if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                # Flash red when low on time
                color = "#ff5c5c" if self.time_left <= 10 else "white"
                self.timer_label.configure(text=f"⏳ {self.time_left}s", text_color=color)
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.save_current_answer()
            self.timer_id = None
            messagebox.showinfo("Time Expired", "Sequence time limit reached. Auto-submitting answers.")
            self.finish_quiz()

    def finish_quiz(self):
        if hasattr(self, 'timer_id') and self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
        self.score = 0
        for q in self.questions:
            q_id = q[0]
            correct_ans = q[6]
            if self.answers.get(q_id) == correct_ans:
                self.score += 1
                
        database.save_result(self.student_name, self.score, len(self.questions))
        self.show_result_screen()

    def show_result_screen(self):
        self.clear_container()
        
        frame = ctk.CTkFrame(self.container, corner_radius=20)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        ctk.CTkLabel(frame, text="Sequence Complete", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(40, 10))
        ctk.CTkLabel(frame, text=f"Report for: {self.student_name}", text_color="gray", font=ctk.CTkFont(size=14)).pack()
        
        # Fancy Score Circle
        score_frame = ctk.CTkFrame(frame, width=200, height=200, corner_radius=100, fg_color="#1f538d")
        score_frame.pack(pady=40)
        score_frame.pack_propagate(False)
        
        percentage = (self.score / len(self.questions)) * 100
        
        # Determine color based on score
        if percentage >= 80:
            res_color = "#4ade80" # Green
        elif percentage >= 50:
            res_color = "#facc15" # Yellow
        else:
            res_color = "#f87171" # Red
            
        ctk.CTkLabel(score_frame, text=f"{self.score}/{len(self.questions)}", 
                     font=ctk.CTkFont(size=40, weight="bold")).pack(expand=True)
                     
        ctk.CTkLabel(frame, text=f"Final Grade: {percentage:.1f}%", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color=res_color).pack(pady=(0, 30))
        
        ctk.CTkButton(frame, text="Return to Main Menu", command=self.show_main_menu, 
                      height=45, width=200, corner_radius=20).pack(pady=(0, 40))

if __name__ == "__main__":
    root = ctk.CTk()
    app = QuizApp(root)
    root.mainloop()
