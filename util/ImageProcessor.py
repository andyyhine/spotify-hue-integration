from PIL import Image
import requests

class ImageProcessor:

    # this works, but should distinguish between colors that are too close yknow..instead of returning 3 identical shades of black
    # try returning more than 3 colors and picking interesting ones from the list <- how can you quantify interesting?
    # up to 1000 is still murky
    def getTopThreeColors(self, imageUrl):
        
        TEMP_ALBUM_FILE = 'albumArt.jpg'

        imageData = requests.get(imageUrl).content
        with open(TEMP_ALBUM_FILE, 'wb') as handler:
            handler.write(imageData)

        def getCount(color):
            return color[0]

        albumImage = Image.open(TEMP_ALBUM_FILE)
        colors = albumImage.getcolors(1024*1024)
        colors.sort(key=getCount, reverse=True)

        # taking every 10000th color.. then take top 3? gets you 1st, 10000th and 20000th
        #    this should scale by len of colors...some albums have sub 5000 others 170k+
        n = len(colors) / 10
        topColors = colors[0::int(round(n))]
        return topColors