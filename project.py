import os
import sys
import spotipy
import spotipy.util as util
import requests
from fpdf import FPDF
from tempfile import gettempdir
from dotenv import load_dotenv

# From Spotify Webdeveloper website to access their API 

load_dotenv()
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = "http://localhost:5000/callback"
scope = "user-top-read"

def token_check():
    if client_id is None:
        print("You need to set your Spotify API credentials to get your CLIENT ID and SECRET ID. \n"
            "Get your credentials at: https://developer.spotify.com/dashboard \n"
            "When it's done, create a .env file and fill the information as follows: \n"
            "CLIENT_ID='Your Client ID' \n"
            "CLIENT_SECRET='Your Client Secret'")
        sys.exit()


class PDF(FPDF):
    def __init__(self, title_duration):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=10)
        self.add_page()
        self.image("background_02.jpg", x=0, y=0, w=self.w, h=self.h) # Import the Background Image from folder
        self.add_title(title_duration)
        
    def add_title(self, title_duration):
        self.set_font("helvetica", "B", 30)
        self.set_text_color(255, 255, 255)
        self.cell(0, 20, "Top 10 Spotify", border=0, ln=1, align="C")
        self.cell(0, 10, "of", border=0, ln=1, align="C")
        self.cell(0, 20, f"the {title_duration} for You", border=0, ln=1, align="C")

    def add_cover(self, index, image_url):
        try:
            img_path = os.path.join(gettempdir(), f"temp_image_{index}.jpg") # Create a path for the temporary folder
            with open(img_path, 'wb') as tmp_file: # Open the img with binary mode not text mode
                tmp_file.write(requests.get(image_url).content) # Download and add the image 

            x_offset = 10 if index % 2 == 0 else 110 # Set the position in X 
            y_offset = 65 + (23 * index) if index % 2 == 0 else 65 + (23 * (index-1)) # set the position in Y 
            self.set_xy(x_offset, y_offset) # it need to be applied together and not separeted 

            border_thickness = 1  # Adjust thickness as needed
            self.set_line_width(border_thickness * 2)
            self.set_draw_color(255, 255, 255)
            self.rect(self.get_x() - border_thickness, self.get_y() - border_thickness,
                    30 + 2 * border_thickness, 30 + 2 * border_thickness) # Draw rectangle for the border
            self.image(img_path, w=30) # Add the actual image
        

        except Exception as e:
            print(f"Error adding image: {e}")

    def add_track(self, index, track_name, artist_name):
        x_offset = 45 if index % 2 == 0 else 145 # Set the position in X 
        y_offset = 73 + (23 * index) if index % 2 == 0 else 73 + (23 * (index-1))# Set the position in Y
        self.set_xy(x_offset, y_offset)
        self.set_font_size(12)
        self.set_font("helvetica", "B")
        self.set_text_color(255, 255, 255)
        self.multi_cell(60, 7, f"{index + 1}. {track_name.title()}", align="L") # If the title is too long, \n

        x_offsett_artist = 50 if index % 2 == 0 else 150
        self.set_x(x_offsett_artist)
        self.set_font("helvetica", "I", 12)
        self.multi_cell(40, 7, f"by {artist_name}", align="L") # If the title is too long, \n
        

    def save_pdf(self):
        self.output("Your_top10_spotify.pdf")


def main():
    token_check()
    user_token = "Token"
    user_input = input("Time range(long/mid/short): ")
    duration = {"long": "long_term",
                "mid": "medium_term",
                "short": "short_term"
                }.get(user_input, "long_term")
    title_duration = {"long": "Year",
                      "mid": "Last 6 Months",
                      "short": "Month"
                      }.get(user_input, "Year")
    tracks, image_urls = get_top(user_token, duration)#Transfer the token to the def
    if tracks:
        pdf = PDF(title_duration)   # Transfer the token into the Class
        # unpack the two list Tracks and Image Urls into one giving them an index 
        for index, (track_name, artist_name), image_url in zip(range(len(tracks)), tracks, image_urls):
            pdf.add_cover(index,image_url)
            pdf.add_track(index, track_name, artist_name) 
        
        pdf.save_pdf()

        remove_token_cache(user_token)


def get_top(user_token, duration):
    token = util.prompt_for_user_token(user_token, scope,
                                        client_id=client_id,
                                        client_secret=client_secret,
                                        redirect_uri=redirect_uri) #use the API and client Token
    
    if token: # Get the API information
        sp = spotipy.Spotify(auth=token) 
        results = sp.current_user_top_tracks(limit=10, time_range=duration) #Set the number of song and since when
        tracks = [(item['name'], item['artists'][0]['name']) for item in results['items']]
        image_urls = [item['album']['images'][0]['url'] for item in results['items']]
        return tracks, image_urls
    else:
        print("Can't get token for")
        return None, None


def remove_token_cache(user_token): #Remove the Tokken so the user is asked again
    cache_file = f".cache-{user_token}"
    if os.path.exists(cache_file):
        os.remove(cache_file)
    
    print("You can revoke access to this application anytime by visiting: https://www.spotify.com/account/apps/")


if __name__ == "__main__":
    main()
