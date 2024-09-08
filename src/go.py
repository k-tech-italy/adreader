from PIL import ImageGrab

screenshot = ImageGrab.grab(bbox=[2634, 97, 2653, 121])  # Take the screenshot
screenshot.show()