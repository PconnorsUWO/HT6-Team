from gradio_client import Client, file

def main():
    client = Client("yisol/IDM-VTON")
    
    # Let's first check the API info to understand the correct structure
    print("Available APIs:")
    print(client.view_api())
    
    # Use the correct API structure based on the API info
    result = client.predict(
            {"background": file('person.jpg'), "layers": [], "composite": None},  # dict parameter
            file('garment.jpg'),  # garm_img
            "Hello!!",  # garment_des
            True,  # is_checked
            False,  # is_checked_crop
            30,  # denoise_steps
            42,  # seed
            api_name="/tryon"
    )
    print(result)


if __name__ == "__main__":
    main()
