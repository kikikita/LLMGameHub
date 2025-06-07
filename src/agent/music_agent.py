from pydantic import BaseModel
from agent.llm import create_light_llm
from langchain_core.messages import SystemMessage, HumanMessage
import logging

logger = logging.getLogger(__name__)

music_options = """Instruments: 303 Acid Bass, 808 Hip Hop Beat, Accordion, Alto Saxophone, Bagpipes, Balalaika Ensemble, Banjo, Bass Clarinet, Bongos, Boomy Bass, Bouzouki, Buchla Synths, Cello, Charango, Clavichord, Conga Drums, Didgeridoo, Dirty Synths, Djembe, Drumline, Dulcimer, Fiddle, Flamenco Guitar, Funk Drums, Glockenspiel, Guitar, Hang Drum, Harmonica, Harp, Harpsichord, Hurdy-gurdy, Kalimba, Koto, Lyre, Mandolin, Maracas, Marimba, Mbira, Mellotron, Metallic Twang, Moog Oscillations, Ocarina, Persian Tar, Pipa, Precision Bass, Ragtime Piano, Rhodes Piano, Shamisen, Shredding Guitar, Sitar, Slide Guitar, Smooth Pianos, Spacey Synths, Steel Drum, Synth Pads, Tabla, TR-909 Drum Machine, Trumpet, Tuba, Vibraphone, Viola Ensemble, Warm Acoustic Guitar, Woodwinds, ...
Music Genre: Acid Jazz, Afrobeat, Alternative Country, Baroque, Bengal Baul, Bhangra, Bluegrass, Blues Rock, Bossa Nova, Breakbeat, Celtic Folk, Chillout, Chiptune, Classic Rock, Contemporary R&B, Cumbia, Deep House, Disco Funk, Drum & Bass, Dubstep, EDM, Electro Swing, Funk Metal, G-funk, Garage Rock, Glitch Hop, Grime, Hyperpop, Indian Classical, Indie Electronic, Indie Folk, Indie Pop, Irish Folk, Jam Band, Jamaican Dub, Jazz Fusion, Latin Jazz, Lo-Fi Hip Hop, Marching Band, Merengue, New Jack Swing, Minimal Techno, Moombahton, Neo-Soul, Orchestral Score, Piano Ballad, Polka, Post-Punk, 60s Psychedelic Rock, Psytrance, R&B, Reggae, Reggaeton, Renaissance Music, Salsa, Shoegaze, Ska, Surf Rock, Synthpop, Techno, Trance, Trap Beat, Trip Hop, Vaporwave, Witch house, ...
Mood/Description: Acoustic Instruments, Ambient, Bright Tones, Chill, Crunchy Distortion, Danceable, Dreamy, Echo, Emotional, Ethereal Ambience, Experimental, Fat Beats, Funky, Glitchy Effects, Huge Drop, Live Performance, Lo-fi, Ominous Drone, Psychedelic, Rich Orchestration, Saturated Tones, Subdued Melody, Sustained Chords, Swirling Phasers, Tight Groove, Unsettling, Upbeat, Virtuoso, Weird Noises, ...
"""
system_prompt = f"""
You are a music agent responsible for generating appropriate music tones for scenes in a visual novel game.

Your task is to analyze the current scene description and generate a detailed music prompt that captures:
1. The emotional atmosphere
2. The intensity level
3. The genre/style that best fits the scene
4. Specific instruments that would enhance the mood

You have access to a wide range of musical elements including:
{music_options}

When generating a music prompt:
- Consider the scene's context, mood, and any suspense elements
- Choose instruments that complement the scene's atmosphere
- Select a genre that matches the story's setting and tone
- Include specific mood descriptors to guide the music generation

Your output should be a concise but detailed prompt that the music generation model can use to create an appropriate soundtrack for the scene.
"""


class MusicPrompt(BaseModel):
    prompt: str


llm = create_light_llm(0.1).with_structured_output(MusicPrompt)


async def generate_music_prompt(scene_description: str, request_id: str) -> str:
    logger.info(f"Generating music prompt for the current scene: {request_id}")
    response = await llm.ainvoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=scene_description)]
    )
    logger.info(f"Music prompt generated: {request_id}")
    return response.prompt
