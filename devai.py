import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
import math
import re

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("pip install google-generativeai")

class BharatiyaAI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bharatiya AI - Intelligent Assistant")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0f4f8")
        
        # Gemini API setup
        self.api_key = "AIzaSyAcIHULP7zTzi1Z95YqTgGX3eKFc2-HOeQ"
        self.model = None
        self.chat = None
        self.conversation_history = []
        
        # Animation variables
        self.angle = 0
        
        # Search variables
        self.search_results = []
        self.current_search_index = 0
        
        # Create UI
        self.create_ui()
        
        # Start logo animation
        self.animate_logo()
        
    def create_ui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg="#1e3a8a", height=120)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo Canvas (Fan)
        self.logo_canvas = tk.Canvas(header_frame, width=80, height=80, 
                                     bg="#1e3a8a", highlightthickness=0)
        self.logo_canvas.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Title Section
        title_section = tk.Frame(header_frame, bg="#1e3a8a")
        title_section.pack(side=tk.LEFT, padx=10, pady=20)
        
        title_label = tk.Label(title_section, text="Bharatiya AI", 
                              font=("Helvetica", 28, "bold"),
                              fg="white", bg="#1e3a8a")
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_section, 
                                 text="Your Intelligent Problem-Solving Assistant",
                                 font=("Helvetica", 11),
                                 fg="#93c5fd", bg="#1e3a8a")
        subtitle_label.pack(anchor=tk.W)
        
        # API Key Frame
        api_frame = tk.Frame(self.root, bg="#f0f4f8")
        api_frame.pack(fill=tk.X, padx=30, pady=15)
        
        api_label = tk.Label(api_frame, text="Gemini API Key:", 
                            font=("Helvetica", 10, "bold"),
                            fg="#1e3a8a", bg="#f0f4f8")
        api_label.pack(side=tk.LEFT)
        
        self.api_entry = tk.Entry(api_frame, font=("Helvetica", 10),
                                 show="*", width=35, relief=tk.FLAT,
                                 bg="white", fg="#1e3a8a", bd=1)
        self.api_entry.pack(side=tk.LEFT, padx=10, ipady=5)
        
        connect_btn = tk.Button(api_frame, text="Connect", 
                               command=self.connect_gemini,
                               font=("Helvetica", 10, "bold"),
                               bg="#2563eb", fg="white",
                               relief=tk.FLAT, padx=20, pady=5,
                               cursor="hand2", activebackground="#1e40af")
        connect_btn.pack(side=tk.LEFT, padx=5)
        
        # Search Frame
        search_frame = tk.Frame(api_frame, bg="white", relief=tk.FLAT, bd=1)
        search_frame.pack(side=tk.RIGHT, padx=10)
        
        search_icon = tk.Label(search_frame, text="🔍", 
                              font=("Helvetica", 12),
                              bg="white", fg="#64748b")
        search_icon.pack(side=tk.LEFT, padx=(8, 2))
        
        self.search_entry = tk.Entry(search_frame, font=("Helvetica", 10),
                                     width=25, relief=tk.FLAT,
                                     bg="white", fg="#1e3a8a", bd=0)
        self.search_entry.pack(side=tk.LEFT, ipady=5)
        self.search_entry.bind("<KeyRelease>", self.search_conversation)
        self.search_entry.bind("<Return>", self.next_search_result)
        
        search_btn = tk.Button(search_frame, text="Search", 
                              command=self.perform_search,
                              font=("Helvetica", 9, "bold"),
                              bg="#60a5fa", fg="white",
                              relief=tk.FLAT, padx=10, pady=4,
                              cursor="hand2", activebackground="#3b82f6")
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Search navigation buttons
        nav_frame = tk.Frame(api_frame, bg="#f0f4f8")
        nav_frame.pack(side=tk.RIGHT, padx=5)
        
        self.prev_btn = tk.Button(nav_frame, text="◀", 
                                 command=self.prev_search_result,
                                 font=("Helvetica", 10, "bold"),
                                 bg="#e0e7ff", fg="#1e3a8a",
                                 relief=tk.FLAT, padx=8, pady=2,
                                 cursor="hand2", state=tk.DISABLED,
                                 activebackground="#c7d2fe")
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        
        self.search_counter = tk.Label(nav_frame, text="0/0",
                                      font=("Helvetica", 9),
                                      fg="#64748b", bg="#f0f4f8")
        self.search_counter.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = tk.Button(nav_frame, text="▶", 
                                 command=self.next_search_result,
                                 font=("Helvetica", 10, "bold"),
                                 bg="#e0e7ff", fg="#1e3a8a",
                                 relief=tk.FLAT, padx=8, pady=2,
                                 cursor="hand2", state=tk.DISABLED,
                                 activebackground="#c7d2fe")
        self.next_btn.pack(side=tk.LEFT, padx=2)
        
        # Main container with chat and info panel
        main_container = tk.Frame(self.root, bg="#f0f4f8")
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Chat Display Area
        chat_frame = tk.Frame(main_container, bg="white", relief=tk.FLAT, bd=1)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            font=("Helvetica", 11),
            bg="white",
            fg="#1e293b",
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for chat styling
        self.chat_display.tag_config("user", foreground="#2563eb", font=("Helvetica", 11, "bold"))
        self.chat_display.tag_config("ai", foreground="#059669", font=("Helvetica", 11, "bold"))
        self.chat_display.tag_config("time", foreground="#64748b", font=("Helvetica", 9))
        self.chat_display.tag_config("error", foreground="#dc2626", font=("Helvetica", 10))
        self.chat_display.tag_config("highlight", background="#fef08a")
        
        # Info Panel
        info_frame = tk.Frame(main_container, bg="white", relief=tk.FLAT, 
                             bd=1, width=280)
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        info_frame.pack_propagate(False)
        
        # Info Panel Title
        info_title = tk.Label(info_frame, text="Chat Information", 
                             font=("Helvetica", 13, "bold"),
                             fg="#1e3a8a", bg="white")
        info_title.pack(pady=(15, 10), padx=15, anchor=tk.W)
        
        # Divider
        tk.Frame(info_frame, bg="#e2e8f0", height=1).pack(fill=tk.X, padx=15)
        
        # Statistics
        stats_frame = tk.Frame(info_frame, bg="white")
        stats_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.create_stat_row(stats_frame, "Total Messages:", "0", 0)
        self.create_stat_row(stats_frame, "Your Messages:", "0", 1)
        self.create_stat_row(stats_frame, "AI Responses:", "0", 2)
        self.create_stat_row(stats_frame, "Connection:", "Disconnected", 3)
        
        # Quick Actions
        tk.Frame(info_frame, bg="#e2e8f0", height=1).pack(fill=tk.X, padx=15, pady=10)
        
        actions_label = tk.Label(info_frame, text="Quick Actions", 
                                font=("Helvetica", 11, "bold"),
                                fg="#1e3a8a", bg="white")
        actions_label.pack(pady=(10, 10), padx=15, anchor=tk.W)
        
        # Action Buttons
        btn_frame = tk.Frame(info_frame, bg="white")
        btn_frame.pack(fill=tk.X, padx=15, pady=5)
        
        clear_btn = tk.Button(btn_frame, text="Clear Chat", 
                             command=self.clear_chat,
                             font=("Helvetica", 9, "bold"),
                             bg="#ef4444", fg="white",
                             relief=tk.FLAT, pady=8,
                             cursor="hand2", activebackground="#dc2626")
        clear_btn.pack(fill=tk.X, pady=3)
        
        export_btn = tk.Button(btn_frame, text="Export Chat", 
                              command=self.export_chat,
                              font=("Helvetica", 9, "bold"),
                              bg="#3b82f6", fg="white",
                              relief=tk.FLAT, pady=8,
                              cursor="hand2", activebackground="#2563eb")
        export_btn.pack(fill=tk.X, pady=3)
        
        # Tips Section
        tk.Frame(info_frame, bg="#e2e8f0", height=1).pack(fill=tk.X, padx=15, pady=10)
        
        tips_label = tk.Label(info_frame, text="💡 Tips", 
                             font=("Helvetica", 11, "bold"),
                             fg="#1e3a8a", bg="white")
        tips_label.pack(pady=(10, 5), padx=15, anchor=tk.W)
        
        tips_text = tk.Label(info_frame, 
                            text="• Use search to find\n  past conversations\n\n"
                                 "• Press Enter to send\n  messages\n\n"
                                 "• Shift+Enter for\n  new lines",
                            font=("Helvetica", 9),
                            fg="#64748b", bg="white",
                            justify=tk.LEFT)
        tips_text.pack(padx=15, anchor=tk.W)
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg="#f0f4f8")
        input_frame.pack(fill=tk.X, padx=30, pady=15)
        
        # Input text with border
        input_container = tk.Frame(input_frame, bg="white", relief=tk.FLAT, bd=1)
        input_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.input_field = tk.Text(input_container, height=3, 
                                   font=("Helvetica", 11),
                                   bg="white", fg="#1e293b",
                                   relief=tk.FLAT, wrap=tk.WORD,
                                   padx=10, pady=10, bd=0)
        self.input_field.pack(fill=tk.BOTH, expand=True)
        self.input_field.bind("<Return>", self.handle_enter)
        
        send_btn = tk.Button(input_frame, text="Send ➤", 
                            command=self.send_message,
                            font=("Helvetica", 12, "bold"),
                            bg="#2563eb", fg="white",
                            relief=tk.FLAT, padx=30, pady=15,
                            cursor="hand2", activebackground="#1e40af")
        send_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Footer
        footer = tk.Frame(self.root, bg="#1e3a8a", height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        footer_label = tk.Label(footer, 
                               text="Powered by Nikhil Goswami - AI Expert & Developer",
                               font=("Helvetica", 10, "bold"),
                               fg="white", bg="#1e3a8a")
        footer_label.pack(pady=10)
        
        # Stats variables
        self.total_messages = 0
        self.user_messages = 0
        self.ai_messages = 0
        
        # Welcome message
        self.display_message("System", 
                           "Welcome to Bharatiya AI! Please enter your Gemini API key to get started.",
                           "ai")
        
    def create_stat_row(self, parent, label, value, row):
        """Create a statistics row"""
        label_widget = tk.Label(parent, text=label, 
                               font=("Helvetica", 9),
                               fg="#64748b", bg="white")
        label_widget.grid(row=row, column=0, sticky=tk.W, pady=3)
        
        value_widget = tk.Label(parent, text=value, 
                               font=("Helvetica", 9, "bold"),
                               fg="#1e3a8a", bg="white")
        value_widget.grid(row=row, column=1, sticky=tk.E, pady=3)
        
        parent.grid_columnconfigure(1, weight=1)
        
        # Store references for updating
        if not hasattr(self, 'stat_labels'):
            self.stat_labels = {}
        self.stat_labels[label] = value_widget
        
    def update_stats(self):
        """Update statistics display"""
        if hasattr(self, 'stat_labels'):
            self.stat_labels["Total Messages:"].config(text=str(self.total_messages))
            self.stat_labels["Your Messages:"].config(text=str(self.user_messages))
            self.stat_labels["AI Responses:"].config(text=str(self.ai_messages))
            status = "Connected" if self.api_key else "Disconnected"
            color = "#059669" if self.api_key else "#dc2626"
            self.stat_labels["Connection:"].config(text=status, fg=color)
        
    def draw_fan_logo(self):
        """Draw animated fan logo"""
        self.logo_canvas.delete("all")
        center_x, center_y = 40, 40
        radius = 30
        
        # Draw 4 fan blades
        for i in range(4):
            angle = self.angle + (i * 90)
            rad = math.radians(angle)
            
            # Create curved blade
            self.logo_canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=angle - 30, extent=60,
                fill="#60a5fa", outline="#2563eb", width=2
            )
        
        # Center circle
        self.logo_canvas.create_oval(
            center_x - 8, center_y - 8,
            center_x + 8, center_y + 8,
            fill="#1e3a8a", outline="#93c5fd", width=2
        )
        
    def animate_logo(self):
        """Animate the fan logo"""
        self.angle = (self.angle + 2) % 360
        self.draw_fan_logo()
        self.root.after(50, self.animate_logo)
        
    def connect_gemini(self):
        """Connect to Gemini AI"""
        if not GEMINI_AVAILABLE:
            messagebox.showerror("Error", 
                               "Google Generative AI library not installed.\n"
                               "Install with: pip install google-generativeai")
            return
            
        api_key = self.api_entry.get().strip()
        if not api_key:
            messagebox.showwarning("Warning", "Please enter your Gemini API key!")
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.chat = self.model.start_chat(history=[])
            self.api_key = api_key
            
            self.display_message("System", 
                               "Successfully connected to Gemini AI! You can now ask me anything.",
                               "ai")
            self.update_stats()
            messagebox.showinfo("Success", "Connected to Gemini AI successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
            self.display_message("System", 
                               f"Connection failed: {str(e)}",
                               "error")
    
    def handle_enter(self, event):
        """Handle Enter key press"""
        if event.state & 0x1:  # Shift+Enter for new line
            return
        else:
            self.send_message()
            return "break"
    
    def send_message(self):
        """Send message to AI"""
        message = self.input_field.get("1.0", tk.END).strip()
        
        if not message:
            return
        
        if not self.api_key or not self.chat:
            messagebox.showwarning("Warning", 
                                 "Please connect to Gemini AI first!")
            return
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Display user message
        self.display_message("You", message, "user")
        self.user_messages += 1
        self.total_messages += 1
        self.update_stats()
        
        # Get AI response in separate thread
        thread = threading.Thread(target=self.get_ai_response, args=(message,))
        thread.daemon = True
        thread.start()
    
    def get_ai_response(self, message):
        """Get response from Gemini AI"""
        try:
            # Show typing indicator
            self.root.after(0, lambda: self.display_message("Bharatiya AI", 
                                                           "Thinking...", "ai"))
            
            # Get response from Gemini
            response = self.chat.send_message(message)
            response_text = response.text
            
            # Remove typing indicator and show response
            self.root.after(0, lambda: self.chat_display.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.chat_display.delete("end-2l", "end-1l"))
            self.root.after(0, lambda: self.chat_display.config(state=tk.DISABLED))
            
            self.root.after(0, lambda: self.display_message("Bharatiya AI", 
                                                           response_text, "ai"))
            self.ai_messages += 1
            self.total_messages += 1
            self.root.after(0, self.update_stats)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.display_message("System", 
                                                           error_msg, "error"))
    
    def display_message(self, sender, message, tag):
        """Display message in chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M")
        
        self.chat_display.insert(tk.END, f"{sender}", tag)
        self.chat_display.insert(tk.END, f" • {timestamp}\n", "time")
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Store in history for search
        self.conversation_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })
    
    def search_conversation(self, event=None):
        """Search through conversation in real-time"""
        search_term = self.search_entry.get().strip()
        
        # Clear previous highlights
        self.chat_display.tag_remove("highlight", "1.0", tk.END)
        
        if not search_term:
            self.search_results = []
            self.update_search_ui()
            return
            
        # Search in chat display
        self.search_results = []
        start_pos = "1.0"
        
        while True:
            pos = self.chat_display.search(search_term, start_pos, 
                                          stopindex=tk.END, nocase=True)
            if not pos:
                break
            
            end_pos = f"{pos}+{len(search_term)}c"
            self.search_results.append((pos, end_pos))
            start_pos = end_pos
        
        self.current_search_index = 0
        self.update_search_ui()
        
        if self.search_results:
            self.highlight_current_result()
    
    def perform_search(self):
        """Perform search when search button is clicked"""
        self.search_conversation()
    
    def highlight_current_result(self):
        """Highlight current search result"""
        if not self.search_results:
            return
        
        # Remove all highlights first
        self.chat_display.tag_remove("highlight", "1.0", tk.END)
        
        # Highlight current result
        pos, end_pos = self.search_results[self.current_search_index]
        self.chat_display.tag_add("highlight", pos, end_pos)
        self.chat_display.see(pos)
    
    def next_search_result(self, event=None):
        """Go to next search result"""
        if not self.search_results:
            return
        
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self.highlight_current_result()
        self.update_search_ui()
    
    def prev_search_result(self):
        """Go to previous search result"""
        if not self.search_results:
            return
        
        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        self.highlight_current_result()
        self.update_search_ui()
    
    def update_search_ui(self):
        """Update search navigation UI"""
        total = len(self.search_results)
        current = self.current_search_index + 1 if total > 0 else 0
        
        self.search_counter.config(text=f"{current}/{total}")
        
        if total > 0:
            self.prev_btn.config(state=tk.NORMAL)
            self.next_btn.config(state=tk.NORMAL)
        else:
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """Clear chat history"""
        result = messagebox.askyesno("Clear Chat", 
                                    "Are you sure you want to clear all chat history?")
        if result:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            self.conversation_history = []
            self.total_messages = 0
            self.user_messages = 0
            self.ai_messages = 0
            self.update_stats()
            
            # Reset chat with Gemini
            if self.model:
                self.chat = self.model.start_chat(history=[])
            
            self.display_message("System", "Chat cleared successfully!", "ai")
    
    def export_chat(self):
        """Export chat to text file"""
        if not self.conversation_history:
            messagebox.showinfo("Export", "No conversation to export!")
            return
        
        try:
            filename = f"bharatiya_ai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("BHARATIYA AI - CONVERSATION EXPORT\n")
                f.write("=" * 60 + "\n\n")
                
                for entry in self.conversation_history:
                    f.write(f"[{entry['timestamp']}] {entry['sender']}\n")
                    f.write(f"{entry['message']}\n\n")
                
                f.write("=" * 60 + "\n")
                f.write("Powered by Nikhil Goswami - AI Expert & Developer\n")
                f.write("=" * 60 + "\n")
            
            messagebox.showinfo("Export Successful", 
                              f"Chat exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error: {str(e)}")

def main():
    root = tk.Tk()
    app = BharatiyaAI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
