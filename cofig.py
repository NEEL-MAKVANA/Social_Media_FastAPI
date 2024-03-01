from dotenv import load_dotenv
import os

load_dotenv()
secret_key = os.environ["SECRET_KEY"]
algorithm = os.environ["ALGORITHM"]
exp_time = os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]
