# UI Tree — Current vs Target

## Current user UI

/start
└── language
    └── rules
        └── accept
            └── required channel
                └── main
                    ├── Functions
                    ├── Automation
                    ├── Library
                    ├── Support
                    ├── Settings
                    └── Help

Business commands are separate from the main menu and use a `.` prefix.

## Target UI from Master Prompt

/start
└── language
    └── rules
        └── accept
            └── mandatory channels
                └── Business onboarding/status
                    └── Main
                        ├── 🛠 Functions
                        │   ├── Messages
                        │   ├── Moderation
                        │   ├── Automation
                        │   ├── Profile
                        │   ├── Text
                        │   ├── Media
                        │   ├── Voice & Audio
                        │   ├── Files
                        │   ├── Generators
                        │   ├── Entertainment
                        │   ├── Telegram Tools
                        │   ├── Library
                        │   ├── Privacy
                        │   ├── Statistics
                        │   └── Utilities
                        ├── 📚 Library
                        ├── ⚡ Automation
                        ├── 👤 Profile
                        ├── 🔒 Privacy
                        ├── 🧰 Tools
                        ├── ⚙️ Settings
                        ├── ❓ Help
                        └── 🎫 Support

Every multi-step screen must have Back and Cancel where applicable.
