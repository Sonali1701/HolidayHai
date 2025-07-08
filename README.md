# HolidayHai - Long Weekend Finder 🌴

A FastAPI-based web application that helps you find long weekends and public holidays for different countries. Plan your vacations and make the most of your time off!

## Features ✨

- Find all long weekends for a given country and year
- Get information about the next long weekend in your country
- View public holidays for any supported country
- Simple and intuitive web interface
- RESTful API for programmatic access

## Installation 🛠️

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/HolidayHai.git
   cd HolidayHai
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On macOS/Linux
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage 🚀

### Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

Then open your browser and visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### API Endpoints

- `GET /` - Homepage with web interface
- `GET /api/long-weekends/{country_code}/{year}` - Get all long weekends for a country and year
- `GET /api/next-long-weekend/{country_code}` - Get the next long weekend for a country

### Example Requests

Get all long weekends for India in 2024:
```
GET /api/long-weekends/IN/2024
```

Get the next long weekend in the United States:
```
GET /api/next-long-weekend/US
```

## Built With 🛠

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Python-dateutil](https://dateutil.readthedocs.io/) - Date/time utilities
- [Jinja2](https://palletsprojects.com/p/jinja/) - Templating engine
- [HTTpx](https://www.python-httpx.org/) - HTTP client

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Public holiday data provided by [Nager.Date](https://date.nager.at/)
- Inspired by the need for better vacation planning tools
