# GetB@ck2Work!

A desktop productivity gamification app that rewards time spent on productive applications with points that can be exchanged for entertainment app access time.

## Features

- Real-time window monitoring
- Point system with streak bonuses
- App categorization (productive vs. entertainment)
- Daily statistics tracking
- Modern GUI interface
- Configurable settings

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GetBack2Work.git
cd GetBack2Work
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. The app will start monitoring your active windows and award points for productive applications.

3. Points can be spent on entertainment applications:
- Productive apps earn points
- Entertainment apps cost points
- Streak bonuses multiply point earnings

## Configuration

The app uses several JSON configuration files in the `data` directory:

- `config.json`: General settings and point values
- `apps_database.json`: App categorization rules
- `user_data.json`: User statistics and point history

## Development

The project structure:
```
GetBack2Work/
├── main.py                 # Entry point and main loop
├── window_monitor.py       # Active window detection
├── point_system.py         # Points logic and calculations
├── app_controller.py       # App blocking and control
├── gui/                    # GUI components
├── data/                   # Configuration and user data
└── utils/                  # Utility functions
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 