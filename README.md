[README (1).md](https://github.com/user-attachments/files/26688600/README.1.md)
# 📒 Contacts App

> A lightweight contact management desktop application built with Python & Tkinter — no database, no internet, no bloat.

## Features

- **Add, edit & delete** contacts with a clean modal interface
- **Live search** — filters by name or phone number instantly
- **Favourites** — star contacts and filter to see only them
- **This week** — see contacts added in the last 7 days
- **Stat cards** — total contacts, added this week, favourites count
- **Color-coded avatars** — auto-generated initials with unique colors per contact
- **Persistent storage** — all data saved locally in `contacts.json`
- **No internet required** — fully offline


## 🚀 Quick Start

### Option 1 — Download (Recommended)

1. Go to the [**Releases page**](../../releases/latest)
2. Download `Contacts.exe`
3. Double-click and run — no installation needed

### Option 2 — Run from source

**Requirements:** Python 3.8 or higher

bash
# 1. Clone the repository
```git clone https://github.com/YOUR_USERNAME/contacts-app.git```
```cd contacts-app```

# 2. Run the app
```python main.py```


No external packages required — uses Python's built-in `tkinter` and `json` only.


## 📁 Project Structure
```
contacts-app/
├── main.py              # Main application code
├── contacts.json        # Local contact data (auto-created on first run)
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── .github/
    └── workflows/
        └── build.yml    # GitHub Actions auto-build workflow
```


## 🗂️ Data Format

Contacts are stored locally in `contacts.json` in this format:
```
json
{
  "Shubham Jondhale": {
    "number": "1010101010",
    "favourite": true,
    "added": "2026-04-13"
  },
  "Mandar Jondhale": {
    "number": "8767884629",
    "favourite": false,
    "added": "2026-04-14"
  }
}
```

The file is created automatically on first launch. You can back it up, move it, or edit it manually.

## 🛠️ Build from Source

To build your own .exe:

bash
# Install PyInstaller
```pip install pyinstaller```

# Build single executable
```pyinstaller --onefile --windowed --name "Contacts" main.py```

# Output will be at:
# dist/Contacts.exe



## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request


## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Mandar Maruti Jondhale**
- GitHub: [mandarjondhale](https://github.com/mandarjondhale)

<p align="center">Made with ❤️ using Python & Tkinter</p>
