import requests
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext

API_KEY = '0e0564ae5237f214668df85cbc8cfb93'  # Replace with your valid OpenWeatherMap API key
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
DB_NAME = 'weather_history.db'

# --- Database functions ---
def create_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            wind_speed REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(location, temperature, humidity, wind_speed):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO history (location, temperature, humidity, wind_speed) VALUES (?, ?, ?, ?)",
              (location, temperature, humidity, wind_speed))
    conn.commit()
    conn.close()

# --- Weather API functions ---
def get_weather(location):
    try:
        if ',' in location:
            lat, lon = location.split(',')
            params = {
                'lat': lat.strip(),
                'lon': lon.strip(),
                'appid': API_KEY,
                'units': 'metric'
            }
        else:
            params = {
                'q': location,
                'appid': API_KEY,
                'units': 'metric'
            }
        
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        if response.status_code == 401:
            messagebox.showerror("Unauthorized", "Invalid API key. Please check your API key.")
        elif response.status_code == 404:
            messagebox.showerror("City Not Found", f"The city '{location}' was not found. Please check the spelling or try using a country code.")
        else:
            messagebox.showerror("HTTP Error", f"HTTP error occurred: {err}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None

def format_weather_data(data):
    city = data['name']
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    return city, temperature, humidity, wind_speed

# --- GUI functions ---
def fetch_weather():
    location = entry.get().strip()
    if not location:
        messagebox.showwarning("Input Required", "Please enter a city name or coordinates.")
        return
    weather_data = get_weather(location)
    if weather_data:
        city, temperature, humidity, wind_speed = format_weather_data(weather_data)
        display_text = (f"Weather in {city}:\n"
                        f"Temperature: {temperature} °C\n"
                        f"Humidity: {humidity} %\n"
                        f"Wind Speed: {wind_speed} m/s")
        display_weather_info(display_text)
        save_to_db(city, temperature, humidity, wind_speed)
    else:
        messagebox.showerror("Error", "Could not retrieve weather data for the given location.")

def display_weather_info(info):
    weather_display.config(state=tk.NORMAL)  # Enable editing to insert text
    weather_display.delete(1.0, tk.END)  # Clear previous text
    weather_display.insert(tk.END, info)  # Insert new weather info
    weather_display.config(state=tk.DISABLED)  # Make it read-only

    # Show the weather display area
    weather_display.pack(pady=20)

def on_enter_key(event):
    fetch_weather()

def toggle_fullscreen(event):
    if root.attributes('-fullscreen'):
        root.attributes('-fullscreen', False)
        root.geometry("800x600")
    else:
        root.attributes('-fullscreen', True)

# --- Main app setup ---
if __name__ == "__main__":
    create_db()  # Ensure database and table exist

    root = tk.Tk()
    root.title("Weather App")
    root.geometry("800x600")  # Set a default window size
    root.configure(bg="#e0f7fa")  # Light cyan background color

    root.bind("<Escape>", toggle_fullscreen)

    title_label = tk.Label(root, text="Weather App", font=("Helvetica", 40, "bold"), bg="#e0f7fa", fg="#00796b")
    title_label.pack(pady=20)

    frame = tk.Frame(root, bg="#e0f7fa")
    frame.pack(pady=20)

    label = tk.Label(frame, text="Enter city name or coordinates (lat,lon):", font=("Arial", 20), bg="#e0f7fa", fg="#004d40")
    label.pack(pady=10)

    entry = tk.Entry(frame, font=("Arial", 20), width=30, bd=2, relief="groove")
    entry.pack(pady=10)
    entry.bind('<Return>', on_enter_key)

    button = tk.Button(frame, text="Get Weather", font=("Arial", 20), bg="#00796b", fg="white", command=fetch_weather)
    button.pack(pady=20)

    # Button hover effect
    def on_enter(e):
        button['bg'] = '#004d40'  # Darker shade on hover

    def on_leave(e):
        button['bg'] = '#00796b'  # Original color

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

    # Weather display area (initially hidden)
    weather_display = scrolledtext.ScrolledText(root, font=("Arial", 16), width=50, height=10, bd=2, relief="groove")
    weather_display.pack_forget()  # Hide it initially
    weather_display.config(state=tk.DISABLED)  # Make it read-only initially

    root.protocol("WM_DELETE_WINDOW", root.quit)  # Allow the window to be closed

    root.mainloop()
