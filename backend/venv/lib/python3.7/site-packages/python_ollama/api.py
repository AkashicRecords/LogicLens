import requests
import json
from .parameters import Parameters

class OllamaAPI:
    """
    A Python client for interacting with the Ollama API.

    This class provides easy-to-use methods to manage models, generate text,
    create embeddings, and perform other actions available through the Ollama API.

    Example Usage:
        >>> ollama = OllamaAPI(url="http://your-ollama-server:port")
        >>> models = ollama.get_models()
        >>> print(models)  # Output: List of available models
        >>> response = ollama.generate(model="llama2", prompt="Hello, world!")
        >>> print(response)  # Output: Generated text from llama2
        >>> ollama.model.create(name="my_model", path="/path/to/my/model") # Create a new model
    """

    def __init__(self, url="http://localhost:11434"):
        """
        Initializes the OllamaAPI client.

        Args:
            url (str, optional): The base URL of the Ollama API server. 
                                Defaults to "http://localhost:11434".
        """
        super().__init__()
        self.url = url
        self.model = self.Model(self)  # Pass the OllamaAPI instance
        self.generate = self.Generate(self)  # Pass the OllamaAPI instance
        self.parameters = Parameters()

    # --- Model Management ---
    class Model:
        """
        Provides methods for managing Ollama models.
        """

        def __init__(self, api_instance):
            self.api_instance = api_instance

        def create(self, name, modelfile=None, path=None, stream=False, **kwargs):
            """
            Creates a new Ollama model.

            Args:
                name (str): The name for the new model.
                modelfile (str, optional): The content of the Modelfile.
                path (str, optional): The path to the Modelfile on the server. 
                stream (bool, optional): If false the response will be returned as a single response object, rather than a stream of objects.
                **kwargs: Additional parameters for model creation (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary. 
            """
            data = {"name": name, "modelfile": modelfile, "path": path, "stream": stream, **kwargs}
            return self.api_instance.post(endpoint="/api/create", json_data=data)

        def delete(self, name):
            """
            Deletes an Ollama model.

            Args:
                name (str): The name of the model to delete.

            Returns:
                dict: The API response as a JSON dictionary.
            """
            data = {"name": name}
            return self.api_instance.delete(endpoint="/api/delete", json_data=data)

        def pull(self, name, insecure=False, stream=False, **kwargs):
            """
            Downloads (pulls) an Ollama model.

            Args:
                name (str): The name of the model to pull.
                insecure (bool, optional): Allow insecure connections to the library. Only use this if you are pulling from your own library during development.
                stream (bool, optional): If false the response will be returned as a single response object, rather than a stream of objects.
                **kwargs: Additional parameters for pulling the model (see Ollama API documentation).

            Returns:
                generator: A generator that yields chunks of the downloaded model data.
            """
            data = {"name": name, "insecure": insecure, "stream": stream, **kwargs}
            return self.api_instance.post(f"/api/pull", data, stream=True)

        def push(self, name, insecure=False, stream=False, **kwargs):
            """
            Uploads (pushes) an Ollama model to a library.

            Args:
                name (str): The name of the model to push.
                insecure (bool, optional): Allow insecure connections to the library. Only use this if you are pushing to your library during development.
                stream (bool, optional): If false the response will be returned as a single response object, rather than a stream of objects.
                **kwargs: Additional parameters for pushing the model (see Ollama API documentation).

            Returns:
                generator: A generator that yields chunks of the response data.
            """
            data = {"name": name, "insecure": insecure, "stream": stream, **kwargs}
            return self.api_instance.post(f"/api/push", data, stream=True)

        def get(self, name):
            """
            Retrieves information about a specific Ollama model.

            Args:
                name (str): The name of the model.

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self.api_instance.get(f"/api/models/{name}")

        def show(self, name, verbose=False, **kwargs):
            """
            Shows detailed information about a model, including its Modelfile, template, 
            parameters, license, and system prompt.

            Args:
                name (str): The name of the model.
                verbose (bool, optional): If set to true, returns full data for verbose response fields.
                **kwargs: Additional parameters for showing model information (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary.
            """
            data = {"name": name, "verbose": verbose, **kwargs}
            return self.api_instance.post("/api/show", data)

        def copy(self, source, destination):
            """
            Creates a copy of an existing Ollama model.

            Args:
                source (str): The name of the model to copy.
                destination (str): The name for the new copied model.

            Returns:
                dict: The API response as a JSON dictionary.
            """
            data = {"source": source, "destination": destination}
            return self.api_instance.post("/api/copy", data)

        def running(self):
            """
            Lists all Ollama models currently loaded in memory.

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self.api_instance.get("/api/ps")

    # --- Text & Chat Completion ---
    class Generate:
        """
        Provides methods for text and chat completion using Ollama models.
        """

        def __init__(self, api_instance):
            self.api_instance = api_instance

        def response(self, model, prompt, suffix=None, images=None, format="text", options=None, system=None, template=None, context=None, stream=False, raw=False, keep_alive="5m", **kwargs):
            """
            Generates text from a prompt.

            Args:
                model (str): The name of the model to use.
                prompt (str): The prompt to generate text from.
                suffix (str, optional): The text after the model response.
                images (list, optional): A list of base64-encoded images (for multimodal models such as llava).
                format (str, optional): The format to return a response in. Currently the only accepted value is json.
                options (dict, optional): Additional model parameters listed in the documentation for the Modelfile such as temperature.
                system (str, optional): System message to (overrides what is defined in the Modelfile).
                template (str, optional): The prompt template to use (overrides what is defined in the Modelfile).
                context (list, optional): The context parameter returned from a previous request to /generate, this can be used to keep a short conversational memory.
                stream (bool, optional): If false the response will be returned as a single response object, rather than a stream of objects.
                raw (bool, optional): If true no formatting will be applied to the prompt. You may choose to use the raw parameter if you are specifying a full templated prompt in your request to the API.
                keep_alive (str, optional): Controls how long the model will stay loaded into memory following the request (default: 5m).
                **kwargs: Additional parameters for text generation (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary.
            """
            data = {
                "model": model,
                "prompt": prompt,
                "suffix": suffix,
                "images": images,
                "format": "json",
                "options": options,
                "system": system,
                "template": template,
                "context": context,
                "stream": stream,
                "raw": raw,
                "keep_alive": keep_alive,
                **kwargs
            }
            return self.api_instance.post("/api/generate", data)

        def embedding(self, model, input_data, truncate=True, options=None, keep_alive="5m", **kwargs):
            """
            Generates embeddings from a model.

            Args:
                model (str): The name of the model to use.
                input_data (str or list): The text to generate embeddings for. 
                                          Can be a string or a list of strings.
                truncate (bool, optional): Truncates the end of each input to fit within context length. Returns error if false and context length is exceeded. Defaults to true.
                options (dict, optional): Additional model parameters listed in the documentation for the Modelfile such as temperature.
                keep_alive (str, optional): Controls how long the model will stay loaded into memory following the request (default: 5m).
                **kwargs: Additional parameters for embedding generation (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary.
            """
            data = {
                "model": model,
                "input": input_data,
                "truncate": truncate,
                "options": options,
                "keep_alive": keep_alive,
                **kwargs
            }
            return self.api_instance.post("/api/embed", data)

        def chat(self, model, messages, tools=None, format="json", options=None, stream=True, keep_alive="5m", **kwargs):
            """
            Generates a chat response from a model.

            Args:
                model (str): The name of the model to use.
                messages (list): A list of message dictionaries representing the conversation history.
                                 Each dictionary should have the following keys:
                                 - role (str): The role of the sender ("system", "user", or "assistant").
                                 - content (str): The text content of the message.
                                 - images (list, optional): A list of images to include in the message (for multimodal models such as llava).
                                 - tool_calls (list, optional): A list of tools the model wants to use.
                tools (list, optional): Tools for the model to use if supported. Requires stream to be set to false.
                format (str, optional): The format to return a response in. Currently the only accepted value is json.
                options (dict, optional): Additional model parameters listed in the documentation for the Modelfile such as temperature.
                stream (bool, optional): If false the response will be returned as a single response object, rather than a stream of objects.
                keep_alive (str, optional): Controls how long the model will stay loaded into memory following the request (default: 5m).
                **kwargs: Additional parameters for chat generation (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary.
            """
            data = {
                "model": model,
                "messages": messages,
                "tools": tools,
                "format": format,
                "options": options,
                "stream": stream,
                "keep_alive": keep_alive,
                **kwargs
            }
            return self.api_instance.post("/api/chat", data)

    # --- Other Ollama API Methods ---
    def get_models(self):
        """
        Gets a list of available models on the Ollama server.

        Returns:
            dict: The API response as a JSON dictionary.
        """
        return self.get("/api/tags")

    def check_blob_exists(self, digest):
        """
        Checks if a file blob (used for FROM/ADAPTER fields in Modelfiles) 
        exists on the server. 

        Args:
            digest (str): The SHA256 digest of the blob.

        Returns:
            requests.Response: The HEAD response from the Ollama server. 
                               A 200 status code means the blob exists.
        """
        return self.head(f"/api/blobs/{digest}")

    def create_blob(self, digest, file_path):
        """
        Uploads a file as a blob to the Ollama server. This can be used
        to provide model files or adapter files when creating models. 

        Args:
            digest (str): The expected SHA256 digest of the file.
            file_path (str): The path to the file to be uploaded.

        Returns:
            str: The server's response (usually indicates the file path on the server).
        """
        with open(file_path, "rb") as f:
            file_data = f.read()
        response = requests.post(f"{self.url}/api/blobs/{digest}", data=file_data)
        response.raise_for_status() 
        return response.text

    # --- Helper Methods ---
    def get(self, endpoint):
        """
        Makes a GET request to the Ollama API.

        Args:
            endpoint (str): The API endpoint to make the request to.

        Returns:
            dict: The API response as a JSON dictionary.
        """
        url = f"{self.url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers)

        # Handle potential JSON errors gracefully
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            # If the response is not valid JSON, return the raw response text
            return response.text

    def post(self, endpoint, json_data=None, data=None, stream=False, format="text"):
        """
        Makes a POST request to the Ollama API.

        Args:
            endpoint (str): The API endpoint to make the request to.
            json_data (dict, optional): Data to send in the request body as JSON.
            data (dict, optional): Data to send in the request body as form data.
            stream (bool, optional): If true, the response will be returned as a stream of objects.
            format (str, optional): The format to return a response in (defaults to "text").

        Returns:
            str or generator: The text response extracted from the JSON data or a generator for streaming responses.
        """
        url = f"{self.url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if json_data:
            response = requests.post(url, headers=headers, json=json_data)
        elif data:
            response = requests.post(url, headers=headers, data=data)
        else:
            raise ValueError("Either json_data or data must be provided.")

        # Handle potential JSON errors gracefully
        try:
            if format == "text":
                response_data = response.json()
                # Extract the response from the JSON data
                return response_data.get('response', '') 
            elif format == "json":
                if stream:
                    return response.iter_content(chunk_size=None)
                else:
                    return response.text
            else:
                raise ValueError("Invalid format. Use 'text' or 'json'.")
        except json.decoder.JSONDecodeError:
            # If the response is not valid JSON, return the raw response text
            return response.text


    def delete(self, endpoint, json_data=None):
        """
        Makes a DELETE request to the Ollama API.

        Args:
            endpoint (str): The API endpoint to make the request to.
            json_data (dict, optional): Data to send in the request body.

        Returns:
            dict: The API response as a JSON dictionary.
        """
        url = f"{self.url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        response = requests.delete(url, headers=headers, json=json_data)

        # Handle potential JSON errors gracefully
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            # If the response is not valid JSON, return the raw response text
            return response.text

    def head(self, endpoint):
        """
        Makes a HEAD request to the Ollama API.

        Args:
            endpoint (str): The API endpoint to make the request to.

        Returns:
            requests.Response: The HEAD response from the Ollama server.
        """
        return requests.head(f"{self.url}{endpoint}")