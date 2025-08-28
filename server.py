from google import genai
from google.genai import types
from openai import OpenAI
from mcp.server.fastmcp import FastMCP, Context
from PIL import Image
from io import BytesIO
import dotenv
import os
import argparse
import base64
from typing import Optional, List
dotenv.load_dotenv()

mcp = FastMCP("Image Generator")
gemini_client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
openai_client = OpenAI()

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--WORKDIR_IN')
parser.add_argument('--WORKDIR_OUT')
args, remaining_args = parser.parse_known_args()
workdir_in_cli = args.WORKDIR_IN
workdir_out_cli = args.WORKDIR_OUT

WORKDIR_IN = workdir_in_cli or os.getenv('WORKDIR_IN')
WORKDIR_OUT = workdir_out_cli or os.getenv('WORKDIR_OUT')

@mcp.tool(
    description='Generate an image based on a prompt and images. Image is saved to host `WORKDIR_OUT/image.png`.\n'+
                'prompt: Prompts or instructions for generating an image. EN is recommended for prompt.\n'+
                'input_images: [Optional] A list of image file names to input. The default is None. \n'+
                'Use this tool when you need to generate **contextually relevant** images based on a prompt. \n'+
                'It can also be used to edit user input images. \n' +
                'A good prompt is descriptive and clear, and makes use of meaningful keywords and modifiers.'
)
def Gemini_generate_image(
    prompt: str, 
    input_images: Optional[List[str]] = None,
    ctx: Context = None
) -> str:
    ret_log = ""
    # open img file
    input_imgs_raw = []
    if input_images:
        for img in input_images:
            img_path = os.path.join(WORKDIR_IN, img)
            try:
                input_imgs_raw.append(Image.open(img_path))
            except Exception as e:
                print(f"Error open image: {e}")
                return f"Error open image: {e}"
    # generate image
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash-image-preview',
            contents=[prompt, input_imgs_raw],
        )
        ret_log = "[System] Image generated successfully\n"
    except Exception as e:
        print(f"Error generating image: {e}")
        return f"Error generating image: {e}"
    # save image
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            ret_log += part.text
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))   
            image.save(os.path.join(WORKDIR_OUT, 'image.png'))
            ret_log += f"\n[System] Image saved to local file `image.png`. \n"
    
    return ret_log

if __name__ == "__main__":
    mcp.run()