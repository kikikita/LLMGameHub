from pydantic import BaseModel

class Character(BaseModel):
    name: str
    age: str
    background: str
    personality: str

class GameSetting(BaseModel):
    character: Character
    setting: str
    genre: str
