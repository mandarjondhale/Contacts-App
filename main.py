import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime, timedelta

# ── palette ───────────────────────────────────────────────────────────────────
C = {
    "bg":      "#F7F7F5",
    "sidebar": "#FFFFFF",
    "card":    "#FFFFFF",
    "border":  "#E5E5E3",
    "accent":  "#1A1A1A",
    "muted":   "#888784",
    "text":    "#1A1A1A",
    "subtext": "#6B6B68",
    "danger":  "#E24B4A",
    "avatars": ["#E6F1FB","#E1F5EE","#EEEDFE","#FAECE7","#FAEEDA"],
    "av_text": ["#0C447C","#085041","#3C3489","#712B13","#633806"],
    "star_on": "#F59E0B",
    "star_off":"#D1D1CE",
}
FONT   = ("Segoe UI", 10)
FONTSM = ("Segoe UI", 9)
FONTMD = ("Segoe UI", 11)
FONTLG = ("Segoe UI", 13, "bold")
FONTH  = ("Segoe UI", 17, "bold")

# ── persistence ───────────────────────────────────────────────────────────────
DATA_FILE = "contacts.json"

def load_contacts():
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
        # migrate old flat format {"name": "number"} → new format
        migrated = {}
        for k, v in data.items():
            if isinstance(v, dict):
                migrated[k] = v
            else:
                migrated[k] = {
                    "number":    v,
                    "favourite": False,
                    "added":     "2000-01-01",
                }
        return migrated
    except Exception:
        return {}

def save_contacts(contacts):
    with open(DATA_FILE, "w") as f:
        json.dump(contacts, f, indent=2)

def today_str():
    return datetime.today().strftime("%Y-%m-%d")

def added_this_week(contacts):
    cutoff = datetime.today() - timedelta(days=7)
    count = 0
    for v in contacts.values():
        try:
            if datetime.strptime(v["added"], "%Y-%m-%d") >= cutoff:
                count += 1
        except Exception:
            pass
    return count

# ── helpers ───────────────────────────────────────────────────────────────────
def initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"

def avatar_colors(name):
    idx = sum(ord(c) for c in name) % len(C["avatars"])
    return C["avatars"][idx], C["av_text"][idx]

# ── modal dialog ──────────────────────────────────────────────────────────────
class ContactDialog(tk.Toplevel):
    def __init__(self, parent, title, name="", number="", on_save=None):
        super().__init__(parent)
        self.on_save = on_save
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=C["bg"])
        self.grab_set()

        w, h = 380, 310
        px = parent.winfo_rootx() + (parent.winfo_width()  - w) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{px}+{py}")

        # header
        hdr = tk.Frame(self, bg=C["sidebar"], pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, font=FONTLG,
                 bg=C["sidebar"], fg=C["text"]).pack(padx=24, anchor="w")
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        body = tk.Frame(self, bg=C["bg"], pady=20)
        body.pack(fill="both", expand=True, padx=24)

        tk.Label(body, text="Full name", font=FONTSM,
                 bg=C["bg"], fg=C["subtext"]).pack(anchor="w", pady=(0,4))
        self.name_var = tk.StringVar(value=name)
        self._entry(body, self.name_var).pack(fill="x", ipady=6, pady=(0,14))

        tk.Label(body, text="Phone number", font=FONTSM,
                 bg=C["bg"], fg=C["subtext"]).pack(anchor="w", pady=(0,4))
        self.num_var = tk.StringVar(value=number)
        self._entry(body, self.num_var).pack(fill="x", ipady=6, pady=(0,20))

        btns = tk.Frame(body, bg=C["bg"])
        btns.pack(fill="x")
        tk.Button(btns, text="Cancel", font=FONT, bg=C["sidebar"],
                  fg=C["subtext"], activebackground=C["border"],
                  relief="flat", bd=1, padx=16, pady=7,
                  command=self.destroy).pack(side="right", padx=(8,0))
        tk.Button(btns, text="Save contact", font=FONT, bg=C["accent"],
                  fg="white", activebackground="#333",
                  relief="flat", bd=0, padx=16, pady=7,
                  command=self._submit).pack(side="right")

    def _entry(self, parent, var):
        return tk.Entry(parent, textvariable=var, font=FONTMD,
                        bg=C["card"], fg=C["text"], insertbackground=C["text"],
                        relief="flat", bd=1, highlightthickness=1,
                        highlightbackground=C["border"],
                        highlightcolor=C["accent"])

    def _submit(self):
        n   = self.name_var.get().strip()
        num = self.num_var.get().strip()
        if not n or not num:
            messagebox.showerror("Validation", "Both fields are required.", parent=self)
            return
        if self.on_save:
            self.on_save(n, num)
        self.destroy()

