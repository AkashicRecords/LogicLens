class Parameters:
    """
    Handles Ollama parameters.

    This class allows for easier management of Ollama parameters in requests.
    """

    def __init__(self):
        """
        Initializes the Parameters class.
        """
        self.num_keep = None
        self.seed = None
        self.num_predict = None
        self.top_k = None
        self.top_p = None
        self.min_p = None
        self.tfs_z = None
        self.typical_p = None
        self.repeat_last_n = None
        self.temperature = None
        self.repeat_penalty = None
        self.presence_penalty = None
        self.frequency_penalty = None
        self.mirostat = None
        self.mirostat_tau = None
        self.mirostat_eta = None
        self.penalize_newline = None
        self.stop = None
        self.numa = None
        self.num_ctx = None
        self.num_batch = None
        self.num_gpu = None
        self.main_gpu = None
        self.low_vram = None
        self.f16_kv = None
        self.vocab_only = None
        self.use_mmap = None
        self.use_mlock = None
        self.num_thread = None

    def set(self, **kwargs):
        """
        Sets multiple parameters.

        Args:
            **kwargs: Keyword arguments to set parameters.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """
        Converts parameters to a dictionary.

        Returns:
            dict: A dictionary containing all parameters and their values.
        """
        return {key: value for key, value in self.__dict__.items() if value is not None}