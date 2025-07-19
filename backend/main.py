from gradio_client import Client, file

def main():
    client = Client("yisol/IDM-VTON")
    result = client.predict(
            file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),  # background image
            file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),  # garment image
            "Hello!!",  # garment description
            True,  # is_checked
            False,  # is_checked_crop
            30,  # denoise_steps
            42,  # seed
            api_name="/tryon"
    )
    print(result)


if __name__ == "__main__":
    main()