# ── main app ──────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contacts")
        self.geometry("860x560")
        self.minsize(720, 460)
        self.configure(bg=C["bg"])
        self.contacts = load_contacts()
        self._active_view = "all"   # "all" | "favourites" | "recent"
        self._build_ui()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._build_sidebar()
        self._build_main()

    # ── sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = tk.Frame(self, bg=C["sidebar"], width=210)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        pad = tk.Frame(sb, bg=C["sidebar"])
        pad.pack(fill="both", expand=True, padx=16, pady=20)

        tk.Label(pad, text="Contacts", font=("Segoe UI",13,"bold"),
                 bg=C["sidebar"], fg=C["text"]).pack(anchor="w")
        tk.Label(pad, text="Manage your network", font=FONTSM,
                 bg=C["sidebar"], fg=C["muted"]).pack(anchor="w", pady=(0,20))
        tk.Frame(pad, bg=C["border"], height=1).pack(fill="x", pady=(0,10))

        self._nav_btns = {}
        nav_items = [
            ("all",        "All contacts",  self._view_all),
            ("favourites", "Favourites",    self._view_favourites),
            ("recent",     "Added this week", self._view_recent),
        ]
        for key, label, cmd in nav_items:
            btn = tk.Button(pad, text=label, font=FONT, anchor="w",
                            bg=C["sidebar"], fg=C["subtext"],
                            activebackground=C["bg"],
                            relief="flat", bd=0, padx=10, pady=8,
                            command=cmd)
            btn.pack(fill="x", pady=1)
            self._nav_btns[key] = btn

        tk.Frame(pad, bg=C["border"], height=1).pack(fill="x", pady=10)

        tk.Button(pad, text="+ Add contact", font=FONT, anchor="w",
                  bg=C["sidebar"], fg=C["subtext"],
                  activebackground=C["bg"],
                  relief="flat", bd=0, padx=10, pady=8,
                  command=self.open_add).pack(fill="x", pady=1)

        tk.Frame(pad, bg=C["border"], height=1).pack(fill="x", pady=10)

        # live stat labels
        self.stat_total_var = tk.StringVar()
        self.stat_week_var  = tk.StringVar()
        self.stat_fav_var   = tk.StringVar()
        for var in [self.stat_total_var, self.stat_week_var, self.stat_fav_var]:
            tk.Label(pad, textvariable=var, font=FONTSM,
                     bg=C["sidebar"], fg=C["muted"],
                     justify="left").pack(anchor="w", pady=1)

        self._update_stats()
        self._set_active_nav("all")

    def _set_active_nav(self, key):
        self._active_view = key
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.configure(bg=C["bg"], fg=C["text"],
                              font=("Segoe UI", 10, "bold"))
            else:
                btn.configure(bg=C["sidebar"], fg=C["subtext"],
                              font=FONT)

    def _update_stats(self):
        total = len(self.contacts)
        week  = added_this_week(self.contacts)
        favs  = sum(1 for v in self.contacts.values() if v.get("favourite"))
        self.stat_total_var.set(f"Total contacts: {total}")
        self.stat_week_var.set(f"Added this week: {week}")
        self.stat_fav_var.set(f"Favourites: {favs}")

    # ── main panel ────────────────────────────────────────────────────────────
    def _build_main(self):
        main = tk.Frame(self, bg=C["bg"])
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(3, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # stat cards row
        stat_row = tk.Frame(main, bg=C["bg"])
        stat_row.grid(row=0, column=0, sticky="ew", padx=24, pady=(20,0))
        stat_row.columnconfigure((0,1,2), weight=1)

        self._stat_cards = {}
        stats = [
            ("total",     "Total contacts",   "0"),
            ("week",      "Added this week",  "0"),
            ("favourites","Favourites",        "0"),
        ]
        for col, (key, label, val) in enumerate(stats):
            card = tk.Frame(stat_row, bg=C["card"],
                            highlightthickness=1,
                            highlightbackground=C["border"])
            card.grid(row=0, column=col, sticky="ew",
                      padx=(0 if col==0 else 8, 0), ipady=10)
            num_var = tk.StringVar(value=val)
            tk.Label(card, textvariable=num_var, font=("Segoe UI",20,"bold"),
                     bg=C["card"], fg=C["text"]).pack(pady=(10,2))
            tk.Label(card, text=label, font=FONTSM,
                     bg=C["card"], fg=C["muted"]).pack(pady=(0,10))
            self._stat_cards[key] = num_var

        # top bar
        top = tk.Frame(main, bg=C["bg"])
        top.grid(row=1, column=0, sticky="ew", padx=24, pady=(16,0))
        top.columnconfigure(0, weight=1)

        self.view_title_var = tk.StringVar(value="All contacts")
        tk.Label(top, textvariable=self.view_title_var, font=FONTH,
                 bg=C["bg"], fg=C["text"]).grid(row=0, column=0, sticky="w")

        tk.Button(top, text="+ Add contact", font=FONT,
                  bg=C["accent"], fg="white",
                  activebackground="#333", relief="flat", bd=0,
                  padx=14, pady=7,
                  command=self.open_add).grid(row=0, column=1, sticky="e")

        # search
        sf = tk.Frame(main, bg=C["bg"])
        sf.grid(row=2, column=0, sticky="ew", padx=24, pady=12)
        sf.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_list())
        self.search_entry = tk.Entry(
            sf, textvariable=self.search_var, font=FONTMD,
            bg=C["card"], fg=C["text"], insertbackground=C["text"],
            relief="flat", bd=1, highlightthickness=1,
            highlightbackground=C["border"], highlightcolor=C["accent"])
        self.search_entry.grid(row=0, column=0, ipady=7, sticky="ew")

        # scrollable list
        wrapper = tk.Frame(main, bg=C["bg"])
        wrapper.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0,20))
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(wrapper, bg=C["bg"], highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew")

        vsb = tk.Scrollbar(wrapper, orient="vertical",
                           command=self._canvas.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self._canvas.configure(yscrollcommand=vsb.set)

        self.list_frame = tk.Frame(self._canvas, bg=C["bg"])
        self._list_win  = self._canvas.create_window(
            (0,0), window=self.list_frame, anchor="nw")

        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._list_win, width=e.width))
        self.list_frame.bind("<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(
                int(-1*(e.delta/120)), "units"))

        self.refresh_list()

    # ── views ─────────────────────────────────────────────────────────────────
    def _view_all(self):
        self._set_active_nav("all")
        self.view_title_var.set("All contacts")
        self.search_var.set("")
        self.refresh_list()

    def _view_favourites(self):
        self._set_active_nav("favourites")
        self.view_title_var.set("Favourites")
        self.search_var.set("")
        self.refresh_list()

    def _view_recent(self):
        self._set_active_nav("recent")
        self.view_title_var.set("Added this week")
        self.search_var.set("")
        self.refresh_list()

    # ── list rendering ────────────────────────────────────────────────────────
    def _filtered_contacts(self):
        q = self.search_var.get().lower()
        result = {}
        cutoff = datetime.today() - timedelta(days=7)

        for name, data in self.contacts.items():
            number = data.get("number","")
            fav    = data.get("favourite", False)
            added  = data.get("added","2000-01-01")

            # view filter
            if self._active_view == "favourites" and not fav:
                continue
            if self._active_view == "recent":
                try:
                    if datetime.strptime(added, "%Y-%m-%d") < cutoff:
                        continue
                except Exception:
                    continue

            # search filter
            if q and q not in name.lower() and q not in number.lower():
                continue

            result[name] = data
        return result

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        items = self._filtered_contacts()

        if not items:
            tk.Label(self.list_frame,
                     text="No contacts found.",
                     font=FONTMD, bg=C["bg"], fg=C["muted"]).pack(pady=40)
        else:
            for name, data in sorted(items.items()):
                self._contact_card(name, data)

        self._update_stats()
        self._update_stat_cards()

    def _update_stat_cards(self):
        total = len(self.contacts)
        week  = added_this_week(self.contacts)
        favs  = sum(1 for v in self.contacts.values() if v.get("favourite"))
        self._stat_cards["total"].set(str(total))
        self._stat_cards["week"].set(str(week))
        self._stat_cards["favourites"].set(str(favs))
        # sidebar
        self.stat_total_var.set(f"Total contacts: {total}")
        self.stat_week_var.set(f"Added this week: {week}")
        self.stat_fav_var.set(f"Favourites: {favs}")

    def _contact_card(self, name, data):
        number = data.get("number","")
        is_fav = data.get("favourite", False)

        row = tk.Frame(self.list_frame, bg=C["card"],
                       highlightthickness=1,
                       highlightbackground=C["border"])
        row.pack(fill="x", pady=3)
        row.columnconfigure(1, weight=1)

        # avatar
        bg_col, fg_col = avatar_colors(name)
        tk.Label(row, text=initials(name),
                 font=("Segoe UI",11,"bold"),
                 bg=bg_col, fg=fg_col,
                 width=3, height=1).grid(
            row=0, column=0, rowspan=2,
            padx=(14,12), pady=12, sticky="ns")

        tk.Label(row, text=name,
                 font=("Segoe UI",11,"bold"),
                 bg=C["card"], fg=C["text"]).grid(
            row=0, column=1, sticky="sw", pady=(10,0))

        tk.Label(row, text=number,
                 font=FONTSM, bg=C["card"], fg=C["subtext"]).grid(
            row=1, column=1, sticky="nw", pady=(0,10))

        # action buttons
        acts = tk.Frame(row, bg=C["card"])
        acts.grid(row=0, column=2, rowspan=2, padx=14, sticky="e")

        # star / favourite toggle
        star_var = tk.StringVar(value="★" if is_fav else "☆")
        star_color = C["star_on"] if is_fav else C["star_off"]
        star_btn = tk.Button(acts, textvariable=star_var,
                             font=("Segoe UI",14),
                             fg=star_color, bg=C["card"],
                             activebackground=C["card"],
                             relief="flat", bd=0, padx=4)
        star_btn.configure(
            command=lambda n=name, sb=star_btn, sv=star_var:
                self._toggle_favourite(n, sb, sv))
        star_btn.pack(side="left", padx=(0,8))

        tk.Button(acts, text="Edit", font=FONTSM,
                  bg=C["bg"], fg=C["subtext"],
                  activebackground=C["border"],
                  relief="flat", bd=1, padx=10, pady=4,
                  command=lambda n=name, num=number:
                      self.open_edit(n, num)).pack(side="left", padx=(0,6))

        tk.Button(acts, text="Delete", font=FONTSM,
                  bg="#FEF2F2", fg=C["danger"],
                  activebackground="#fee2e2",
                  relief="flat", bd=1, padx=10, pady=4,
                  command=lambda n=name:
                      self.delete_contact(n)).pack(side="left")

    # ── actions ───────────────────────────────────────────────────────────────
    def _toggle_favourite(self, name, btn, var):
        self.contacts[name]["favourite"] = \
            not self.contacts[name].get("favourite", False)
        is_fav = self.contacts[name]["favourite"]
        var.set("★" if is_fav else "☆")
        btn.configure(fg=C["star_on"] if is_fav else C["star_off"])
        save_contacts(self.contacts)
        self._update_stat_cards()

    def open_add(self):
        def save(name, number):
            if name in self.contacts:
                messagebox.showerror("Duplicate",
                                     f'"{name}" already exists.')
                return
            self.contacts[name] = {
                "number":    number,
                "favourite": False,
                "added":     today_str(),
            }
            save_contacts(self.contacts)
            self.refresh_list()
        ContactDialog(self, "Add contact", on_save=save)

    def open_edit(self, old_name, old_number):
        def save(name, number):
            if name != old_name and name in self.contacts:
                messagebox.showerror("Duplicate",
                                     f'"{name}" already exists.')
                return
            old_data = self.contacts.pop(old_name, {})
            old_data["number"] = number
            self.contacts[name] = old_data
            save_contacts(self.contacts)
            self.refresh_list()
        ContactDialog(self, "Edit contact",
                      name=old_name, number=old_number, on_save=save)

    def delete_contact(self, name):
        if messagebox.askyesno(
                "Delete contact",
                f'Delete "{name}"? This cannot be undone.'):
            del self.contacts[name]
            save_contacts(self.contacts)
            self.refresh_list()


if __name__ == "__main__":
    App().mainloop()
