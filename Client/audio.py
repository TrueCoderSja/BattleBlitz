import pygame.mixer

class SoundManager:
    # Static properties for sound file paths
    LOADING = "assets/loading.mp3"
    BACKGROUND = "assets/loading.mp3"
    HIT_AUDIO="assets/hit.mp3"
    EXPLOSION_AUDIO="assets/explosion.mp3"

    def __init__(self, sound_key):
        """
        Initializes a SoundManager instance for a specific sound.
        :param sound_key: The static property representing the sound file path.
        """
        self.sound_key = sound_key
        self.sound = None
        self.initialized = False

    def initialize(self):
        if not self.initialized:
            pygame.mixer.init()
            self.initialized = True

    def load_sound(self):
        """
        Loads the sound file associated with this instance.
        """
        self.initialize()
        if not self.sound:
            try:
                self.sound = pygame.mixer.Sound(self.sound_key)
            except Exception as e:
                print(f"Error loading sound '{self.sound_key}': {e}")
                self.sound = None

    def play(self, loops=-1):
        """
        Plays the sound managed by this instance.
        :param loops: Number of times to loop the sound. -1 for infinite loop.
        """
        if not self.sound:
            self.load_sound()
        if self.sound:
            self.sound.play(loops=loops)

    def playOnce(self):
        self.play(0)

    def stop(self):
        """
        Stops the sound managed by this instance.
        """
        if self.sound:
            self.sound.stop()
