"""Quarantine Tab - Manage quarantined files"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
from pathlib import Path

class QuarantineTab:
    def __init__(self, parent):
        self.parent = parent
        self.quarantine_dir = Path("quarantine")
        self.quarantine_dir.mkdir(exist_ok=True)
        
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        self.refresh_list()
    
    def _create_widgets(self):
        # Control buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Restore Selected", command=self.restore_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete All", command=self.delete_all).pack(side=tk.LEFT, padx=5)
        
        # File list
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("File", "Original Path", "Date", "Threat", "Size")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 200 if col in ["File", "Original Path"] else 150
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Info
        info_frame = ttk.LabelFrame(self.frame, text="Quarantine Info", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="Files in quarantine: 0 | Total size: 0 KB")
        self.info_label.pack()
    
    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        
        total_files = 0
        total_size = 0
        
        if self.quarantine_dir.exists():
            for file in self.quarantine_dir.iterdir():
                if file.is_file():
                    try:
                        stat = file.stat()
                        size = stat.st_size
                        mtime = stat.st_mtime
                        
                        import time
                        date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
                        
                        # Try to read metadata
                        meta_file = file.with_suffix(file.suffix + '.meta')
                        original_path = "Unknown"
                        threat = "N/A"
                        
                        if meta_file.exists():
                            try:
                                with open(meta_file, 'r') as f:
                                    lines = f.readlines()
                                    for line in lines:
                                        if line.startswith('original_path:'):
                                            original_path = line.split(':', 1)[1].strip()
                                        elif line.startswith('threat_level:'):
                                            threat = line.split(':', 1)[1].strip()
                            except:
                                pass
                        
                        self.tree.insert('', 'end', values=(
                            file.name, original_path, date_str, threat, f"{size // 1024} KB"
                        ))
                        
                        total_files += 1
                        total_size += size
                    except:
                        continue
        
        self.info_label.config(text=f"Files in quarantine: {total_files} | Total size: {total_size // 1024} KB")
    
    def restore_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select files to restore")
            return
        
        restored = 0
        for item in selected:
            filename = self.tree.item(item)['values'][0]
            file_path = self.quarantine_dir / filename
            meta_path = file_path.with_suffix(file_path.suffix + '.meta')
            
            if file_path.exists():
                # Read original path from metadata
                original_path = None
                if meta_path.exists():
                    try:
                        with open(meta_path, 'r') as f:
                            for line in f:
                                if line.startswith('original_path:'):
                                    original_path = line.split(':', 1)[1].strip()
                                    break
                    except:
                        pass
                
                if original_path and messagebox.askyesno("Restore", f"Restore {filename} to {original_path}?"):
                    try:
                        shutil.move(str(file_path), original_path)
                        if meta_path.exists():
                            meta_path.unlink()
                        restored += 1
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to restore: {e}")
        
        if restored > 0:
            messagebox.showinfo("Success", f"Restored {restored} file(s)")
            self.refresh_list()
    
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select files to delete")
            return
        
        if not messagebox.askyesno("Confirm", f"Permanently delete {len(selected)} file(s)?"):
            return
        
        deleted = 0
        for item in selected:
            filename = self.tree.item(item)['values'][0]
            file_path = self.quarantine_dir / filename
            meta_path = file_path.with_suffix(file_path.suffix + '.meta')
            
            try:
                if file_path.exists():
                    file_path.unlink()
                if meta_path.exists():
                    meta_path.unlink()
                deleted += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {filename}: {e}")
        
        if deleted > 0:
            messagebox.showinfo("Success", f"Deleted {deleted} file(s)")
            self.refresh_list()
    
    def delete_all(self):
        if not messagebox.askyesno("Confirm", "Permanently delete ALL quarantined files?"):
            return
        
        deleted = 0
        if self.quarantine_dir.exists():
            for file in self.quarantine_dir.iterdir():
                try:
                    file.unlink()
                    deleted += 1
                except:
                    continue
        
        messagebox.showinfo("Success", f"Deleted {deleted} file(s)")
        self.refresh_list()
    
    def get_frame(self):
        return self.frame
