import os

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CLASSES = {
    "Calc": "BC Calculus 20-21",
    "Gov": "Law & Gov",
    "Writing": "Professional and Technical Writing",
    "Physics": "Block5 (mod9) AP Physics C - DeLano",
}
TITLE_MATCH_THRESH = 80