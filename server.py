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
    description='Generate an image based on a prompt. \n'+
                'prompt: The prompt to generate the image. EN is recommended for prompt.\n'+
                'num_images: [Optional] The number of images to generate, from 1 to 4 (inclusive). The default is 1. \n'+
                'Use this tool when you need to generate images with '+
                '**quality**, **photorealism**, **artistic detail**, and **a specific style** based on a prompt.' +
                'A good prompt is descriptive and clear, and makes use of meaningful keywords and modifiers.'
)
def Imagen3_generate_image(
    prompt: str, 
    num_images: int = 1, 
    ctx: Context = None
) -> str:
    ret_log = ""
    try:
        response = gemini_client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images= num_images,
            )
        )
        ret_log = "Image generated successfully\n"
    except Exception as e:
        print(f"Error generating image: {e}")
        return f"Error generating image: {e}"
    # save the images to a file
    for i, generated_image in enumerate(response.generated_images):
        try:
            save_file_name = f'image_{i}.png'
            save_path = os.path.join(WORKDIR_OUT, save_file_name)
            image = Image.open(BytesIO(generated_image.image.image_bytes))
            image.save(save_path)
            ret_log += f"Image saved to `{save_file_name}`\n"
        except Exception as e:
            print(f"Error saving image {i}: {e}")
            ret_log += f"Error saving image {i}\n"
    return ret_log


@mcp.tool(
    description='Generate an image based on a prompt and images. \n'+
                'prompt: Prompts or instructions for generating an image. EN is recommended for prompt.\n'+
                'input_images: [Optional] A list of image file names to input. The default is None. \n'+
                'Use this tool when you need to generate **contextually relevant** images based on a prompt. \n'+
                'It can also be used to edit user input images. \n' +
                'A good prompt is descriptive and clear, and makes use of meaningful keywords and modifiers.'
)
def OpenAI_generate_image(
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
                input_imgs_raw.append(open(img_path, 'rb'))
            except Exception as e:
                print(f"Error open image: {e}")
    # generate image
    try:
        if input_imgs_raw:
            result = openai_client.images.edit(
                model='gpt-image-1',
                image=input_imgs_raw,
                prompt=prompt
            )
        else:
            result = openai_client.images.generate(
                model='gpt-image-1',
                prompt=prompt
            )
        ret_log = "Image generated successfully\n"
    except Exception as e:
        print(f"Error generating image: {e}")
        return f"Error generating image: {e}"
    # save image
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    save_path = os.path.join(WORKDIR_OUT, 'image.png')
    try:
        with open(save_path, 'wb') as f:
            f.write(image_bytes)
        ret_log += f"Image saved to `image.png`\n"
    except Exception as e:
        print(f"Error saving image: {e}")
        ret_log += f"Error saving image\n"
    return ret_log


if __name__ == "__main__":
    mcp.run()