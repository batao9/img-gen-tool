from google import genai
from google.genai import types
from mcp.server.fastmcp import FastMCP, Context
from PIL import Image
from io import BytesIO
import dotenv
import os
dotenv.load_dotenv()

mcp = FastMCP("Image Generator")
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

@mcp.tool(
    description='Generate an image based on a prompt. \n'+
                'prompt: The prompt to generate the image. EN is recommended for prompts.\n'+
                'num_images: The number of images to generate, from 1 to 4 (inclusive). The default is 1. \n'+
                'Use this tool when you need to generate an image based on a prompt.' +
                'A good prompt is descriptive and clear, and makes use of meaningful keywords and modifiers.'
)
def generate_image(prompt: str, num_images: int = 1, ctx: Context = None) -> str:
    ret_log = ""
    try:
        response = client.models.generate_images(
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
            save_path = os.path.join(os.getenv('OUTPUT_DIR'), save_file_name)
            image = Image.open(BytesIO(generated_image.image.image_bytes))
            image.save(save_path)
            ret_log += f"Image saved to {save_file_name}\n"
        except Exception as e:
            print(f"Error saving image {i}: {e}")
    return ret_log

if __name__ == "__main__":
    mcp.run()