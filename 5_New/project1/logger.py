import logging

# 1. Create a custom logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 2. Create a handler specifically for file writing
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)

# 3. Define the layout format for records
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 4. Bind the handler to your logger
logger.addHandler(file_handler)
