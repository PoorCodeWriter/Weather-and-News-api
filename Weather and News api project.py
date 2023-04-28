import tkinter as tk
import webbrowser
from tkinter import ttk
import requests
import time
import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2Tk
import io
from PIL import ImageTk, Image

OPENWEATHER_API_KEY = "API-KEY"
NEWS_API_KEY = "API-KEY"


def get_weather_data(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + OPENWEATHER_API_KEY + "&q=" + city + "&units=metric"
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404" and "main" in data and "weather" in data:
        weather_data = {
            "city": data.get("name"),
            "temperature": data["main"].get("temp"),
            "description": data["weather"][0].get("description"),
            "icon": data["weather"][0].get("icon")
        }
        return weather_data
    else:
        return None


def get_news_data(query):
    base_url = "https://newsapi.org/v2/everything?"
    complete_url = base_url + "apikey=" + NEWS_API_KEY + "&q=" + query
    response = requests.get(complete_url)
    data = response.json()

    if data["status"] == "ok":
        return data["articles"]
    else:
        return None


def draw_graph(canvas):
    fig, ax = plt.subplots(figsize=(4, 2))

    # Historical LINE
    x1 = [17, 18, 19, 20, 21]
    y1 = [3.4, 4.2, 3.4, 6.8, 11]
    ax.plot(x1, y1, color='green', linestyle='dashed', linewidth=3, marker='o', markerfacecolor='blue', markersize=12)

    # Predicted LINE
    x2 = [17, 18, 19, 20, 21]
    y2 = [9, 7, 12, 10, 17]
    ax.plot(x2, y2, color='red', linestyle='dashed', linewidth=3, marker='o', markerfacecolor='purple', markersize=12)

    ax.set_xticks(np.arange(min(x1), max(x1) + 1, 1.0))
    ax.set_ylim(0, 21)
    ax.set_xlim(17, 21)
    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature C')
    ax.set_title('Temp graph for the week')

    graph_canvas = FigureCanvasTkAgg(fig, master=canvas)
    graph_canvas.draw()
    canvas.create_window(230, 320, window=graph_canvas.get_tk_widget())


def get_weather_icon(icon_code):
    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    response = requests.get(icon_url)
    icon_img = Image.open(io.BytesIO(response.content))
    return ImageTk.PhotoImage(icon_img)


def display_weather_and_news():
    city = city_entry.get()
    weather_data = get_weather_data(city)
    time.sleep(1)  # Add a brief delay between API calls
    news_data = get_news_data(city)

    if weather_data:
        weather_icon.config(image=get_weather_icon(weather_data["icon"]))
        weather_label.config(
            text=f"{weather_data['city']}\n"
                 f"{weather_data['temperature']}°C\n"
                 f"{weather_data['description']}",
            font=("Deja Vu", 16)
        )

        # Remove the previous image if it exists
        if hasattr(canvas, 'image_on_canvas'):
            canvas.delete(canvas.image_on_canvas)

        # Check if the weather description contains the word "clear sky"
        weather_images = {
            "clear sky": "https://clipartix.com/wp-content/uploads/2016/04/Sunshine-sun-clip-art-with-transparent"
                         "-background-free.png",
            "moderate rain": "https://creazilla-store.fra1.digitaloceanspaces.com/emojis/49832/cloud-with-rain-emoji"
                             "-clipart-md.png",
            "overcast clouds": "https://static-00.iconduck.com/assets.00/face-in-clouds-emoji-512x504-sxu35vrs.png",
            "few clouds": "https://em-content.zobj.net/source/skype/289/cloud_2601-fe0f.png",
            "broken clouds": "https://images.emojiterra.com/openmoji/v14.0/512px/1f636-1f32b.png",
            "drizzle": "https://images.emojiterra.com/openmoji/v14.0/512px/1f636-1f32b.png",
            "thunderstorm": "https://cdn-icons-png.flaticon.com/512/2204/2204341.png",
            "snow": "https://images.emojiterra.com/google/android-12l/512px/2603.png",
            "mist": "https://em-content.zobj.net/source/microsoft-teams/337/face-in-clouds_1f636-200d-1f32b-fe0f.png",
            "light rain": "https://cdn-icons-png.flaticon.com/512/2570/2570494.png",
            "scattered clouds": "https://media1.giphy.com/media/Ze42eWJPXzWo0KHPhT/giphy.gif?cid"
                                "=6c09b952gkli7zkgwei5ikveph38fkbn38qc97yyu4k5rq23&rid=giphy.gif&ct=s"
        }

        weather_description = weather_data["description"].lower()

        for key, value in weather_images.items():
            if key in weather_description:
                display_image_from_url(value, canvas)
                break

    else:
        weather_icon.config(image="")
        weather_label.config(text="City not found", font=("Arial", 16))

    if news_data:
        news_listbox.delete(0, tk.END)
        for article in news_data[:20]:
            news_listbox.insert(tk.END, f"{article['title']} ({article['source']['name']})")
    else:
        news_listbox.delete(0, tk.END)
        news_listbox.insert(tk.END, "No news found for the specified city")


def open_ad_url(event, link):
    webbrowser.open(link)


def display_ad(parent, ad_image_url, link, max_size=(350, 500)):
    response = requests.get(ad_image_url)
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))

    # Resize the image
    image.thumbnail(max_size, Image.LANCZOS)

    photo = ImageTk.PhotoImage(image)

    ad_label = tk.Label(parent, image=photo)
    ad_label.image = photo
    ad_label.bind("<Button-1>", lambda event: open_ad_url(event, link))

    parent.create_window(400, 520, window=ad_label)
    return ad_label


