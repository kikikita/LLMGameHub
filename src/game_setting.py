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


def get_user_story(
    scene_description: str, scene_image_description: str, user_choice: str
) -> str:
    return f"""Current scene description:
            {scene_description}
            Current scene image description: {scene_image_description}
            
            User's choice: {user_choice}
        """