def update_ad(parent, ad_label=None):
    ad_image_urls_links = {
        "https://www.edsby.com/wp-content/uploads/2018/04/Screen-Shot-2018-04-25-at-9.52.02-AM.png": "https://glchs"
                                                                                                     ".edsby.com/p"
                                                                                                     "/BasePublic/",
        "https://www.ctvnews.ca/polopoly_fs/1.4138115.1539796391!/httpImage/image.jpg_gen/derivatives/landscape_1020"
        "/image.jpg": "https://ocs.ca/",
        "https://www.pikpng.com/pngl/b/301-3015537_memezasf-pornhub-supremelogo-supreme-pornhub-supreme-clipart.png":
            "https://us.supreme.com/",
        "https://www.wboy.com/wp-content/uploads/sites/43/2020/04/soos.jpg?w=1300&h=732&crop=1"
        ".jpg": "https://www.urbandictionary.com/define.php?term=kys"
        # Add more ad image URLs and their links here
    }

    if ad_label:
        ad_label.destroy()  # Remove the old ad label

    ad_image_url, link = random.choice(list(ad_image_urls_links.items()))  # Select a random ad image URL and its link
    new_ad_label = display_ad(parent, ad_image_url, link)

    #parent.after(5000, update_ad, parent, new_ad_label)


def display_image_from_url(image_url, parent, position=(400, 150)):
    response = requests.get(image_url)
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))

    # Resize the image
    max_size = (150, 150)  # Change these values to your desired size
    image.thumbnail(max_size, Image.LANCZOS)

    photo = ImageTk.PhotoImage(image)

    # Create a label to display the image and add it to your application
    image_label = ttk.Label(parent, image=photo)
    image_label.image = photo  # Keep a reference to the image to prevent garbage collection

    if hasattr(parent, 'image_on_canvas'):
        parent.delete(parent.image_on_canvas)

    parent.image_on_canvas = parent.create_image(position[0], position[1], image=photo, anchor='center')


def set_background(parent, background_image_url):
    background_response = requests.get(background_image_url)
    background_image_data = background_response.content
    background_image = Image.open(io.BytesIO(background_image_data))
    background_photo = ImageTk.PhotoImage(background_image)

    canvas = tk.Canvas(parent, width=800, height=600)
    canvas.pack(expand=True, fill="both")
    canvas.create_image(0, 0, image=background_photo, anchor='nw')
    canvas.image = background_photo  # Keep a reference to the image to prevent garbage collection

    return canvas


# coordinate of those show up
app = tk.Tk()
app.title("Weather and News App")
app.geometry("800x600")


background_image_url = "https://cdn.wallpapersafari.com/5/94/unQymT.jpg"
canvas = set_background(app, background_image_url)
city_label = ttk.Label(canvas, text="Enter city:", font=("Deja Vu", 13))
canvas.create_window(100, 50, window=city_label)

city_entry = ttk.Entry(canvas, font=("Deja Vu", 12))
canvas.create_window(200, 50, window=city_entry)

submit_button = ttk.Button(canvas, text="Get Weather and News", command=display_weather_and_news)
canvas.create_window(400, 50, window=submit_button)

weather_icon = ttk.Label(canvas)
canvas.create_window(100, 150, window=weather_icon)

weather_label = ttk.Label(canvas, font=("Deja Vu", 16))
canvas.create_window(200, 150, window=weather_label)

news_listbox = tk.Listbox(canvas, font=("Calibri", 12), width=35, height=20)
canvas.create_window(630, 230, window=news_listbox)
draw_graph(canvas)
update_ad(canvas)
app.mainloop()

